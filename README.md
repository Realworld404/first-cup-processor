# 🎬 First Cup Processor

Automated YouTube transcript processing with Slack integration and macOS auto-triggering. Generates SEO-optimized titles, descriptions, and newsletter articles using Claude AI.

**Cost**: ~$0.15-0.30 per 30-minute episode

## ✨ Features

- 🤖 **Slack Integration** - Interactive title selection via Slack (mobile-friendly)
- 🚀 **Auto-trigger** - macOS Launch Agent runs automatically when you drop files
- ⚡ **Interactive Selection** - Choose from 5 titles, request new ones, or provide custom titles
- ☕ **First Cup Optimized** - Prompts tuned for Product Coffee's panel discussion format
- 📝 **Template System** - Customizable YouTube description templates
- 🎯 **Markdown Newsletters** - ~150 word articles with bold, italics, and hyperlinks
- 📊 **Organized Outputs** - All files neatly organized per episode

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python packages (Anaconda recommended)
pip install anthropic requests
```

### 2. Configure API Key

Create `.env` file:
```bash
ANTHROPIC_API_KEY=your-key-here
```

### 3. Configure Settings

Edit `config.json`:
```json
{
  "directories": {
    "transcripts": "./transcripts",
    "outputs": "./outputs"
  },
  "templates": {
    "youtube_description": "./youtube_description_template.txt",
    "newsletter_examples": "./newsletter_examples.md"
  },
  "api": {
    "model": "claude-sonnet-4-20250514",
    "watch_interval": 10
  },
  "slack": {
    "enabled": false
  }
}
```

### 4. Install Launch Agent (Optional but Recommended)

```bash
./install_launch_agent.sh
```

This sets up automatic processing when you drop files into `./transcripts/`

### 5. Test It

```bash
# Copy sample to trigger processing
cp sample_transcript.txt transcripts/
```

## 📖 How It Works

1. **Drop** a transcript file (.txt, .md, or .json) into `./transcripts/`
2. **Select** your preferred title (via Slack or CLI)
3. **Get** organized outputs in `./outputs/[episode_name]/`:
   - `SELECTED_TITLE.txt` - Your chosen title
   - `youtube_description.txt` - Complete description with timestamps
   - `newsletter_article.txt` - Markdown-formatted newsletter
   - `keywords.txt` - SEO keywords
   - `description_components.txt` - Raw AI components

## 🤖 Slack Integration (Optional)

Get mobile notifications and respond from anywhere.

**Setup:**
1. Follow `SLACK_SETUP_GUIDE.md` to create a Slack app
2. Add credentials to `config.json`
3. Test: The system will send title options to Slack and wait for your response

**Benefits:**
- Respond from your phone
- All messages threaded per episode
- Visual progress updates
- Error notifications

See `SLACK_SETUP_GUIDE.md` for detailed setup.

## 🚀 Launch Agent (macOS)

Automatically process transcripts when files are added - no manual start needed.

**Install:**
```bash
./install_launch_agent.sh
```

**Manage:**
```bash
# Check status
launchctl list | grep firstcup

# Restart after code changes
launchctl unload ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
launchctl load ~/Library/LaunchAgents/com.productcoffee.firstcup.plist

# View logs
tail -f logs/processor_stdout.log
tail -f logs/processor_stderr.log
```

See `LAUNCH_AGENT_GUIDE.md` for details.

## 🎨 Customization

### Templates

Edit `youtube_description_template.txt` to customize your YouTube descriptions:
- Add your branding and links
- Include sponsor mentions
- Customize CTAs
- Change formatting

See `TEMPLATE_GUIDE.md` for details.

### Newsletter Style

Add examples to `newsletter_examples.md` - the AI learns from your style and matches it.

### Prompts

Edit `youtube_processor.py` to adjust:
- Article length
- Number of title options
- Tone and style
- Output format

## 🎯 What You Get

### Title Options
5 SEO-optimized, viral-friendly titles under 60 characters each. Interactive selection with:
- Choose from 1-5
- Type `f` + feedback to generate new options
- Type `TITLE: Your Custom Title` to specify exactly what you want

### YouTube Description
- Engaging hook (2-3 sentences)
- Key topics with bullet points
- Chapter timestamps extracted from transcript
- Panelist information
- SEO keywords (comma-separated, no hashtags)
- Your custom branding (from template)

### Newsletter Article
- ~150 words, concise and punchy
- Formatted with **bold**, *italics*, and [hyperlinks]()
- Subject line included
- Follows style from `newsletter_examples.md`
- Header format: `☕️ First Cup: [Title]`

## 📁 Project Structure

```
first-cup-processor/
├── youtube_processor.py          # Main processor
├── slack_helper.py                # Slack integration
├── config.json                    # Configuration
├── .env                           # API keys
├── requirements.txt               # Dependencies
├── install_launch_agent.sh        # Auto-install script
├── run_processor.sh               # Launch Agent wrapper
├── com.productcoffee.firstcup.plist  # Launch Agent config
├── youtube_description_template.txt  # Description template
├── newsletter_examples.md         # Newsletter style examples
├── sample_transcript.txt          # Test file
├── transcripts/                   # Drop files here
├── outputs/                       # Processed results
├── logs/                          # Application logs
├── SLACK_SETUP_GUIDE.md          # Slack setup walkthrough
├── LAUNCH_AGENT_GUIDE.md         # Launch Agent details
└── TEMPLATE_GUIDE.md             # Template customization
```

## 🆘 Troubleshooting

### Launch Agent Not Triggering
```bash
# Check if running
launchctl list | grep firstcup

# Check logs for errors
tail -50 logs/processor_stderr.log

# Restart
launchctl unload ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
launchctl load ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
```

### Slack Not Responding
- Verify bot is invited to channel: `/invite @First Cup Processor`
- Check `config.json` has correct tokens and channel ID
- Ensure `slack.enabled` is `true`
- Test connection (test feature in code)

### Module Not Found
```bash
# Use Anaconda Python (if installed)
/Users/jasonbrett/anaconda3/bin/python3 -m pip install anthropic requests

# Or system Python
pip3 install anthropic requests
```

### API Key Not Found
Ensure `.env` file exists with:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## 🔗 Documentation

- **`SLACK_SETUP_GUIDE.md`** - Complete Slack app setup
- **`LAUNCH_AGENT_GUIDE.md`** - Auto-trigger setup and management
- **`TEMPLATE_GUIDE.md`** - Customize description templates
- **`newsletter_examples.md`** - Add examples to improve AI output

## 📄 License

Copyright (C) 2025 Jason Brett

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
