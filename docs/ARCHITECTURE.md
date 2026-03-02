# Architecture: First Cup Processor

**Last Updated:** 2026-03-01
**Project:** First Cup Processor
**Type:** Python automation tool with macOS Launch Agent integration

---

## System Overview

First Cup Processor automates post-production for Product Coffee's weekly "First Cup" panel discussions. A transcript file dropped into the `transcripts/` directory triggers a multi-step Claude AI pipeline that generates a YouTube title, description, newsletter teaser, and blog post. Results are surfaced via Slack for interactive review, then optionally published to WordPress.

---

## High-Level Data Flow

```
transcripts/episode.txt
        |
        v
  Watch Loop (watch_directory)
  - Polls every WATCH_INTERVAL seconds
  - Skips already-processed and FAILED_ files
  - Pauses on credits exhaustion (_credits_paused_for_file flag)
        |
        v
  process_transcript_file()
        |
        +---> Step 1: Title generation (get_titles_from_claude)
        |         5 SEO title options → Interactive selection via CLI or Slack
        |
        +---> Step 2: YouTube description + keywords (create_youtube_description_prompt)
        |         Inputs: selected title + transcript
        |         Outputs: hook, key_topics, timestamps, panelists, keywords
        |
        +---> Step 3: Newsletter teaser (create_newsletter_teaser_prompt)
        |         Inputs: title + hook from Step 2 + transcript
        |         Output: ~50-75 word email teaser with markdown
        |
        +---> Step 4: Blog post (create_blog_post_prompt)
        |         Inputs: title + transcript
        |         Output: ~200-250 word article with markdown headline
        |
        v
  save_outputs()  →  outputs/[episode_name]/
        |
        v
  Slack notifications + spawn publish_poller.py
        |
        v (polls every 60s for up to 24h)
  publish_poller.py
  Detects 📤 reaction or "publish" reply
        |
        v
  YouTube API → WordPress API → Blog post created (draft)
```

---

## Core Modules

### youtube_processor.py
Main application. Three execution modes:
1. **Watch mode** (default): `watch_directory()` loop monitors `./transcripts/` for new `.txt`, `.md`, `.json` files
2. **Manual mode**: Process a specific file once (triggered by Launch Agent or direct invocation)
3. **Test mode** (`--test-slack`): Verify Slack connectivity

Key functions:
- `process_transcript_file()` — Orchestrates the 4-step pipeline for a single file
- `watch_directory()` — The main watch loop with credits-pause guard
- `call_claude_api()` — Wrapper around Anthropic SDK with error classification
- `save_outputs()` — Writes all generated content to per-episode directory

Error handling hierarchy:
- `APICreditsExhaustedError` → Pause and wait for resume (NOT FAILED_)
- `APIRateLimitError` → Mark FAILED_ (auto-resolves, no user action needed)
- Generic `Exception` → Log, notify Slack, continue watching

### slack_helper.py
Slack integration layer. Requires `SLACK_BOT_TOKEN` and `SLACK_USER_ID` env vars.

Key methods:
| Method | Purpose |
|--------|---------|
| `start_new_thread()` | Creates thread anchor for a new transcript |
| `send_titles()` | Posts 5 title options and waits for selection |
| `poll_for_response()` | Blocks indefinitely until user replies with a number |
| `notify_completion()` | Posts completion summary with output paths |
| `notify_credits_exhausted(filename)` | Sends top-level (non-threaded) credits alert |
| `poll_for_resume(poll_interval=30)` | Blocks until user replies "resume" in thread |
| `check_for_publish_command()` | Monitors for publish triggers between files |

Threading model: one Slack thread (`thread_ts`) per transcript file. `notify_credits_exhausted()` deliberately sends outside the thread (top-level) so it's visible even if no thread exists.

### blog_publisher.py
Optional WordPress publishing module.
- WordPress REST API with `HTTPBasicAuth`
- YouTube Data API for fetching video URL and thumbnail from First Cup playlist
- Posts created as drafts in "First Cup" category with featured image

### publish_poller.py
Background daemon spawned after each successful processing run.
- Polls Slack every 60 seconds for 📤 emoji reactions or "publish" text replies
- Auto-terminates after 24 hours or on successful publish
- Coordinates via `.publish_poller_state.json` state file

---

## Error Handling: Credits vs. Rate Limit

A deliberate architectural distinction governs the two API error types:

| Error Type | Cause | Behavior | Why |
|------------|-------|----------|-----|
| `APICreditsExhaustedError` | Billing account depleted, API key invalid/expired | Pause watch loop; wait for "resume" | Requires user action; file should be retried after fix |
| `APIRateLimitError` | Token-per-minute quota exceeded | Mark `FAILED_`; move on | Resolves automatically; permanent retry loop would be harmful |

**Credits pause flow with Slack:**
```
APICreditsExhaustedError raised
  → slack.notify_credits_exhausted(filename)   # top-level Slack message
  → slack.poll_for_resume()                    # blocks, polls every 30s
    └─ user replies "resume" in Slack thread
  → _credits_paused_for_file = None            # clear flag
  → return None from process_transcript_file() # file NOT marked FAILED_
  → next watch loop iteration retries the file
```

**Credits pause flow without Slack:**
```
APICreditsExhaustedError raised
  → _credits_paused_for_file = filepath.name  # set module-level flag
  → return None from process_transcript_file()
  → watch loop sees flag set, prints billing URL
  → loop continues sleeping (WATCH_INTERVAL) until flag cleared
  → user must restart processor after adding credits
```

---

## Configuration

| File | Purpose | Committed? |
|------|---------|------------|
| `.env` | All secrets (API keys, tokens) | No |
| `config.json` | Settings (paths, feature flags) | Yes |
| `.env.template` | Documents required env vars | Yes |
| `config.json.template` | Documents config schema | Yes |

---

## Claude API Usage

| Step | Function | Max Tokens | Model |
|------|----------|-----------|-------|
| Title generation | `get_titles_from_claude` | ~1000 | claude-sonnet-4-20250514 |
| YouTube description + keywords | `create_youtube_description_prompt` | 4000 | claude-sonnet-4-20250514 |
| Newsletter teaser | `create_newsletter_teaser_prompt` | 1000 | claude-sonnet-4-20250514 |
| Blog post | `create_blog_post_prompt` | 2000 | claude-sonnet-4-20250514 |

**Cost:** ~$0.15-0.30 per 30-minute episode

---

## Output Directory Structure

```
outputs/[episode_name]/
├── SELECTED_TITLE.txt           # Chosen title from Step 1
├── youtube_description.txt      # Full assembled YouTube description
├── description_components.txt   # Raw Step 2 parsed components
├── keywords.txt                 # SEO keywords (comma-separated)
├── newsletter_teaser.txt        # ~50-75 word email teaser (markdown)
├── linkedin_blog_post.txt       # ~200-250 word blog article (markdown)
└── full_response.txt            # Raw Claude responses for debugging
```

---

## macOS Launch Agent

`com.productcoffee.firstcup.plist` configures automatic triggering when transcript files appear.

```
File dropped → launchd detects → run_processor.sh → youtube_processor.py
```

`run_processor.sh` loads `.env` before invoking the processor so secrets are available to the Launch Agent process.

Logs: `logs/stdout.log` and `logs/stderr.log`
