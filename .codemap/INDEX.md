# Codemap — first-cup-processor

Navigation layer for `/diagnose`. **This map is orientation, not ground truth** — it points at files and
mechanisms; always verify against live source before acting. Pinned to the commit in `.mapped-sha`;
refresh with `/codemap-update`.

Repo shape: a flat single-package Python project (~4,700 lines, 8 modules). It watches a directory for
YouTube transcripts, runs a 4-step Claude pipeline to generate titles/descriptions/newsletter/blog copy,
takes a human title selection over Slack, and can publish the result to WordPress on a Slack trigger.
Runs continuously as a macOS Launch Agent.

## Hubs

### Core pipeline
- **[processor](processor.md)** — The main module (`youtube_processor.py`): the watch loop, the 4-step
  Claude pipeline, prompt builders, regex parsers, output writing, and the API error taxonomy. Also covers
  `model_registry.py` — the single funnel for model resolution + deprecation recovery.
  The heart of the system; start here for anything about content generation.
- **[slack](slack.md)** — Human-in-the-loop layer (`slack_helper.py`): threaded conversations, interactive
  title selection, credits-exhaustion pause/resume. Optional (gated by `slack.enabled`), but when on it
  **blocks the pipeline** waiting for a human.

### Publishing
- **[publish-triggers](publish-triggers.md)** — The two ways a publish gets fired: `publish_poller.py`
  (background daemon polling Slack for a 📤 reaction or "publish" reply) and `publish_webhook.py`
  (alternative HTTP server). Owns the `.publish_poller_state.json` IPC file.
- **[publishing](publishing.md)** — `blog_publisher.py`: WordPress REST post creation (as draft),
  YouTube video/thumbnail lookup, featured-image upload. Depends on a **cross-repo import** from the
  sibling `weekly-brew` project.

### Supporting
- **[deployment](deployment.md)** — Config/secrets split, `run_processor.sh`, and the launchd agents.
  Home of the two nastiest footguns in the repo (`.env` shell-quoting; installed-vs-committed plist drift).
- **[thumbnails](thumbnails.md)** — `thumbnail_generator.py`: Claude-brainstorms-concept →
  Gemini-generates-image. **Work in progress, uncommitted, and NOT wired into the pipeline.**

## Adjacency

Which subsystems interact — use this for `/diagnose`'s completeness sweep, since a symptom in one
of these usually has its cause in a neighbour.

- **processor ↔ slack** — Tightest coupling in the repo. The processor calls `poll_for_response()` for
  title selection, which **blocks the entire watch loop indefinitely**. A "processor is hung / nothing is
  processing" symptom is very often really "Slack is waiting on a human." Same for
  `poll_for_resume()` on credits exhaustion.
- **processor → publish-triggers** — The processor **spawns `publish_poller.py` as a subprocess** after
  each successful episode. Lifecycle/orphaning questions live at this seam.
- **publish-triggers → publishing** — Both the poller and the webhook call into `blog_publisher`, with
  **no idempotency check**, so double-publish is reachable if both paths fire.
- **publish-triggers ↔ slack** — Poller reads Slack reactions/replies (needs `reactions:read`); shares the
  rate-limit budget and the same bot token as the processor's own polling.
- **publishing → external (weekly-brew)** — Imports `youtube_helper.py` from **outside this repo**. A
  path change there breaks publishing here with no signal in this codebase.
- **deployment → everything** — `.env` is shell-sourced, so a badly-quoted secret silently corrupts any
  subsystem downstream (this actually broke WordPress auth). `KeepAlive: true` converts any hard failure
  anywhere into a silent infinite crash-loop rather than a visible stop.
- **thumbnails → (nothing yet)** — Deliberately isolated; no importers. Shares `GOOGLE_API_KEY` with
  `YOUTUBE_API_KEY` (same Google credential), so a quota/key problem there could surface in **publishing**.

## Known live traps (as of this build)

These bit us recently or are one edit away from biting. Check them before deep-diving:

1. ~~**The model ID lives in code, not config.**~~ **RESOLVED 2026-07-15.** Model resolution now flows
   through `model_registry.get_model()` (reads `config.json api.model`, default `claude-sonnet-5`;
   `ANTHROPIC_MODEL` overrides). The old hardcoded `MODEL` constant — which caused a total 404 crash-loop
   when it went stale — is gone. A retired model now triggers a Slack-driven recovery
   (`ModelUnavailableError` → pick replacement → `set_model()` → retry), and `test_model_registry.py`
   fails the build if any call site reintroduces a hardcoded `claude-*` literal.
2. **`.env` is `source`d by bash.** Any value containing spaces MUST be quoted or bash truncates it at the
   first space. This silently broke `WP_APP_PASSWORD` (WordPress app passwords are space-separated).
3. **The committed plist is a stale template** with unsubstituted placeholders; the installed one has
   diverged. Re-running `install_launch_agent.sh` would clobber the working agent.
4. **`logs/stdout.log` lags** — Python block-buffers when stdout is a file, so a healthy process can look
   frozen. Never infer "hung" from a silent stdout; check `stderr.log` and process liveness.
5. **The production parsers have no unit coverage.** `test_parse_response.py` only exercises the
   *deprecated* mega-prompt parser; the three parsers actually used in the pipeline are covered only by
   `test_pipeline.py`, which costs real API spend to run.
6. **`.publish_poller_state.json` is a single global path**, not per-episode — concurrent pollers can
   overwrite each other's state.
