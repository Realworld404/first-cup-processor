# Integration Requirements

**Last Updated:** 2026-03-01

---

## Anthropic Claude API (Required)

**What it does:** Generates titles, YouTube descriptions, newsletter teasers, and blog posts.

**Credentials:**
- Sign up at https://console.anthropic.com
- Create an API key at https://console.anthropic.com/settings/keys
- Add credits at https://console.anthropic.com/settings/billing

**Configuration:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

**Notes:**
- The model used is `claude-sonnet-4-20250514`
- Credits exhaustion raises `APICreditsExhaustedError` — processor will pause and wait for "resume" rather than failing the file permanently
- Rate limits raise `APIRateLimitError` — file is marked `FAILED_` (rate limits resolve automatically)
- Cost: ~$0.15-0.30 per 30-minute episode

---

## Slack API (Optional, Strongly Recommended)

**What it does:** Interactive title selection from mobile, processing notifications, publish triggers, credits exhaustion alerts.

**Setup:**
1. Go to https://api.slack.com/apps and create a new app
2. Add the app to your workspace
3. Enable the following Bot Token Scopes:
   - `chat:write`
   - `channels:history`
   - `groups:history`
   - `reactions:read`
4. Install the app to your workspace
5. Copy the Bot User OAuth Token (`xoxb-...`)
6. Create an incoming webhook for the channel
7. Invite the bot to the channel: `/invite @YourBotName`

**Configuration:**
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_USER_ID=U01234567890   # Your Slack user ID or the channel ID
```

**Finding your User ID:** Click your name in Slack > View profile > More > Copy member ID

**Full setup guide:** See `SLACK_SETUP_GUIDE.md`

**Fallback behavior without Slack:** CLI prompts at the terminal; credits exhaustion requires processor restart.

---

## WordPress REST API (Optional)

**What it does:** Creates draft blog posts from processed episodes when user triggers publish.

**Setup:**
1. Log into WordPress Dashboard
2. Go to Users > Profile
3. Scroll to "Application Passwords"
4. Create a new application password (name it "First Cup Processor")
5. Copy the generated password (shown only once)

**Configuration:**
```bash
WP_SITE_URL=https://productcoffee.com
WP_USERNAME=your-wordpress-username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

**Notes:**
- Posts are created as drafts for human review before publishing
- Category "First Cup" is set automatically (created if it doesn't exist)
- Requires YouTube API to also be configured for thumbnail fetching

---

## YouTube Data API (Optional — needed for blog publishing)

**What it does:** Fetches the YouTube video URL and thumbnail from the First Cup playlist to embed in WordPress posts.

**Setup:**
1. Go to https://console.cloud.google.com
2. Create or select a project
3. Enable the YouTube Data API v3
4. Create an API key (Credentials > Create Credentials > API Key)
5. Restrict the key to YouTube Data API v3

**Configuration:**
```bash
YOUTUBE_API_KEY=AIza...
```

**Implementation note:** Uses `youtube_helper.py` borrowed from the weekly-brew project. This file must be accessible on the Python path when running `blog_publisher.py`.

**Playlist:** `FIRST_CUP_PLAYLIST_ID` is hardcoded in `youtube_helper.py`. Update it if the playlist changes.

---

## Integration Dependency Map

```
ANTHROPIC_API_KEY   → Required for all content generation (Steps 1-4)

SLACK_WEBHOOK_URL   → Optional; enables Slack notifications
SLACK_BOT_TOKEN     → Required for interactive features (title selection, resume)
SLACK_USER_ID       → Required for all Slack features

WP_SITE_URL         → Required for WordPress publishing
WP_USERNAME         → Required for WordPress publishing
WP_APP_PASSWORD     → Required for WordPress publishing
YOUTUBE_API_KEY     → Required for WordPress publishing (thumbnail fetch)
```

WordPress publishing requires all four of: `WP_SITE_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`, and `YOUTUBE_API_KEY`.
