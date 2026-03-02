# API Reference: First Cup Processor

**Last Updated:** 2026-03-01

---

## Anthropic Claude API

**Purpose:** Content generation (titles, descriptions, newsletter, blog post)
**Model:** `claude-sonnet-4-20250514`
**Auth:** `ANTHROPIC_API_KEY` environment variable
**SDK:** `anthropic` Python library (`anthropic>=0.18.0`)

### Usage Pattern

```python
from anthropic import Anthropic
import anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# All calls go through call_claude_api() in youtube_processor.py
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    messages=[{"role": "user", "content": prompt}]
)
response_text = message.content[0].text
```

### Error Classification

`call_claude_api()` maps Anthropic SDK exceptions to project-specific errors:

| Condition | SDK Exception | Project Exception |
|-----------|--------------|------------------|
| "credit"/"billing"/"payment" in message | `anthropic.RateLimitError` | `APICreditsExhaustedError` |
| Other rate limit | `anthropic.RateLimitError` | `APIRateLimitError` |
| Invalid/expired API key | `anthropic.AuthenticationError` | `APICreditsExhaustedError` |

### Token Budgets by Step

| Step | Max Tokens | Notes |
|------|-----------|-------|
| Title generation | ~1000 | Small, focused |
| YouTube description + keywords | 4000 | Largest step |
| Newsletter teaser | 1000 | Short output |
| Blog post | 2000 | Medium article |

**Cost:** ~$0.15-0.30 per 30-minute episode

---

## Slack API

**Purpose:** Interactive title selection, processing notifications, publish triggers, credits-exhaustion alerts
**Auth:** `SLACK_BOT_TOKEN` environment variable (xoxb- prefix)
**Delivery:** `SLACK_WEBHOOK_URL` for simple sends, bot token for interactive polling

### Required Environment Variables

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_USER_ID=U01234567890  # or channel ID C01234567890
```

### Required Bot Scopes

| Scope | Used For |
|-------|---------|
| `chat:write` | Sending messages |
| `channels:history` | Reading channel message history |
| `groups:history` | Reading private channel history |
| `reactions:read` | Detecting 📤 emoji for publish trigger |

### Key API Endpoints Used

```python
# Send a message
POST https://slack.com/api/chat.postMessage
{
    "channel": user_id,
    "text": message,
    "thread_ts": thread_ts  # omit for top-level
}

# Read thread replies (poll_for_resume)
GET https://slack.com/api/conversations.replies
params: {"channel": user_id, "ts": thread_ts, "limit": 20}

# Read channel history (poll_for_response, check_for_publish_command)
GET https://slack.com/api/conversations.history
params: {"channel": user_id, "oldest": thread_ts}

# Read reactions (publish trigger detection)
GET https://slack.com/api/reactions.get
```

### Threading Model

- One Slack thread per transcript (`thread_ts` stored on `SlackHelper` instance)
- All messages go to the thread except `notify_credits_exhausted()`, which sends top-level
- `thread_ts` is the timestamp of the first message in the thread, not `message_ts`

### slack_helper.py Public Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `is_enabled()` | `() -> bool` | Returns True if credentials are configured |
| `start_new_thread()` | `(filename: str) -> str` | Creates thread anchor, returns thread_ts |
| `send_message()` | `(text: str, in_thread=True) -> dict` | Sends message, optionally threaded |
| `send_titles()` | `(titles: list[str]) -> str` | Posts numbered title list |
| `poll_for_response()` | `(oldest_ts: str) -> str` | Blocks until user replies |
| `notify_completion()` | `(output_path: str, filename: str) -> None` | Posts completion summary |
| `notify_credits_exhausted()` | `(filename: str) -> None` | Top-level credits alert |
| `poll_for_resume()` | `(poll_interval=30) -> bool` | Blocks until "resume" reply |
| `notify_error()` | `(filename: str, error_message: str) -> None` | Posts error notification |
| `notify_cancelled()` | `(filename: str) -> None` | Posts cancellation notice |
| `check_for_publish_command()` | `() -> None` | Checks for idle publish triggers |
| `set_publish_callback()` | `(callback: callable) -> None` | Register publish function |

---

## YouTube Data API

**Purpose:** Fetch video URL and thumbnail for blog publishing
**Auth:** `YOUTUBE_API_KEY` environment variable
**SDK:** `google-api-python-client` (via `youtube_helper.py` from weekly-brew project)

```python
from youtube_helper import get_most_recent_video, FIRST_CUP_PLAYLIST_ID

video = get_most_recent_video(FIRST_CUP_PLAYLIST_ID, title_match="Episode Title")
# Returns: {'video_id', 'title', 'share_url', 'published_at', 'description'}

thumbnail_url = f"https://img.youtube.com/vi/{video['video_id']}/maxresdefault.jpg"
```

---

## WordPress REST API

**Purpose:** Create draft blog posts with featured images
**Auth:** Application password via `HTTPBasicAuth`
**Library:** `requests` (standard HTTP, no special SDK)

### Required Environment Variables

```bash
WP_SITE_URL=https://productcoffee.com
WP_USERNAME=your-wordpress-username
WP_APP_PASSWORD=your-application-password-here
```

### Key Endpoints

```python
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth(username, app_password)

# Upload featured image
response = requests.post(
    f"{site_url}/wp-json/wp/v2/media",
    auth=auth,
    headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    data=image_bytes
)
media_id = response.json()["id"]

# Create post as draft
response = requests.post(
    f"{site_url}/wp-json/wp/v2/posts",
    auth=auth,
    json={
        "title": title,
        "content": html_content,
        "status": "draft",
        "categories": [category_id],
        "featured_media": media_id
    }
)
```

**Application passwords:** Create in WordPress Dashboard > Users > Profile > Application Passwords
