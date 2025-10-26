# 🎬 YouTube Transcript Processor

Automatically process YouTube transcripts to generate SEO-optimized titles, descriptions, and newsletter articles using Claude AI.

**Cost**: ~$0.15-0.30 per 30-minute episode

## 📦 What's Included

### Core Files
- **`youtube_processor.py`** - Main Python script that watches for transcripts and processes them
- **`setup.sh`** - Automated setup script (recommended starting point)
- **`requirements.txt`** - Python dependencies
- **`SETUP_GUIDE.md`** - Complete documentation with troubleshooting

### n8n Workflow
- **`n8n_workflow.json`** - Import this into n8n for full automation

### Testing
- **`sample_transcript.txt`** - Example transcript to test the system

## 🚀 Quick Start (2 minutes)

### Option 1: Automated Setup (Recommended)

```bash
./setup.sh
```

This will:
1. Check Python installation
2. Install dependencies
3. Set up your API key
4. Create necessary directories
5. Optionally test with sample transcript

### Option 2: Manual Setup

```bash
# 1. Install dependencies
pip install anthropic --break-system-packages

# 2. Set API key
export ANTHROPIC_API_KEY='your-api-key-here'

# 3. Create directories
mkdir -p ~/youtube_transcripts ~/youtube_outputs

# 4. Run the processor
python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
```

## 📖 How It Works

1. **Drop** a transcript file (.txt, .md, or .json) into the watched folder
2. **Process** happens automatically via Claude API
3. **Get** organized outputs:
   - 5 title options
   - YouTube description with timestamps
   - Newsletter article
   - Full response for reference

## 🎯 What You Get

### 1. Title Options (5 choices)
SEO-optimized, viral-friendly titles under 60 characters

### 2. YouTube Description
- Compelling hook
- Key topics with bullet points
- Chapter timestamps
- Call-to-action
- Relevant hashtags

### 3. Newsletter Article
- Engaging 200-300 word summary
- One key takeaway
- CTA to drive YouTube views
- Suggested subject line

## 💰 Cost Comparison

| Solution | Monthly Cost | Setup Time |
|----------|-------------|------------|
| **This (n8n + Claude)** | ~$1 | 10 min |
| Zapier + OpenAI | $25-50 | 5 min |
| Zapier + Claude | $25-30 | 5 min |
| Manual work | $0 (+ 2 hrs/episode) | 0 min |

## 📁 File Structure

After processing, outputs are organized like this:

```
youtube_outputs/
└── episode_name_20241025_143022/
    ├── titles.txt
    ├── youtube_description.txt
    ├── newsletter_article.txt
    └── full_response.txt
```

## 🔧 Two Deployment Options

### Python Script (Simple)
- ✅ Works immediately
- ✅ No additional software needed
- ✅ Easy to customize
- ❌ Must keep terminal open (or use screen/systemd)

### n8n Workflow (Advanced)
- ✅ Fully automated background processing
- ✅ Visual workflow editor
- ✅ Easy to extend (add YouTube upload, email sending, etc.)
- ❌ Requires Docker
- ❌ Slight learning curve

## 📚 Documentation

See **`SETUP_GUIDE.md`** for:
- Detailed setup instructions
- Troubleshooting guide
- Customization options
- Integration ideas (YouTube auto-upload, newsletter automation, etc.)
- Cost optimization tips
- Running as background service

## 🎬 Example Output

Drop in a 30-minute show transcript and get outputs like:

**Titles**:
1. "AI Agents Are About to Change Everything (Here's How)"
2. "Why 2025 Is the Year of AI Agents | Productivity Revolution"
3. "Stop Using AI Wrong: The Agent Mindset Explained"

**Description** with timestamps:
```
00:00 - Introduction
02:15 - Current State of AI Tools
05:30 - What Makes Agents Different
...
```

**Newsletter** with hook, summary, and CTA to watch on YouTube.

## 🛠️ Customization

Edit the prompt in `youtube_processor.py` to:
- Change number of titles (5 → 10)
- Adjust article length (200-300 → 400-500 words)
- Add sponsor mentions
- Include specific hashtags
- Change tone/style

## 🆘 Troubleshooting

### "No module named 'anthropic'"
```bash
pip install anthropic --break-system-packages
```

### "API key not set"
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### Files not processing
- Check file extensions (.txt, .md, .json)
- Verify file permissions
- Check `.processed_transcripts.json` in output dir

More help in `SETUP_GUIDE.md`

## 🔗 Resources

- [Get Claude API Key](https://console.anthropic.com)
- [Claude API Docs](https://docs.anthropic.com)
- [n8n Documentation](https://docs.n8n.io)

## 📝 Requirements

- Python 3.8+
- Anthropic API key
- 10MB disk space

## 🎯 Next Steps

1. Run `./setup.sh` to get started
2. Test with `sample_transcript.txt`
3. Process your first real transcript
4. Read `SETUP_GUIDE.md` for advanced features
5. Consider setting up n8n for full automation

## 💡 Tips

- Start with the Python script to test
- Use sample transcript to verify everything works
- Gradually customize the prompts
- Consider n8n once you're comfortable
- Check costs in Anthropic console

---

**Questions?** Check `SETUP_GUIDE.md` or the Claude API docs.

**Ready?** Run `./setup.sh` and drop in your first transcript! 🚀

## 📄 License

Copyright (C) 2025 Jason Brett

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.