# 📚 Newsletter Examples - Few-Shot Learning Guide

## 🎯 What This Does

The `newsletter_examples.md` file teaches the AI your writing style through **few-shot learning**. By providing examples of your best newsletter articles, the AI learns to match:

- Your voice and tone
- Your writing style
- Your structure preferences
- How you use names and specifics
- Your level of detail

---

## 🚀 Quick Start

### 1. Place the Examples File

Put `newsletter_examples.md` in your transcripts folder:
```bash
cp newsletter_examples.md ~/youtube_transcripts/
```

Or in the same directory as your script (it auto-detects).

### 2. Add Your Examples

Edit `newsletter_examples.md` and add your best newsletter articles:

```markdown
## Example 1: Your Best Article

**Subject Line**: What Top PMs Are Really Doing with AI

Ever wonder what AI tools your fellow product managers...
[full article text]

**[Watch on YouTube →]**
```

### 3. Run Normally

The script automatically uses the examples:
```bash
python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
```

You'll see:
```
📚 Using newsletter examples for style matching
```

---

## 📝 How to Add Examples

### What Makes a Good Example?

Add newsletter articles that:
- ✅ Got great response/engagement
- ✅ Match your desired tone
- ✅ Have your ideal structure
- ✅ Use names and specifics well
- ✅ Have strong subject lines

### How Many Examples?

**Start with**: 1-3 examples
**Ideal**: 3-5 examples
**Maximum**: 5-10 examples

More isn't always better - quality over quantity!

### Where to Find Good Examples

Look for articles that:
- Had high open rates
- Got lots of replies/engagement
- You're particularly proud of
- Represent your best work
- Match the tone you want

---

## 📋 Example Template

Copy this structure for each example:

```markdown
## Example [NUMBER]: [Brief Description]

**Subject Line**: [Your actual subject line]

[Full article text - 200-300 words]
- Include the hook
- Include all paragraphs
- Include the key takeaway
- Include the CTA

**[Watch on YouTube →]**

---
```

---

## 🎨 What the AI Learns

### From Example 1 (AI Experiments):

**Style elements it learns**:
- Conversational opening with a question
- Use of specific names (Allison Herbert, Nandu Shah, Steve Johnson)
- Mix of excitement and balanced perspective
- Concrete examples with details
- Clear, single takeaway
- Simple CTA

**Subject line pattern**:
- Question + Parenthetical surprise
- "What... (Spoiler:...)"

**Structure**:
- Hook paragraph (question + preview)
- Body paragraph 1 (specific examples with names)
- Body paragraph 2 (contrarian/balanced view)
- Takeaway paragraph (actionable insight)
- CTA

---

## 💡 Pro Tips

### 1. Use Recent Examples
Your style evolves - use examples from the last 3-6 months.

### 2. Match Your Current Voice
Don't use old examples if your tone has changed.

### 3. Include Subject Lines
Subject lines are crucial! The AI learns your patterns.

### 4. Keep Full Articles
Don't edit or shorten - the AI needs complete examples.

### 5. Add Variety
Include examples with different:
- Subject line styles
- Opening hooks
- Key takeaway types
- CTAs

### 6. Update Regularly
Every few months:
- Remove examples that feel dated
- Add new favorites
- Keep your best 5-10

---

## 🔄 Workflow

### Initial Setup:
1. Create `newsletter_examples.md`
2. Add 2-3 of your best articles
3. Place in `~/youtube_transcripts/`

### After Each Episode:
If you love the newsletter output:
1. Copy it to `newsletter_examples.md`
2. Add as a new example
3. Remove oldest/weakest example if needed

### Monthly Review:
1. Read through your examples
2. Remove any that feel dated
3. Add recent favorites
4. Keep your top 5-10

---

## 📊 Before & After

### Without Examples:
```
Subject: Product Management Discussion

This week's episode covers product management 
topics. We discuss various aspects of the role 
and different perspectives on best practices.

Watch the full episode on YouTube.
```
❌ Generic, no personality, boring

### With Examples:
```
Subject: What Top PMs Are Really Doing with AI (Not What You Think)

Ever wonder what AI tools your fellow product 
managers are actually using behind the scenes? 
Our latest First Cup panel brought together 
seasoned PMs to share their real-world AI 
experiments – and the results might surprise you.

[Continues with specific examples, names, insights]

Watch the full discussion to hear specific tools...
```
✅ Engaging, specific, your voice

---

## 🎯 What to Include in Examples

### Must Have:
- ✅ Complete article (all paragraphs)
- ✅ Subject line
- ✅ Your best work
- ✅ Match desired tone

### Nice to Have:
- Notes on why it worked well
- Engagement metrics (if you track them)
- What made it special

### Don't Include:
- ❌ Examples you're not proud of
- ❌ Different styles you don't want to match
- ❌ Incomplete articles
- ❌ Heavily edited versions

---

## 🔍 Testing Impact

### Test 1: Without Examples
Process a transcript without the examples file.

### Test 2: With Examples
Add examples file and process another transcript.

### Compare:
- Does it match your voice better?
- Are names used more naturally?
- Is the structure more consistent?
- Do subject lines follow your patterns?

---

## 🛠️ Troubleshooting

### "No newsletter examples found"
```
ℹ️  No newsletter examples found at [path]
   Will generate newsletters without style examples
```
**Fix**: Copy `newsletter_examples.md` to `~/youtube_transcripts/`

### Not matching your style
- Add more examples (need at least 2-3)
- Ensure examples are consistent with each other
- Check that examples match your desired tone

### Output is too similar to examples
- This is rare, but if it happens:
- Reduce number of examples
- Use more varied examples
- The AI shouldn't copy - it should learn patterns

---

## 📈 Continuous Improvement

This file is a **living document**. Your writing evolves, so should your examples!

**Monthly routine**:
1. Review generated newsletters
2. Keep the best ones as examples
3. Remove dated/weak examples
4. Refine your style over time

**Result**: Every month, your automated newsletters get better at sounding like you!

---

## ✅ Quick Reference

**File location**: `~/youtube_transcripts/newsletter_examples.md`

**Format**: Markdown with examples

**Recommended**: 3-5 high-quality examples

**Update**: Monthly or after creating great content

**Impact**: AI matches your voice and style

---

## 🎉 You're Ready!

1. Edit `newsletter_examples.md`
2. Add 2-3 of your best articles
3. Place in transcripts folder
4. Process your next transcript
5. See the AI match your style!

The more you curate your examples, the better your automated newsletters will sound like you wrote them personally! 📝