# Quick Reference Card

## 🚀 Getting Started (30 seconds)

```bash
# Option 1: Auto-setup (recommended)
./setup.sh

# Option 2: Manual
export ANTHROPIC_API_KEY='your-key'
pip install anthropic --break-system-packages
mkdir -p ~/youtube_transcripts ~/youtube_outputs
python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
```

---

## 📂 File Locations

- **Drop transcripts here**: `~/youtube_transcripts/`
- **Get outputs here**: `~/youtube_outputs/`
- **Processed file tracker**: `~/youtube_outputs/.processed_transcripts.json`

---

## 🎬 Daily Usage

### Process a transcript:
1. Drop `.txt` file in `~/youtube_transcripts/`
2. Wait ~30 seconds
3. Find results in `~/youtube_outputs/episode_name_timestamp/`

### Reprocess a file:
```bash
# Remove from processed list
nano ~/youtube_outputs/.processed_transcripts.json
# Delete the filename entry, save, and drop file again
```

---

## 🔧 Common Commands

### Start the watcher:
```bash
python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
```

### Run in background (screen):
```bash
screen -S youtube
python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
# Press Ctrl+A then D to detach
```

### Reattach to background process:
```bash
screen -r youtube
```

### Stop the watcher:
Press `Ctrl+C` in the terminal

---

## 🛠️ Customization

### Change title count (5 → 10):
Edit `youtube_processor.py` line ~60:
```python
1. TITLE OPTIONS (10 options)  # was: (5 options)
```

### Change newsletter length:
Edit `youtube_processor.py` line ~85:
```python
Write a 400-500 word newsletter article  # was: 200-300
```

### Use cheaper model (Haiku):
Edit `youtube_processor.py` line ~98:
```python
model="claude-haiku-3-5-20241022",  # was: claude-sonnet-4
```

### Use best model (Opus):
```python
model="claude-opus-4-20250514",  # was: claude-sonnet-4
```

---

## 💰 Cost Check

View usage:
```
https://console.anthropic.com/settings/usage
```

Typical costs:
- Sonnet 4.5: $0.20/episode
- Haiku 3.5: $0.02/episode (90% cheaper, slightly lower quality)
- Opus 4: $0.60/episode (3x cost, highest quality)

---

## 🐛 Troubleshooting Quick Fixes

### Files not processing:
```bash
# Check if script is running
ps aux | grep youtube_processor

# Check file permissions
ls -la ~/youtube_transcripts/

# View processed files list
cat ~/youtube_outputs/.processed_transcripts.json

# Delete processed list to reprocess
rm ~/youtube_outputs/.processed_transcripts.json
```

### API key issues:
```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Set temporarily
export ANTHROPIC_API_KEY='sk-ant-...'

# Set permanently (add to ~/.bashrc)
echo "export ANTHROPIC_API_KEY='sk-ant-...'" >> ~/.bashrc
source ~/.bashrc
```

### Module not found:
```bash
pip install anthropic --break-system-packages
```

### Check API usage:
Visit: https://console.anthropic.com/settings/usage

---

## 📊 Output Files Explained

Each transcript creates a folder with:

- **`titles.txt`** → Choose your favorite
- **`youtube_description.txt`** → Copy to YouTube
- **`newsletter_article.txt`** → Use in email
- **`full_response.txt`** → Reference/archive

---

## 🔄 Workflow Integration Ideas

### Auto-upload to YouTube:
Use n8n workflow + YouTube API node

### Email newsletter:
Connect to Mailchimp/ConvertKit API

### Social posts:
Add X (Twitter) and LinkedIn API calls

### Archive:
Send to Notion, Airtable, or Google Drive

---

## ⚡ Performance Tips

1. **Batch process**: Drop multiple files at once
2. **Use Haiku**: 90% cheaper for drafts, then refine with Sonnet
3. **Cache prompts**: Enable prompt caching in API (90% off repeated prompts)
4. **Process during off-peak**: No difference in quality, just good practice

---

## 📖 Documentation Files

- **`README.md`** → Overview and quick start
- **`SETUP_GUIDE.md`** → Complete setup instructions
- **`COMPARISON.md`** → Choose between Python vs n8n
- **`QUICK_REFERENCE.md`** → This file (common commands)

---

## 🆘 Get Help

1. Check `SETUP_GUIDE.md` troubleshooting section
2. Check Claude API docs: https://docs.anthropic.com
3. Verify API key: https://console.anthropic.com
4. Check usage/billing: https://console.anthropic.com/settings/usage

---

## 🎯 Pro Tips

- **Test first**: Use `sample_transcript.txt` before your real content
- **Iterate prompts**: Refine based on your actual output needs
- **Monitor costs**: Check console after first few runs
- **Start simple**: Don't over-customize until you know what you want
- **Save good prompts**: Keep versions that work well

---

## 🔐 Security Notes

- Never commit API key to git
- Use environment variables for API key
- Don't share `.processed_transcripts.json` (contains filenames)
- Keep outputs directory private if content is sensitive

---

## ⏰ Scheduled Processing (Optional)

### Using cron (runs at 9 AM daily):
```bash
crontab -e
# Add:
0 9 * * * cd /path/to/script && python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
```

### Using systemd (always running):
See `SETUP_GUIDE.md` for full systemd service setup

---

## 📞 Support Resources

- Anthropic Console: https://console.anthropic.com
- API Docs: https://docs.anthropic.com
- Pricing: https://anthropic.com/pricing
- Rate Limits: https://docs.anthropic.com/en/api/rate-limits

---

## ✅ Checklist

- [ ] API key obtained and set
- [ ] Dependencies installed
- [ ] Directories created
- [ ] Test with sample transcript
- [ ] Customize prompts (optional)
- [ ] Process first real transcript
- [ ] Set up background running (optional)
- [ ] Monitor costs after first week

---

**Remember**: Start simple, test with sample, then customize as needed!

---

## 📄 License

Copyright (C) 2025 Jason Brett

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.