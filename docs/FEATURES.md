# Features: First Cup Processor

**Last Updated:** 2026-03-01

---

## Core Features

### Multi-Step Content Pipeline
Automated generation of all post-production assets for a First Cup episode from a single transcript file.

**What it produces:**
- 5 SEO-optimized title options (user selects one)
- YouTube description (hook, key topics, panelist list, timestamps, keywords)
- Newsletter teaser (~50-75 words, email-ready markdown)
- Blog post (~200-250 words, markdown with mandatory headline format)

**How to trigger:**
```bash
# Drop a transcript into the watched directory
cp my_episode.txt transcripts/

# Or process manually
python3 youtube_processor.py
```

---

### Interactive Title Selection
After generating 5 title options, the processor waits for the user to select one before generating any other content. This ensures all downstream outputs align with the chosen title.

**Selection methods:**
- **Slack:** Reply with a number (1-5) in the Slack thread; also supports "none" or text feedback for regeneration
- **CLI:** Type the number at the terminal prompt

**Feedback iteration:** Replying with text other than a number re-prompts Claude for new titles incorporating the feedback.

---

### Slack Integration
All interactions can happen from a mobile device via Slack.

**Notification flow:**
1. Processing started — thread created
2. Title options posted — bot waits for reply
3. Processing each step — status updates in thread
4. Completion — outputs listed in thread
5. Publish trigger — reply "publish" or react with 📤

**Credits exhaustion alerts:** Sent as a top-level Slack message (not threaded) so it's visible regardless of thread context. Includes billing URL and resume instructions.

---

### Pause & Resume on API Credits Exhaustion
When the Anthropic API returns a credits/billing error, the processor pauses and waits for the user to resume rather than permanently failing the file.

**With Slack:**
1. Slack sends top-level notification with billing URL
2. Processor blocks, polling for "resume" reply every 30 seconds
3. User adds credits, replies "resume"
4. Processor retries the file automatically

**Without Slack:**
1. Console prints billing URL and restart instructions
2. Watch loop pauses (continues sleeping, won't process new files)
3. User restarts processor after adding credits

**Key distinction from rate limits:** `APIRateLimitError` still marks the file as `FAILED_` (prefixed with `FAILED_` in the processed-files log), because rate limits resolve automatically and do not require user action.

---

### WordPress Blog Publishing
After processing, reply "publish" in Slack or react with 📤 to create a draft WordPress post.

**What it does automatically:**
- Fetches the YouTube video URL from the First Cup playlist
- Downloads the YouTube thumbnail as the featured image
- Creates the post in the "First Cup" category
- Sets status to "draft" for final review

**Managed by:** `publish_poller.py` daemon, spawned automatically after each processing run. Monitors for 24 hours then terminates.

---

### Template-Driven YouTube Descriptions
The final YouTube description is assembled from a template file (`youtube_description_template.txt`) using placeholders populated by Step 2 output.

**Placeholders:**
- `{{HOOK}}` — Opening sentence from Step 2
- `{{KEY_TOPICS}}` — Bullet list of discussion topics
- `{{TIMESTAMPS}}` — Approximate timestamps
- `{{KEYWORDS}}` — Comma-separated SEO keywords

Edit the template to change description structure without modifying code.

---

### Few-Shot Newsletter Style Learning
Add example newsletters to `newsletter_examples.md` to teach the AI your preferred style. More examples produce better style matching via few-shot learning.

---

### Organized Per-Episode Output
All outputs are stored in a dedicated directory: `outputs/[episode_name]/`. Files are never mixed between episodes.

---

## Optional / Advanced Features

### Thumbnail Generator
`thumbnail_generator.py` — Standalone tool for generating episode thumbnail images. See `THUMBNAIL_PLAN.md` for planned integration.

### Publish Webhook
`publish_webhook.py` — Alternative HTTP webhook server for triggering blog publishing without relying on Slack polling.

---

## Operational Behavior

| Scenario | Behavior |
|----------|---------|
| Transcript dropped during processing of another file | Queued; processed on next watch loop iteration |
| Processing succeeds | File logged as processed; not reprocessed |
| `APICreditsExhaustedError` | Processor pauses; file NOT marked failed; retried after resume |
| `APIRateLimitError` | File marked `FAILED_`; watcher skips on next loop |
| Generic exception | Error logged and Slack notified; watcher continues |
| User replies "none" to titles | Processing cancelled; file not marked failed |
| Slack unavailable | Falls back to CLI prompts |
