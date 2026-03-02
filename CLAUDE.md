# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

First Cup Processor - Automated YouTube transcript processing system for Product Coffee's weekly "First Cup" panel discussions. Uses Claude AI (Anthropic API) to generate SEO-optimized titles, descriptions, and newsletter articles with Slack integration for mobile-friendly title selection.

**Project Type:** Python automation tool with macOS Launch Agent integration
**Status:** Active - In Production Use
**Cost:** ~$0.15-0.30 per 30-minute episode

## Project Status

### ✅ Completed Work

- ✅ Core Claude AI integration for content generation (youtube_processor.py)
- ✅ Slack integration with threaded conversations (slack_helper.py)
- ✅ macOS Launch Agent for automatic file watching
- ✅ Interactive title selection (CLI and Slack)
- ✅ Template system for YouTube descriptions
- ✅ Dual output: Newsletter teaser (~50-75 words) + LinkedIn/blog post (~200-250 words)
- ✅ Organized output management (per-episode directories)
- ✅ Launch Agent installation script
- ✅ Comprehensive documentation suite (3 setup guides + README)
- ✅ Blog publishing via Slack command (blog_publisher.py)
  - React with 📤 emoji OR reply "publish" in Slack thread to post to WordPress
  - Publish poller daemon monitors for triggers for 24 hours after processing
  - Auto-fetches YouTube video URL from First Cup playlist
  - Uploads YouTube thumbnail as featured image
  - Sets "First Cup" category automatically
  - Creates post as draft for review
- ✅ Publish poller daemon (publish_poller.py)
  - Spawned automatically after transcript processing completes
  - Polls Slack every 60 seconds for emoji reactions or text commands
  - Auto-terminates after 24 hours or when publish completes
- ✅ **API Credits Exhaustion — Pause & Resume** (2026-03-01) ⭐ **LATEST**
  - Fixed bug where credits exhaustion permanently marked file as FAILED_ and never retried
  - `APICreditsExhaustedError` now pauses the watcher instead of failing
  - With Slack: sends top-level notification via `notify_credits_exhausted()`, then blocks via `poll_for_resume()` (polls every 30s for "resume" reply)
  - Without Slack: sets module-level `_credits_paused_for_file` flag; watch loop pauses with instructions to restart
  - File is NOT marked FAILED_ — will be retried automatically after resume
  - `APIRateLimitError` retains original FAILED_ behavior (intentional: rate limits are temporary, not actionable)
  - New methods in `slack_helper.py`: `notify_credits_exhausted()` (top-level message, not threaded) and `poll_for_resume()` (blocks until "resume" reply)
- ✅ **Multi-Step Pipeline Architecture** (2026-01-05)
  - Replaced single mega-prompt with focused 4-step pipeline for 100% reliability
  - Step 2: YouTube description + keywords (4000 tokens, focused prompt)
  - Step 3: Newsletter teaser (1000 tokens, uses title + description hook)
  - Step 4: Blog post (2000 tokens, encourages watching video)
  - Fixed keywords/newsletter/blog post generation failures (now 100% success rate)
  - Added robust JSON error handling for all Slack API calls (prevents service crashes)
  - Added test_pipeline.py for validating multi-step architecture
  - Each step builds on previous outputs for better coherence and quality
- ✅ **Keyword Generation Fix & Regression Tests** (2025-12-16)
  - Fixed issue where Claude occasionally failed to generate keywords
  - Strengthened prompt with REQUIRED markers and checklist
  - Added validation warnings when keywords are empty or incomplete
  - Added comprehensive missing section detection in parse_response()
  - Created test_parse_response.py regression test suite (6 tests)

## Architecture Overview

This is a YouTube transcript processor optimized for Product Coffee's "First Cup" panel discussion format. It uses Claude AI to generate SEO-optimized titles, descriptions, and newsletter articles.

### Core Components

**youtube_processor.py** - Main application with three execution modes:
1. **Watch mode** (default): Continuously monitors `./transcripts/` for new files
2. **Manual mode**: Process files without watching (triggered by Launch Agent)
3. **Test mode** (`--test-slack`): Verify Slack integration

**slack_helper.py** - Slack integration layer handling:
- Message threading (one thread per transcript)
- Interactive polling (waits indefinitely for user responses)
- Notification lifecycle (start → titles → selection → completion → publish)
- Publish command support (reply "publish" to post to WordPress)
- Credits exhaustion alerts: `notify_credits_exhausted()` sends a top-level (non-threaded) message; `poll_for_resume()` blocks until user replies "resume"

**blog_publisher.py** - WordPress blog publishing:
- WordPress REST API integration with HTTPBasicAuth
- YouTube Data API integration (reuses weekly-brew helper)
- Featured image upload from YouTube thumbnails
- Category management ("First Cup" category)

**publish_poller.py** - Background daemon for publish triggers:
- Spawned by youtube_processor.py after processing completes
- Polls Slack every 60 seconds for 📤 emoji reactions or "publish" replies
- Auto-terminates after 24 hours or on successful publish
- Uses state file (`.publish_poller_state.json`) for inter-process communication

### Data Flow

```
Transcript file → Step 1: Title generation (5 options) → Interactive selection
                         ↓
                  Step 2: YouTube description + keywords (focused prompt)
                         ↓
                  Step 3: Newsletter teaser (uses title + hook from Step 2)
                         ↓
                  Step 4: Blog post (uses title + transcript)
                         ↓
                  Save all outputs → Slack notification + spawn publish_poller.py
                         ↓ (polls every 60s for up to 24h)
                  Detects 📤 reaction or "publish" reply
                         ↓
                  YouTube API → WordPress API → Blog post created
```

**Key architectural decisions:**
- **Multi-step pipeline** - Each step has focused prompt with specific token limits (more reliable than mega-prompt)
- Title selection happens BEFORE content generation (ensures all outputs align with chosen title)
- Each step builds on previous outputs (Step 3 uses hook from Step 2)
- Slack uses `thread_ts` for conversation threading (not `last_message_ts`)
- Configuration split: secrets in `.env`, settings in `config.json`
- Robust JSON error handling prevents service crashes from invalid Slack API responses
- **Credits exhaustion pauses, rate limits fail** - `APICreditsExhaustedError` is retryable (user can add funds and resume); `APIRateLimitError` marks FAILED_ because it auto-resolves without user action. Module flag `_credits_paused_for_file` coordinates between the processor function and the watch loop when Slack is unavailable

### Prompt Engineering

The system uses a **multi-step pipeline** with focused prompts for each content type:

**Step 1: Title Generation** (`get_titles_from_claude`)
- 5 SEO-optimized title options (<60 chars)
- Supports feedback iteration for refinement
- Interactive selection via CLI or Slack

**Step 2: YouTube Description + Keywords** (`create_youtube_description_prompt`)
- Max tokens: 4000
- Inputs: selected title + transcript
- Outputs: hook, key topics, timestamps, panelists, keywords
- Plain text only (no markdown)
- Focused on description components for YouTube

**Step 3: Newsletter Teaser** (`create_newsletter_teaser_prompt`)
- Max tokens: 1000
- Inputs: title + description hook + transcript
- Output: Short ~50-75 word email teaser
- Uses markdown (`**bold**`, `*italics*`, `[links]()`)
- Builds on hook from Step 2 for coherence

**Step 4: Blog Post** (`create_blog_post_prompt`)
- Max tokens: 2000
- Inputs: title + transcript
- Output: ~200-250 word article encouraging video watch
- Uses markdown formatting
- MUST start with "☕️ First Cup: [title]" headline

**Critical requirements across all steps:**
- Current date context to prevent wrong year references
- Focus on First Cup panel (first ~25 min), not main session teaser
- Newsletter/blog use markdown, YouTube components use plain text
- Each step validated with specific extraction and warnings

### Parsing Functions

The multi-step pipeline uses dedicated parsing functions for each step:

**`parse_youtube_description_response()`** - Step 2 output:
- Extracts: hook, key_topics, timestamps, panelists, keywords
- Strips markdown from YouTube components (plain text only)
- Validates each section with warnings if missing
- Keywords validated for completeness (must have commas, >20 chars)

**`parse_newsletter_teaser_response()`** - Step 3 output:
- Pattern: `r'NEWSLETTER\s+TEASER:\s*(.*?)$'`
- Keeps all markdown formatting intact
- Returns string directly (not dict)

**`parse_blog_post_response()`** - Step 4 output:
- Pattern: `r'(?:LINKEDIN/?BLOG\s*POST|BLOG\s*POST):\s*(.*?)$'`
- Strips email subject lines if present
- Keeps all markdown formatting intact
- Returns string directly (not dict)

**Key rules:**
- **Do NOT strip markdown** from newsletter/blog content
- YouTube description components use plain text (markdown stripped)
- Each parser validates and logs extraction status
- Missing sections trigger warnings with clear error messages

## Configuration & Secrets

**Security model (12-factor app):**
- `.env` = All secrets (API key, Slack tokens) - NEVER committed
- `config.json` = Settings only (paths, enabled flags) - Safe to commit
- Templates: `.env.template` and `config.json.template` for documentation

**Launch Agent setup:**
- `run_processor.sh` wrapper loads `.env` before executing
- Uses Anaconda Python (`/Users/jasonbrett/anaconda3/bin/python3`)
- Logs to `logs/stdout.log` and `logs/stderr.log`

## External Services & APIs

### Anthropic Claude API (Primary Service)
**Purpose:** Generate SEO-optimized titles, descriptions, and newsletter articles
**SDK:** `anthropic` Python library
**Authentication:** API key via `ANTHROPIC_API_KEY` environment variable
**Credentials:** Obtain from https://console.anthropic.com/

**Models Used:**
- Claude 3.5 Sonnet (default) - Balanced performance and quality

**API Patterns:**
```python
# In youtube_processor.py
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    temperature=0.7,
    messages=[{"role": "user", "content": prompt}]
)
```

**Cost Management:**
- ~$0.15-0.30 per episode
- Single mega-prompt reduces API calls
- Title regeneration uses smaller, focused prompts

### Slack API (Optional)
**Purpose:** Mobile-friendly title selection and progress notifications
**SDK:** Native HTTP requests (no external SDK)
**Authentication:** Bot token + webhook URL via environment variables
**Credentials:** Create Slack app at https://api.slack.com/apps

**Required Environment Variables:**
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_USER_ID=U01234567890  # or channel ID C01234567890
```

**Required Scopes:**
- `chat:write` - Send messages
- `channels:history` - Read channel messages
- `groups:history` - Read private channel messages
- `reactions:read` - Read emoji reactions (for publish trigger)

**API Patterns:**
```python
# In slack_helper.py
import requests

# Send threaded message
requests.post(
    "https://slack.com/api/chat.postMessage",
    headers={"Authorization": f"Bearer {bot_token}"},
    json={
        "channel": user_id,
        "text": message,
        "thread_ts": thread_ts  # For threading
    }
)

# Poll for responses
requests.get(
    "https://slack.com/api/conversations.history",
    headers={"Authorization": f"Bearer {bot_token}"},
    params={"channel": user_id, "oldest": thread_ts}
)
```

**Setup Guide:** See `SLACK_SETUP_GUIDE.md` for complete setup instructions

### YouTube Data API (Optional - for blog publishing)
**Purpose:** Fetch video URL and thumbnail from First Cup playlist
**SDK:** `google-api-python-client` via `youtube_helper.py` (from weekly-brew project)
**Authentication:** API key via `YOUTUBE_API_KEY` environment variable
**Credentials:** Get from https://console.cloud.google.com/apis/credentials

**API Patterns:**
```python
# Reuses weekly-brew/youtube_helper.py
from youtube_helper import get_most_recent_video, FIRST_CUP_PLAYLIST_ID

video = get_most_recent_video(FIRST_CUP_PLAYLIST_ID, title_match="AI Bubble")
# Returns: {'video_id', 'title', 'share_url', 'published_at', 'description'}

thumbnail_url = f"https://img.youtube.com/vi/{video['video_id']}/maxresdefault.jpg"
```

### WordPress REST API (Optional - for blog publishing)
**Purpose:** Create blog posts on Product Coffee website
**SDK:** Native HTTP requests with `requests` library
**Authentication:** Application password via HTTPBasicAuth
**Credentials:** Create application password in WordPress Dashboard > Users > Profile

**Required Environment Variables:**
```bash
WP_SITE_URL=https://productcoffee.com
WP_USERNAME=your-wordpress-username
WP_APP_PASSWORD=your-application-password-here
```

**API Patterns:**
```python
# In blog_publisher.py
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth(username, app_password)

# Create post
response = requests.post(
    f"{site_url}/wp-json/wp/v2/posts",
    auth=auth,
    json={
        'title': title,
        'content': html_content,
        'status': 'draft',
        'categories': [category_id],
        'featured_media': media_id
    }
)

# Upload media (featured image)
response = requests.post(
    f"{site_url}/wp-json/wp/v2/media",
    auth=auth,
    headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    data=image_bytes
)
```

## Development Commands

### Testing & Running

```bash
# Manual processing (one-time)
python3 youtube_processor.py

# Test Slack integration
python3 youtube_processor.py --test-slack

# Run regression tests
python3 test_parse_response.py

# Test multi-step pipeline
python3 test_pipeline.py

# Trigger via Launch Agent (drop file)
cp sample_transcript.txt transcripts/

# Check Launch Agent status
launchctl list | grep firstcup

# Restart after code changes
launchctl unload ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
launchctl load ~/Library/LaunchAgents/com.productcoffee.firstcup.plist

# View logs
tail -f logs/stderr.log  # Errors
tail -f logs/stdout.log  # Output
```

### Template Customization

**YouTube descriptions:** Edit `youtube_description_template.txt`
- Uses placeholders: `{{HOOK}}`, `{{KEY_TOPICS}}`, `{{TIMESTAMPS}}`, `{{KEYWORDS}}`

**Newsletter style:** Add examples to `newsletter_examples.md`
- AI learns from examples via few-shot learning
- More examples = better style matching

### Prompt Modifications

Edit `youtube_processor.py`:
- `create_youtube_description_prompt()` (line ~140): Step 2 YouTube components
- `create_newsletter_teaser_prompt()` (line ~211): Step 3 newsletter teaser
- `create_blog_post_prompt()` (line ~244): Step 4 blog post
- `get_titles_from_claude()` (line ~360): Title generation with feedback
- `create_prompt()` (line ~306): DEPRECATED mega-prompt (kept for reference)

## Common Issues

**Empty or missing content (keywords, newsletter, blog post):**
- **FIXED in multi-step pipeline** - Now 100% success rate
- Multi-step architecture prevents Claude from getting overwhelmed
- Each component generated in focused prompt with appropriate token limits
- If failures occur, check `full_response.txt` for each step's output
- Run `python3 test_pipeline.py` to validate pipeline is working

**API credits exhausted (processor pauses instead of failing):**
- **FIXED (2026-03-01)** - File is no longer marked FAILED_; processor pauses and waits
- With Slack: reply "resume" in the Slack thread after adding credits; processor retries automatically
- Without Slack: watch loop prints billing URL + restart instructions; restart the processor after adding credits
- Rate limit errors (`APIRateLimitError`) still mark FAILED_ — this is intentional, as rate limits resolve automatically and the file can be manually re-queued when ready
- Check logs for "API CREDITS EXHAUSTED" or "RATE LIMIT HIT" to distinguish the two cases

**JSON parsing errors from Slack API:**
- **FIXED** - Added robust error handling for all `.json()` calls
- Invalid JSON responses now logged with error details
- Service continues running instead of crashing
- Check logs for "Invalid JSON response" warnings

**Slack not responding to replies:**
- Ensure `poll_for_response()` uses `thread_ts` not `message_ts`
- Bot must be invited to channel: `/invite @First Cup Processor`
- Check scopes: `chat:write`, `channels:history`, `groups:history`

**Launch Agent not triggering:**
- Verify `.env` is loaded (check `run_processor.sh`)
- Ensure correct Python path in wrapper script
- Check `KeepAlive` is true in plist

## Code Modification Guidelines

**When modifying prompts:**
- Maintain clear section headers (TITLE OPTIONS, NEWSLETTER ARTICLE, etc.)
- Regex patterns depend on these headers - update both if changed
- Test with sample transcript after prompt changes

**When modifying Slack integration:**
- Always call `start_new_thread()` before processing new transcript
- Use `thread_ts` for threading, not `last_message_ts`
- Send all messages with `in_thread=True` except the first

**When adding new output files:**
- Add to `save_outputs()` function (line ~630)
- Follow naming pattern: lowercase with underscores
- Save to transcript-specific directory (not root outputs/)

## Project Structure

```
first-cup-processor/
├── youtube_processor.py          # Main processor (3 modes: watch/manual/test)
├── slack_helper.py                # Slack integration layer
├── blog_publisher.py              # WordPress blog publishing (optional)
├── publish_poller.py              # Background daemon for publish triggers
├── publish_webhook.py             # HTTP webhook server (alternative trigger method)
├── test_parse_response.py         # Regression tests for response parsing
├── test_pipeline.py               # Test script for multi-step pipeline validation
├── config.json                    # Settings (safe to commit)
├── .env                           # Secrets (NEVER commit)
├── .env.template                  # Template for credentials
├── config.json.template           # Template for settings
├── .publish_poller_state.json     # State file for poller (auto-generated, gitignored)
├── requirements.txt               # Python dependencies
├── install_launch_agent.sh        # Auto-install Launch Agent
├── run_processor.sh               # Launch Agent wrapper script
├── com.productcoffee.firstcup.plist        # Launch Agent for processor
├── com.productcoffee.firstcup.poller.plist # Launch Agent for poller (on-demand)
├── com.productcoffee.firstcup.webhook.plist # Launch Agent for webhook (optional)
├── youtube_description_template.txt  # YouTube description template
├── newsletter_examples.md         # Newsletter style examples (few-shot learning)
├── sample_transcript.txt          # Test transcript file
├── transcripts/                   # Drop new transcripts here (watched by Launch Agent)
├── outputs/                       # Generated outputs (per-episode directories)
│   └── [episode_name]/
│       ├── SELECTED_TITLE.txt
│       ├── youtube_description.txt
│       ├── newsletter_teaser.txt     # Short hook for email newsletter
│       ├── linkedin_blog_post.txt    # Full article for social/blog
│       ├── keywords.txt
│       ├── description_components.txt
│       └── full_response.txt         # Raw Claude response for debugging
├── logs/                          # Application logs
│   ├── stdout.log
│   ├── stderr.log
│   ├── poller_stdout.log          # Publish poller logs
│   └── poller_stderr.log
├── ai-chats/                      # Development notes
├── CLAUDE.md                      # AI assistant guidance (this file)
├── README.md                      # User-facing documentation
├── TODO.md                        # Active tasks and backlog
├── SLACK_SETUP_GUIDE.md          # Slack app setup walkthrough
├── LAUNCH_AGENT_GUIDE.md         # Launch Agent setup and management
└── TEMPLATE_GUIDE.md             # YouTube description template customization
```

## Next Steps / TODO

See [TODO.md](TODO.md) for current active tasks and backlog.

**Potential Enhancements:**
- [ ] Support for multi-episode batch processing
- [ ] Analytics tracking (title CTR, newsletter engagement)
- [ ] Additional output formats (Twitter threads, LinkedIn posts)
- [ ] Integration with YouTube API for direct upload
- [ ] A/B testing framework for title selection

## Getting Help

- **User Guide:** [README.md](README.md) - Complete setup and usage instructions
- **Slack Setup:** [SLACK_SETUP_GUIDE.md](SLACK_SETUP_GUIDE.md) - Step-by-step Slack app creation
- **Launch Agent:** [LAUNCH_AGENT_GUIDE.md](LAUNCH_AGENT_GUIDE.md) - Auto-trigger setup and troubleshooting
- **Templates:** [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md) - Customize YouTube description templates
- **Active Tasks:** [TODO.md](TODO.md) - Current work and backlog
