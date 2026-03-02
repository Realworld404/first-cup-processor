# ADR 001: Credits Exhaustion Should Pause, Not Fail

**Date:** 2026-03-01
**Status:** Accepted
**Context:** First Cup Processor — error handling for Anthropic API errors

---

## Context

When the Anthropic API returns an error indicating that API credits are exhausted (or the API key is invalid/expired), the processor previously treated this the same as any other fatal error: it marked the transcript file as `FAILED_[filename]` in the processed-files log and moved on.

The consequence was that the user had to:
1. Add credits to their Anthropic account
2. Manually rename or remove the `FAILED_` entry from the log
3. Re-trigger the processor

This was error-prone and confusing. Users reported that episodes were "lost" after credit exhaustion.

---

## Decision

Credits exhaustion (`APICreditsExhaustedError`) now **pauses the processor and waits for user action** rather than marking the file as permanently failed.

### With Slack enabled
1. `process_transcript_file()` catches `APICreditsExhaustedError`
2. Calls `slack.notify_credits_exhausted(filename)` — sends a **top-level** (non-threaded) Slack message with the billing URL and instructions to reply "resume"
3. Calls `slack.poll_for_resume()` — blocks, polling `conversations.replies` every 30 seconds
4. When the user replies "resume", `poll_for_resume()` returns `True`
5. `_credits_paused_for_file` is cleared and `process_transcript_file()` returns `None` (without marking FAILED_)
6. The watch loop picks up the file again on the next iteration and retries

### Without Slack
1. `process_transcript_file()` catches `APICreditsExhaustedError`
2. Sets `_credits_paused_for_file = filepath.name` (module-level flag)
3. Returns `None` (no FAILED_ marker written)
4. The watch loop sees the flag is set and prints billing instructions on each iteration, then sleeps
5. The user restarts the processor after adding credits; the flag is cleared on startup

### Rate limits behave differently
`APIRateLimitError` still marks the file as `FAILED_`. Rate limits are temporary and auto-resolve — no user action is needed, and retrying immediately would worsen the situation.

---

## Consequences

**Positive:**
- No more "lost" episodes after credit exhaustion
- User receives clear instructions and a direct link to billing
- Processor resumes automatically after credits are added (Slack path)
- Consistent experience: pausing feels intentional, not like a crash

**Negative:**
- Without Slack, the watch loop is effectively frozen until the processor is restarted
- The `_credits_paused_for_file` module-level flag is a form of global mutable state — acceptable for a single-process script, but worth noting

**Invariant maintained:**
- A file is only ever marked `FAILED_` for errors that are non-retryable by the user in the current session (rate limits, generic exceptions not related to credits)
- Credits exhaustion and authentication errors are always retryable after user action

---

## Alternatives Considered

**Retry with exponential backoff:** Rejected. Credits exhaustion is not a transient error — retrying immediately just hammers a billing-blocked API.

**Mark FAILED_ and document how to retry:** Rejected. Too error-prone; users consistently missed the manual retry step.

**Separate daemon for retry queue:** Rejected. Over-engineered for the current volume (one episode per week).
