# Interactive Title Selection Guide

## 🎯 New Feature: Interactive Title Selection

The script now pauses to let you review and approve titles before generating the description and newsletter!

---

## 🎬 How It Works

### 1. **Drop your transcript**
```bash
cp your-transcript.txt ~/youtube_transcripts/
```

### 2. **Script generates 5 titles**
The processor will automatically generate 5 title options focused on your First Cup panel discussion.

### 3. **You get this prompt:**
```
📝 Title Options:

  1. AI Agents: The Future of Productivity in 2025
  2. Why 2025 Is the Year AI Gets Autonomous
  3. Stop Using AI Tools Wrong (Here's the Right Way)
  4. The Agent Mindset: Next-Level AI Productivity
  5. AI Agents Will Transform Your Workflow (Ready?)

------------------------------------------------------------
Options:
  • Enter a number (1-5) to select that title
  • Enter 'f' to provide feedback and generate new titles
  • Enter 'q' to quit without processing
------------------------------------------------------------

Your choice: 
```

### 4. **Your Options:**

#### **Option A: Select a Title (Enter 1-5)**
```
Your choice: 3
✅ Selected: Stop Using AI Tools Wrong (Here's the Right Way)

🔍 Confirm this title? (y/n): y
```

The script then generates the description and newsletter based on your chosen title.

#### **Option B: Request New Titles (Enter 'f')**
```
Your choice: f

💬 Provide feedback for title generation:
   (e.g., 'Focus more on AI', 'Make it more specific', 'Too generic')

Feedback: Make it more specific to productivity and business use cases

🔄 Generating new titles based on your feedback...

📝 Title Options:

  1. 5 Ways AI Agents Boost Business Productivity in 2025
  2. AI Agents for Busy Entrepreneurs: Automate Your Workflow
  3. Business Productivity Revolution: AI Agents Explained
  4. How AI Agents Save Business Owners 10+ Hours Weekly
  5. The Entrepreneur's Guide to AI Agent Productivity
```

You can iterate as many times as you want!

#### **Option C: Cancel (Enter 'q')**
```
Your choice: q
❌ Processing cancelled.
```

The file won't be marked as processed, so you can try again later.

---

## 💡 Feedback Examples

### **Make it more specific:**
- "Focus on the technical aspects"
- "Make it more beginner-friendly"
- "Target business owners"
- "Emphasize cost savings"

### **Change the tone:**
- "Make it more clickbaity"
- "More professional and serious"
- "Add urgency"
- "Use a question format"

### **Adjust the focus:**
- "Focus on the panel's key takeaway"
- "Highlight the controversy discussed"
- "Emphasize practical applications"
- "Make it about the specific industry mentioned"

### **Fix specific issues:**
- "Too long, under 50 characters"
- "Too vague, be more specific"
- "Include the word 'automation'"
- "Don't use the word 'revolution'"

---

## 🔄 Iteration Strategy

### **First Round:**
Let Claude give you its best shot without guidance.

### **Second Round (if needed):**
Provide specific feedback like:
- "More focus on [specific topic from transcript]"
- "Target [specific audience]"
- "Use [specific keyword]"

### **Third Round (if needed):**
Get even more specific:
- "Combine the style of option 2 with the focus of option 4"
- "Make it shorter but keep the curiosity gap"

---

## 📊 What Happens After You Select

Once you confirm a title:

1. **Description generated** - Aligned with your chosen title
2. **Newsletter written** - Supports the chosen title
3. **Files saved**:
   - `SELECTED_TITLE.txt` - Your chosen title
   - `youtube_description.txt` - Description with timestamps
   - `newsletter_article.txt` - Newsletter content
   - `full_response.txt` - Complete output

---

## ⚡ Quick Tips

### **First Cup Specific:**
The prompts are now tuned for First Cup format:
- Titles focus ONLY on the panel discussion (not the teaser)
- Description includes teaser in timestamps but doesn't elaborate on it
- Newsletter is purely about the panel discussion

### **Speed Up Selection:**
- If the first batch is good, just pick one quickly (enter 1-5)
- Use feedback sparingly - Claude is already pretty good!

### **Cost Consideration:**
- Each title generation: ~$0.05
- Description + Newsletter: ~$0.15
- Total even with 2-3 iterations: Still under $0.30/episode

### **Batch Processing:**
The script processes files one at a time, waiting for your input on each. If you have multiple transcripts, they'll queue up.

---

## 🛠️ Advanced Usage

### **Want to skip interaction for testing?**
You can't fully skip it with this version, but you can:
1. Always pick option 1
2. Press 'y' to confirm

Takes 2 seconds per file.

### **Want Slack integration instead?**
Let me know! Slack would allow you to:
- Get title options sent to Slack
- Reply with your choice
- Fully async (no need to be at terminal)

But requires:
- Slack app setup
- Bot token
- Webhook configuration

**Trade-off**: More setup, but can respond from phone/anywhere.

---

## 🎯 Workflow Comparison

### **Old Workflow (Automatic):**
```
Drop file → Wait 30s → Get all outputs
```
- Fast
- No control over titles
- Might need to manually rewrite

### **New Workflow (Interactive):**
```
Drop file → Review titles → Give feedback (optional) → Select → Get outputs
```
- 2-3 minutes per file
- Full control over titles
- Description/newsletter align with chosen title
- No need to rewrite later

---

## ✅ Example Session

```bash
$ python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs

👀 Watching directory: /Users/you/youtube_transcripts
📁 Output directory: /Users/you/youtube_outputs
⏱️  Checking every 10 seconds...

🔔 Waiting for transcript files (.txt, .md, .json)...


📄 Processing: episode_24_transcript.txt
  Transcript length: 15234 characters

============================================================
TITLE SELECTION
============================================================

  Generating titles from Claude API...

📝 Title Options:

  1. First Cup: AI Agents Change Everything in 2025
  2. The AI Agent Revolution Panel Discussion
  3. Stop Using AI Like It's 2024 (First Cup Panel)
  4. AI Agents: From Tools to Teammates | First Cup
  5. First Cup Panel: Your AI Future Starts Now

------------------------------------------------------------
Options:
  • Enter a number (1-5) to select that title
  • Enter 'f' to provide feedback and generate new titles
  • Enter 'q' to quit without processing
------------------------------------------------------------

Your choice: f

💬 Provide feedback for title generation:
   (e.g., 'Focus more on AI', 'Make it more specific', 'Too generic')

Feedback: Less generic, focus on the productivity angle for business owners

🔄 Generating new titles based on your feedback...

📝 Title Options:

  1. How AI Agents Save Business Owners 10 Hours Weekly
  2. Automate Your Business: AI Agents Panel Discussion
  3. First Cup: AI Productivity Secrets Business Owners Need
  4. Business Automation Panel: AI Agents for Entrepreneurs
  5. Stop Wasting Time: AI Agent Productivity for Business

------------------------------------------------------------
Options:
  • Enter a number (1-5) to select that title
  • Enter 'f' to provide feedback and generate new titles
  • Enter 'q' to quit without processing
------------------------------------------------------------

Your choice: 1

✅ Selected: How AI Agents Save Business Owners 10 Hours Weekly

🔍 Confirm this title? (y/n): y

  📝 Generating description and newsletter...
  ✓ Response received (3421 chars)
  ✓ Outputs saved to: /Users/you/youtube_outputs/episode_24_transcript_20241026_153022

  ✅ Complete!
```

---

## 🆘 Troubleshooting

**Script seems stuck?**
- It's waiting for your input! Check the terminal.

**Want to cancel?**
- Press 'q' when prompted for title selection
- Or press Ctrl+C to stop the entire script

**Made a mistake?**
- No worries! Delete the file from `.processed_transcripts.json`
- Drop the transcript again

**Costs too much to iterate?**
- Consider switching to Haiku model for title generation (90% cheaper)
- Keep Sonnet for final description/newsletter

---

## 🎉 You're Ready!

The interactive mode gives you full control while still automating 90% of the work.

Try it out:
```bash
python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
```

Drop a transcript and watch the magic happen! ✨