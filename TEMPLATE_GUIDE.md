# YouTube Description Template Guide

## Overview

Customize `youtube_description_template.txt` to maintain consistent branding across all episodes.

## Template Placeholders

The template uses placeholders automatically replaced with AI-generated content:

- `{{HOOK}}` - Engaging 2-3 sentence introduction
- `{{KEY_TOPICS}}` - Bullet points of topics covered
- `{{TIMESTAMPS}}` - Chapter markers with timestamps
- `{{KEYWORDS}}` - Comma-separated keywords (no hashtags)

## Configuration

Set the template path in `config.json`:

```json
{
  "templates": {
    "youtube_description": "./youtube_description_template.txt"
  }
}
```

## Example Template

```
{{HOOK}}

📋 WHAT WE COVER:
{{KEY_TOPICS}}

⏱️ TIMESTAMPS:
{{TIMESTAMPS}}

---

🎙️ ABOUT FIRST CUP:
Weekly panel discussion on product management trends.

🔗 LINKS:
• Website: https://productcoffee.com
• Newsletter: https://productcoffee.com/newsletter

💬 Join the conversation in the comments!

👍 Subscribe for weekly episodes

Keywords: {{KEYWORDS}}
```

## Output Files

After processing, you'll get:

- **`youtube_description.txt`** - Complete description with template populated
- **`keywords.txt`** - Keywords only (easy to copy/paste)
- **`description_components.txt`** - Raw AI components before template insertion
- **`SELECTED_TITLE.txt`** - Your chosen title
- **`newsletter_article.txt`** - Newsletter content

## Tips

- **Update anytime** - Changes apply to all future episodes automatically
- **Use sections** - Organize with clear headings for better readability
- **Include branding** - Add your links, CTAs, and brand elements
- **Test CTAs** - Try different calls-to-action to see what performs better

## Important Notes

- Use placeholder names **exactly** as shown (case-sensitive, double curly braces)
- Keywords should be comma-separated, **not hashtags**
  - ✅ `AI, productivity, business automation`
  - ❌ `#AI #productivity #business`
- The template preserves your formatting (blank lines, spacing, etc.)
