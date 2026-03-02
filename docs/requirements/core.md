# Core Requirements

**Last Updated:** 2026-03-01

---

## Runtime Requirements

### Python
- **Version:** Python 3.9+ (uses f-strings, pathlib, dataclasses)
- **Interpreter:** Anaconda Python at `/Users/jasonbrett/anaconda3/bin/python3` (for Launch Agent compatibility)

### Python Dependencies (`requirements.txt`)

```
anthropic>=0.18.0       # Anthropic Claude API SDK
requests>=2.31.0        # HTTP client for Slack and WordPress APIs
google-genai>=1.0.0     # Google AI (used by thumbnail_generator.py)
Pillow>=10.0.0          # Image processing (thumbnail generation)
```

Install:
```bash
pip install -r requirements.txt
```

---

## Required Configuration

### Mandatory Environment Variables (`.env`)

```bash
ANTHROPIC_API_KEY=sk-ant-...   # Required for all content generation
```

### Optional Environment Variables (`.env`)

```bash
# Slack integration (interactive title selection + notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_USER_ID=U01234567890

# WordPress blog publishing
WP_SITE_URL=https://productcoffee.com
WP_USERNAME=your-username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# YouTube Data API (for blog publishing, fetches thumbnail + video URL)
YOUTUBE_API_KEY=AIza...
```

### config.json Settings

```json
{
    "watch_dir": "./transcripts",
    "output_dir": "./outputs",
    "template_path": "./youtube_description_template.txt",
    "examples_path": "./newsletter_examples.md",
    "slack": {
        "enabled": true
    }
}
```

---

## File System Requirements

| Path | Purpose | Required? |
|------|---------|----------|
| `transcripts/` | Drop zone for new transcript files | Yes (auto-created) |
| `outputs/` | Generated content storage | Yes (auto-created) |
| `logs/` | Application logs | Yes (auto-created) |
| `youtube_description_template.txt` | YouTube description template | Recommended (fallback exists) |
| `newsletter_examples.md` | Newsletter style examples | Optional |
| `.env` | Secrets | Yes |
| `config.json` | Settings | Yes |

---

## macOS Launch Agent Requirements

- macOS 10.14+ (Mojave or later)
- `launchd` available (built into macOS)
- Anaconda Python installed at `/Users/jasonbrett/anaconda3/bin/python3`
- User must be logged in for Launch Agent to run

Install the Launch Agent:
```bash
bash install_launch_agent.sh
```
