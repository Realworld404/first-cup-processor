# YouTube Description Template Guide

## 🎯 Overview

The script now uses a customizable template file for YouTube descriptions, allowing you to maintain consistent branding and easily update boilerplate content.

---

## 📝 Template File

### Location Options:

1. **In your transcripts folder**: `~/youtube_transcripts/youtube_description_template.txt`
2. **In the current directory**: `./youtube_description_template.txt`
3. **Custom path**: Specify as third argument when running the script

### Template File: `youtube_description_template.txt`

The template uses placeholders that are automatically replaced with AI-generated content:

- `{{HOOK}}` - Engaging 2-3 sentence intro
- `{{KEY_TOPICS}}` - Bullet points of topics covered
- `{{TIMESTAMPS}}` - Chapter markers with timestamps
- `{{KEYWORDS}}` - Comma-separated keywords (NO hashtags)

---

## 🎨 Customizing Your Template

### Edit `youtube_description_template.txt`:

```
{{HOOK}}

{{KEY_TOPICS}}

⏱️ TIMESTAMPS:
{{TIMESTAMPS}}

---

🎙️ ABOUT FIRST CUP:
First Cup is our weekly panel discussion where we dive deep into the latest trends in [YOUR NICHE]. Join us every [DAY] at [TIME]!

👥 TODAY'S PANELISTS:
• [Panelist 1] - [Title]
• [Panelist 2] - [Title]
• [Panelist 3] - [Title]

🔗 LINKS & RESOURCES:
• Website: https://yoursite.com
• Newsletter: https://yoursite.com/newsletter
• Community: https://discord.gg/your-invite

📱 CONNECT WITH US:
• Twitter: @yourhandle
• LinkedIn: /company/yourcompany
• Instagram: @yourhandle

💬 What's your take? Drop a comment!

👍 If you enjoyed this:
• Give us a thumbs up
• Subscribe for weekly episodes
• Share with a friend

🎯 NEXT EPISODE:
Coming next week: [Preview next episode topic]

---

#FirstCup #YourBrand

Keywords: {{KEYWORDS}}
```

---

## 🔧 What Gets Replaced

### `{{HOOK}}`
AI generates an engaging 2-3 sentence intro about the panel discussion topic.

**Example:**
```
Ever wonder how AI agents will reshape your business in 2025? In this First Cup panel, we explore the practical applications, real costs, and surprising limitations of AI automation. Our experts break down what's hype and what's actually working right now.
```

### `{{KEY_TOPICS}}`
AI generates 3-5 bullet points about what's discussed.

**Example:**
```
• The difference between AI tools and true AI agents
• Real-world cost analysis: When automation actually saves money
• Common mistakes businesses make when implementing AI
• Practical framework for deciding what to automate first
• The human skills that become MORE valuable with AI
```

### `{{TIMESTAMPS}}`
AI extracts timestamps from your transcript.

**Example:**
```
00:00 - Introduction
02:15 - Current State of AI Tools
05:30 - What Makes an Agent Different
09:45 - Real World Applications
14:20 - Technical Enablers
18:00 - Challenges We Still Face
22:15 - What to Expect in 2025
26:30 - Key Takeaway
28:45 - Transition to Main Session
```

### `{{KEYWORDS}}`
AI generates comma-separated keywords (no hashtags).

**Example:**
```
artificial intelligence, AI agents, business automation, productivity tools, workflow optimization, machine learning, automation strategy, digital transformation, AI implementation, business efficiency
```

---

## 📦 Output Files

After processing, you'll get:

### 1. `youtube_description.txt`
Your complete description with the template populated.

### 2. `keywords.txt`
Just the keywords, comma-separated (easy to copy/paste).

### 3. `description_components.txt`
The raw AI-generated components before template insertion (for reference/editing).

### 4. `SELECTED_TITLE.txt`
Your chosen title.

### 5. `newsletter_article.txt`
Newsletter content.

### 6. `full_response.txt`
Everything combined for reference.

---

## 🎬 Usage

### Option 1: Template in transcripts folder (automatic)
```bash
# Put template here:
cp youtube_description_template.txt ~/youtube_transcripts/

# Run normally:
python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
```

### Option 2: Template in current directory (automatic)
```bash
# Template in same folder as script
python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
```

### Option 3: Custom template path
```bash
python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs ~/path/to/my_custom_template.txt
```

---

## ✏️ Template Tips

### Keep Boilerplate Updated
Edit your template anytime to update:
- Social media links
- Panelist names
- Next episode teasers
- Call-to-action text
- Brand messaging

Changes apply to all future episodes automatically!

### Use Sections
Organize with clear sections:
- About the show
- Panelists
- Links & resources
- Social media
- CTA

### Include Brand Elements
Add your:
- Brand hashtags
- Catchphrases
- Sponsor mentions
- Affiliate links
- Course promotions

### Dynamic Content
You can manually edit the output files to add:
- Episode-specific guest info
- Special announcements
- Limited-time offers

---

## 🔄 Workflow

1. **One-time setup**: Customize `youtube_description_template.txt`
2. **Drop transcript**: File appears in watch folder
3. **Select title**: Interactive title selection
4. **Get output**: Description populated with your template
5. **Copy/paste**: Use generated description on YouTube
6. **Update template**: Edit template anytime, all future episodes use new version

---

## 📋 Template Checklist

When customizing your template, include:

- [ ] Show name and tagline
- [ ] Schedule (when new episodes drop)
- [ ] Panelist information (or space to customize per episode)
- [ ] All your links (website, newsletter, community)
- [ ] Social media handles
- [ ] Call-to-action
- [ ] Next episode teaser section
- [ ] Brand hashtags
- [ ] Keywords section with {{KEYWORDS}} placeholder
- [ ] All four placeholders: {{HOOK}}, {{KEY_TOPICS}}, {{TIMESTAMPS}}, {{KEYWORDS}}

---

## 🎨 Template Variations

### Minimal Template
```
{{HOOK}}

⏱️ CHAPTERS:
{{TIMESTAMPS}}

Subscribe for weekly episodes!

Keywords: {{KEYWORDS}}
```

### Detailed Template
```
{{HOOK}}

📋 WHAT WE COVER:
{{KEY_TOPICS}}

⏱️ TIMESTAMPS:
{{TIMESTAMPS}}

[Your extensive boilerplate here]

Keywords: {{KEYWORDS}}
```

### Custom Sections
Add your own sections that stay consistent:
```
{{HOOK}}

{{KEY_TOPICS}}

⏱️ TIMESTAMPS:
{{TIMESTAMPS}}

🎓 FREE RESOURCES:
Download our AI Implementation Guide: [link]

💼 SPONSOR:
This episode is brought to you by [Sponsor]

📚 RECOMMENDED READING:
• [Book 1]
• [Book 2]

Keywords: {{KEYWORDS}}
```

---

## 🚨 Important Notes

### Placeholder Names
Use EXACTLY these placeholder names:
- `{{HOOK}}`
- `{{KEY_TOPICS}}`
- `{{TIMESTAMPS}}`
- `{{KEYWORDS}}`

(Case-sensitive, double curly braces)

### Keywords Format
Keywords are now **comma-separated, NO hashtags**.

**OLD** ❌: `#AI #productivity #business`
**NEW** ✅: `AI, productivity, business automation, workflow`

This is better for YouTube's algorithm!

### Line Breaks
The template preserves your formatting, so:
- Use blank lines where you want spacing
- Structure sections with line breaks
- Add visual separators (---, ===, etc.)

---

## 🔧 Troubleshooting

### "Template not found" warning
The script will use a basic default template. To fix:
1. Create `youtube_description_template.txt`
2. Place it in your transcripts folder OR current directory
3. Or specify path: `python3 youtube_processor.py watch_dir output_dir /path/to/template.txt`

### Placeholders not replaced
Check spelling: `{{HOOK}}` not `{{Hook}}` or `{HOOK}`

### Want different format
Edit the template! The script just replaces placeholders - everything else is yours to customize.

### Update existing episodes
The template only affects NEW processed episodes. To reprocess:
1. Remove filename from `.processed_transcripts.json`
2. Drop transcript again

---

## 💡 Pro Tips

1. **Version control your template** - Keep it in git so you can revert changes
2. **A/B test CTAs** - Try different calls-to-action and track which performs better
3. **Seasonal updates** - Update for holidays, events, product launches
4. **Guest templates** - Create special templates for guest appearances
5. **Series templates** - Different templates for different content series

---

## 📊 Example Output

### Before Template (Raw AI Output):
```
HOOK: AI agents are transforming business...
KEY_TOPICS: • What makes agents different...
TIMESTAMPS: 00:00 - Introduction...
KEYWORDS: AI, automation, productivity...
```

### After Template (Final Output):
```
AI agents are transforming business in 2025. In this episode...

📋 WHAT WE COVER:
• What makes agents different from tools
• Real-world cost analysis
• Implementation strategies

⏱️ TIMESTAMPS:
00:00 - Introduction
05:30 - Agent Definition
[... your complete formatted description ...]

🔗 LINKS:
• Website: https://yoursite.com
• Newsletter: https://yoursite.com/subscribe

💬 Drop a comment with your thoughts!

Keywords: AI, automation, productivity, business tools, workflow
```

---

## ✅ Quick Start

1. **Download** `youtube_description_template.txt`
2. **Customize** with your links, branding, and boilerplate
3. **Place** in `~/youtube_transcripts/` folder
4. **Run** the processor as normal
5. **Enjoy** consistent, branded descriptions for every episode!

---

Questions? The template system is designed to be simple and flexible. Just edit the text file anytime!