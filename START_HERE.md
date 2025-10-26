# 🎬 START HERE - YouTube Transcript Processor

Welcome! You now have a complete automation system that will save you hours every week and cost less than $1/month.

## ✨ What This Does

Automatically transforms your YouTube transcripts into:
1. **5 viral-worthy title options** (SEO optimized, under 60 chars)
2. **Complete YouTube description** (hook, chapters with timestamps, CTAs, hashtags)
3. **Newsletter article** (200-300 words with key takeaway and CTA)

**Cost**: $0.15-0.30 per 30-minute episode (~$1/month for weekly show)

---

## 🚀 FASTEST Start (2 minutes)

```bash
# 1. Run the setup script
./setup.sh

# 2. That's it! The script will:
#    - Install dependencies
#    - Set up your API key
#    - Create directories
#    - Optionally test with sample transcript
```

### What You Need:
- Python 3.8+ (already have it? check: `python3 --version`)
- Anthropic API key → Get free at: https://console.anthropic.com
  - New users get $5 free credit (≈25 episodes!)

---

## 📚 Your Complete Package

### Core Files (Download All):
1. **`youtube_processor.py`** - The main automation script
2. **`setup.sh`** - One-command installation
3. **`requirements.txt`** - Dependencies list
4. **`sample_transcript.txt`** - Test file

### Documentation:
5. **`README.md`** - Overview and features
6. **`SETUP_GUIDE.md`** - Detailed setup and troubleshooting
7. **`COMPARISON.md`** - Choose Python vs n8n
8. **`QUICK_REFERENCE.md`** - Common commands cheat sheet

### Advanced Option:
9. **`n8n_workflow.json`** - For full automation (requires Docker)

---

## 🎯 Three-Step Start

### Step 1: Setup (2 minutes)
```bash
# Run this ONE command:
./setup.sh
```

### Step 2: Test (30 seconds)
The setup script will offer to process the sample transcript. Say yes!

### Step 3: Use It (ongoing)
```bash
# Drop your transcript files here:
~/youtube_transcripts/

# Get your results here:
~/youtube_outputs/
```

---

## 💡 Which Solution Should I Use?

### START WITH: Python Script (`youtube_processor.py`)
**Perfect for:**
- ✅ Weekly show (your use case!)
- ✅ Getting started quickly
- ✅ Easy customization
- ✅ Same cost as alternatives

**Later consider: n8n Workflow**
**When you want:**
- Auto-upload to YouTube
- Newsletter auto-sending
- Multiple shows
- Complex integrations

Both cost the same (~$1/month). Start simple!

---

## 📖 Read This Next

### If you want to start NOW:
1. Run `./setup.sh`
2. Test with sample
3. Drop your first real transcript

### If you want to understand everything first:
1. Read `README.md` (5 min overview)
2. Read `SETUP_GUIDE.md` (complete docs)
3. Check `COMPARISON.md` (Python vs n8n)

### If you want a cheat sheet:
- Open `QUICK_REFERENCE.md` for common commands

---

## 🎬 Real-World Workflow

### Your New Process:
**OLD WAY** (2+ hours):
1. Export transcript from YouTube
2. Brainstorm titles
3. Write description
4. Find timestamps manually
5. Write newsletter
6. Copy/paste everything

**NEW WAY** (30 seconds):
1. Drop transcript file
2. Get coffee ☕
3. Choose your favorite title
4. Copy outputs to YouTube/newsletter
5. Done!

---

## 💰 Cost Breakdown

### This Solution:
- Setup: **FREE**
- Monthly: **~$1** (just Claude API)
- Time saved: **2 hrs/week** = 104 hrs/year
- ROI: **Immediate** (if your time is worth >$0.01/hour 😄)

### Alternatives:
- Zapier + Claude: $25-30/month = $360/year 💸
- Zapier + OpenAI: $40-50/month = $600/year 💸💸
- Manual work: $0, but -104 hours ⏰

**You save $300-600/year vs alternatives!**

---

## 🔑 Get Your API Key

1. Visit: https://console.anthropic.com
2. Sign up (free)
3. Go to Settings → API Keys
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)
6. Keep it secret! Never share or commit to git

**New users get $5 free credit** ≈ 25 episodes!

---

## ⚡ Super Quick Start (TL;DR)

```bash
# 1. Get API key from console.anthropic.com
export ANTHROPIC_API_KEY='sk-ant-...'

# 2. Run setup
./setup.sh

# 3. Test
# (setup script will offer to test automatically)

# 4. Use it
cp your-transcript.txt ~/youtube_transcripts/
# Wait 30 seconds
ls ~/youtube_outputs/
```

---

## 🎯 First-Time Workflow

### Today:
1. **Run `./setup.sh`** (2 min)
2. **Test with sample** (included)
3. **Check outputs** (see what it creates)
4. **Read outputs** (verify quality)

### Tomorrow:
1. **Process your first real transcript**
2. **Use the outputs** (YouTube, newsletter)
3. **Tweak prompts if needed** (optional)

### Next Week:
1. **Drop transcripts as you create them**
2. **Enjoy your extra 2 hours** 🎉
3. **Check costs** (should be pennies)
4. **Consider n8n** if you want more automation

---

## 🛠️ Customization (Optional)

Once you're comfortable, you can:
- Change # of titles (5 → 10)
- Adjust article length (200-300 → 400-500 words)
- Add sponsor mentions
- Change tone/style
- Use cheaper model (Haiku) or best model (Opus)

All instructions in `SETUP_GUIDE.md`

---

## 🆘 Help & Support

### Something not working?
1. Check `SETUP_GUIDE.md` → Troubleshooting section
2. Check `QUICK_REFERENCE.md` → Common fixes
3. Visit https://docs.anthropic.com

### Want to customize?
1. Read `SETUP_GUIDE.md` → Customization section
2. Edit the prompt in `youtube_processor.py`

### Want full automation?
1. Read `COMPARISON.md` → n8n section
2. Import `n8n_workflow.json`

---

## 🎓 Learning Path

### Beginner (You are here):
- [ ] Run setup script
- [ ] Test with sample
- [ ] Process first real transcript
- [ ] Use outputs in production

### Intermediate (After 5-10 episodes):
- [ ] Customize prompts
- [ ] Set up background running
- [ ] Monitor and optimize costs
- [ ] Refine output quality

### Advanced (Optional):
- [ ] Deploy n8n workflow
- [ ] Add YouTube auto-upload
- [ ] Add newsletter auto-send
- [ ] Create social media posts
- [ ] Build content database

---

## ✅ Success Checklist

- [ ] Downloaded all files
- [ ] Have Python 3.8+ installed
- [ ] Got Anthropic API key
- [ ] Ran `./setup.sh`
- [ ] Tested with sample transcript
- [ ] Verified outputs look good
- [ ] Processed first real transcript
- [ ] Used outputs in production
- [ ] Checked cost in console
- [ ] Set up for recurring use

---

## 🎉 You're Ready!

Run this command and you're live:
```bash
./setup.sh
```

**Questions?** Everything is explained in `SETUP_GUIDE.md`

**Need quick help?** Check `QUICK_REFERENCE.md`

**Want to compare options?** Read `COMPARISON.md`

---

## 💪 What You've Gained

✅ Automated title generation (saves 15 min/episode)
✅ Automated description writing (saves 20 min/episode)  
✅ Automated newsletter article (saves 30 min/episode)
✅ Automated timestamp extraction (saves 15 min/episode)
✅ Professional-quality outputs (better than manual!)
✅ Total time saved: **90+ minutes per episode**

---

## 🚀 Ready, Set, Go!

```bash
./setup.sh
```

Welcome to the future of content creation! 🎬✨

---

**P.S.** Don't forget to check your API costs after the first week. You'll be amazed at how cheap this is!

---

## 📄 License

Copyright (C) 2025 Jason Brett

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.