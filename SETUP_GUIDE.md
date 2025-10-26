# YouTube Transcript Processor - Setup Guide

## 🎯 Overview

This automation processes YouTube transcripts and generates:
1. **5 SEO-optimized, viral title options**
2. **YouTube description** with timestamps and chapters
3. **Newsletter article** with key takeaway and CTA

**Cost per episode**: ~$0.15-0.30 (Claude API only)

---

## Option 1: Claude Code Script (Recommended for Quick Start)

### Prerequisites
- Python 3.8+
- Claude API key from console.anthropic.com

### Setup Steps

1. **Install dependencies**:
```bash
pip install anthropic --break-system-packages
```

2. **Set up your API key**:
```bash
# Add to your ~/.bashrc or ~/.zshrc
export ANTHROPIC_API_KEY='your-api-key-here'

# Or set temporarily
export ANTHROPIC_API_KEY='sk-ant-...'
```

3. **Make the script executable**:
```bash
chmod +x youtube_processor.py
```

4. **Create directories**:
```bash
mkdir -p ~/youtube_transcripts
mkdir -p ~/youtube_outputs
```

5. **Run the watcher**:
```bash
python youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
```

The script will now watch the `~/youtube_transcripts` folder for any `.txt`, `.md`, or `.json` files.

### Usage

1. Drop a transcript file into `~/youtube_transcripts/`
2. The script automatically processes it
3. Outputs appear in `~/youtube_outputs/[filename]_[timestamp]/`
   - `titles.txt` - 5 title options
   - `youtube_description.txt` - Full description with timestamps
   - `newsletter_article.txt` - Newsletter content
   - `full_response.txt` - Complete Claude response

### Run as Background Service (Optional)

To keep it running 24/7:

```bash
# Using screen
screen -S youtube-processor
python youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
# Press Ctrl+A then D to detach

# To reattach later
screen -r youtube-processor
```

Or create a systemd service (Linux):

```bash
# Create service file
sudo nano /etc/systemd/system/youtube-processor.service
```

```ini
[Unit]
Description=YouTube Transcript Processor
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername
ExecStart=/usr/bin/python3 /path/to/youtube_processor.py /path/to/transcripts /path/to/outputs
Environment=ANTHROPIC_API_KEY=your-key-here
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable youtube-processor
sudo systemctl start youtube-processor
sudo systemctl status youtube-processor
```

---

## Option 2: n8n Workflow (Best for Full Automation)

### Prerequisites
- Docker installed
- Claude API key

### Setup Steps

1. **Install n8n with Docker**:
```bash
docker run -d --restart unless-stopped \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e ANTHROPIC_API_KEY='your-api-key-here' \
  n8nio/n8n
```

2. **Access n8n**:
   - Open browser to `http://localhost:5678`
   - Create an account on first launch

3. **Import the workflow**:
   - Click "Add workflow" → "Import from File"
   - Select `n8n_workflow.json`
   - The workflow will appear in your canvas

4. **Configure the workflow**:

   **a) Update the Watch Folder node**:
   - Click "Watch Transcript Folder" node
   - Change path to your transcript directory
   - Example: `/home/yourusername/youtube_transcripts`

   **b) Update output paths in Save nodes**:
   - Click each "Save..." node
   - Update the `filePath` to your desired output directory
   - Example: `/home/yourusername/youtube_outputs`

   **c) Set up API key** (if not using environment variable):
   - Click "Call Claude API" node
   - In the "Headers" section, update the x-api-key value
   - Or use n8n credentials manager:
     - Go to Settings → Credentials
     - Add "Header Auth" credential
     - Name: `x-api-key`
     - Value: Your Claude API key

5. **Activate the workflow**:
   - Toggle the switch in top right to "Active"
   - The workflow will now monitor the folder automatically

6. **Test it**:
   - Drop a transcript file in your watched folder
   - Check n8n's "Executions" tab to see processing
   - Find outputs in your configured output directory

### n8n Mobile Access (Optional)

Access from anywhere:
```bash
# Use ngrok for secure tunnel
ngrok http 5678
```

Or set up with a domain and SSL (recommended for production).

---

## 📝 Transcript Format

The processor accepts plain text transcripts in these formats:

### Simple Text
```
[Speaker talks about topic]
The main content of your show...
Discussion points...
```

### With Timestamps (Better for chapter detection)
```
00:00 - Introduction
Hi everyone, welcome to the show...

05:30 - Main Topic
Today we're discussing...

15:45 - Key Takeaway
The most important thing is...
```

### JSON Format
```json
{
  "transcript": "Your full transcript here...",
  "duration": "30:00",
  "speakers": ["Host", "Guest"]
}
```

---

## 🎛️ Customization

### Adjust the Prompt

Edit the prompt in either file to customize outputs:

**Python script**: Edit the `create_prompt()` function
**n8n workflow**: Edit the "Call Claude API" node's message content

### Example customizations:
- Change number of title options (5 → 10)
- Adjust newsletter length (200-300 words → 400-500 words)
- Add specific hashtag requirements
- Include sponsor mentions
- Add custom CTAs

### Change Claude Model

For cheaper processing (90% cost reduction):
- Change model from `claude-sonnet-4-20250514` to `claude-haiku-3-5-20241022`
- Trade-off: Slightly lower quality, but still very good

For higher quality:
- Use `claude-opus-4-20250514` (3x cost but best quality)

---

## 🔧 Troubleshooting

### Script Issues

**"No module named 'anthropic'"**:
```bash
pip install anthropic --break-system-packages
```

**"ANTHROPIC_API_KEY not set"**:
```bash
export ANTHROPIC_API_KEY='your-key'
# Add to ~/.bashrc to persist
```

**Files not processing**:
- Check file permissions: `ls -la ~/youtube_transcripts`
- Ensure files are .txt, .md, or .json
- Check `.processed_transcripts.json` - delete to reprocess files

### n8n Issues

**Can't access localhost:5678**:
```bash
docker ps  # Check if n8n is running
docker logs n8n  # Check for errors
docker restart n8n  # Restart if needed
```

**API errors**:
- Verify API key is correct
- Check Claude API dashboard for rate limits
- Ensure you have credits in your account

**No outputs created**:
- Check n8n Executions tab for errors
- Verify output directory paths exist and are writable
- Test with a small transcript first

---

## 💰 Cost Estimates

### Claude Sonnet 4.5
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

**Per 30-minute episode**:
- Transcript: ~5,000 tokens input
- Generated content: ~2,000 tokens output
- **Cost: $0.15-0.30 per episode**

**Monthly (4 episodes)**:
- $0.60-1.20/month

### Comparison
- Zapier + Claude: ~$25-30/month (minimum plan + API)
- n8n + Claude: ~$1/month (just API)
- **Savings: 95%+**

---

## 🚀 Next Steps

### Integrations to Add

1. **Auto-upload to YouTube**:
   - Use n8n YouTube node to auto-populate description
   - Requires YouTube API credentials

2. **Newsletter automation**:
   - Connect to Mailchimp, ConvertKit, or Substack API
   - Auto-draft or send newsletter

3. **Social media posts**:
   - Generate Twitter/X threads from key points
   - Create LinkedIn post variations
   - Instagram carousel copy

4. **Analytics tracking**:
   - Log which titles perform best
   - A/B test descriptions
   - Track newsletter click-through rates

5. **Archive to Notion/Airtable**:
   - Keep organized database of all content
   - Track performance metrics

### Example n8n Extended Workflow

```
Transcript File
    ↓
Process with Claude
    ↓
├─→ Save to files (current)
├─→ Upload to YouTube (auto-populate description)
├─→ Send to Mailchimp (draft newsletter)
├─→ Create Twitter thread
├─→ Log to Airtable (content database)
└─→ Notify via Slack (processing complete)
```

---

## 📚 Resources

- **Claude API Docs**: https://docs.anthropic.com
- **n8n Documentation**: https://docs.n8n.io
- **Prompt Engineering Guide**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- **Get API Key**: https://console.anthropic.com

---

## ✅ Quick Start Checklist

- [ ] Python 3.8+ installed (for script option)
- [ ] Anthropic API key obtained
- [ ] Dependencies installed (`pip install anthropic`)
- [ ] Environment variable set (`ANTHROPIC_API_KEY`)
- [ ] Transcript and output directories created
- [ ] Script tested with sample transcript
- [ ] Background service configured (optional)
- [ ] n8n installed (for automation option)
- [ ] Workflow imported and configured
- [ ] First transcript successfully processed

---

## 🎬 Ready to Process!

Drop your first transcript file and watch the magic happen. The AI will analyze your content and generate professional, optimized outputs in seconds.

Questions? Check the Troubleshooting section or the Claude API documentation.

---

## 📄 License

Copyright (C) 2025 Jason Brett

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.