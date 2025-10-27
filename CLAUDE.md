# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a YouTube transcript processor optimized for Product Coffee's "First Cup" panel discussion format. It uses Claude AI to generate SEO-optimized titles, descriptions, and newsletter articles.

### Core Components

**youtube_processor.py** - Main application with three execution modes:
1. **Watch mode** (default): Continuously monitors `./transcripts/` for new files
2. **Manual mode**: Process files without watching (triggered by Launch Agent)
3. **Test mode** (`--test-slack`): Verify Slack integration

**slack_helper.py** - Slack integration layer handling:
- Message threading (one thread per transcript)
- Interactive polling (waits indefinitely for user responses)
- Notification lifecycle (start → titles → selection → completion)

### Data Flow

```
Transcript file → Claude API → Parse response → Interactive title selection → Claude API (with title) → Save outputs
                                                  ↓ (if Slack enabled)
                                           Slack notification + polling
```

**Key architectural decisions:**
- Title selection happens BEFORE final processing (ensures description/newsletter align with chosen title)
- Slack uses `thread_ts` for conversation threading (not `last_message_ts`)
- Newsletter extraction uses regex with fallback patterns (Claude's response format can vary)
- Configuration split: secrets in `.env`, settings in `config.json`

### Prompt Engineering

The system uses a single mega-prompt in `create_prompt()` that generates all outputs in one API call:
- 5 title options (SEO-optimized, <60 chars)
- Description components (hook, topics, timestamps, panelists, keywords)
- Newsletter article (~150 words with markdown)

**Critical prompt requirements:**
- Newsletter MUST use markdown (`**bold**`, `*italics*`, `[links]()`)
- Plain text only for titles/description/keywords
- Current date context to prevent wrong year references
- Focus on First Cup panel (first ~25 min), not main session teaser

### Regex Parsing Gotchas

**Newsletter extraction** (lines 579-600):
- Primary pattern: `r'NEWSLETTER\s+ARTICLE:\s*(.*?)$'` (allows flexible spacing)
- Fallback pattern if primary fails
- **Do NOT strip markdown** - keep bold/italics/links intact
- Log extraction status for debugging intermittent failures

**Other extractions** use lookahead patterns to stop at next section header.

## Configuration & Secrets

**Security model (12-factor app):**
- `.env` = All secrets (API key, Slack tokens) - NEVER committed
- `config.json` = Settings only (paths, enabled flags) - Safe to commit
- Templates: `.env.template` and `config.json.template` for documentation

**Launch Agent setup:**
- `run_processor.sh` wrapper loads `.env` before executing
- Uses Anaconda Python (`/Users/jasonbrett/anaconda3/bin/python3`)
- Logs to `logs/stdout.log` and `logs/stderr.log`

## Development Commands

### Testing & Running

```bash
# Manual processing (one-time)
python3 youtube_processor.py

# Test Slack integration
python3 youtube_processor.py --test-slack

# Trigger via Launch Agent (drop file)
cp sample_transcript.txt transcripts/

# Check Launch Agent status
launchctl list | grep firstcup

# Restart after code changes
launchctl unload ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
launchctl load ~/Library/LaunchAgents/com.productcoffee.firstcup.plist

# View logs
tail -f logs/stderr.log  # Errors
tail -f logs/stdout.log  # Output
```

### Template Customization

**YouTube descriptions:** Edit `youtube_description_template.txt`
- Uses placeholders: `{{HOOK}}`, `{{KEY_TOPICS}}`, `{{TIMESTAMPS}}`, `{{KEYWORDS}}`

**Newsletter style:** Add examples to `newsletter_examples.md`
- AI learns from examples via few-shot learning
- More examples = better style matching

### Prompt Modifications

Edit `youtube_processor.py`:
- `create_prompt()` (line ~130): Main mega-prompt
- `get_titles_from_claude()` (line ~284): Title regeneration with feedback
- Look for "NEWSLETTER ARTICLE" section to adjust newsletter requirements

## Common Issues

**Blank newsletter articles:**
- Check `full_response.txt` to see raw Claude output
- Verify regex pattern matched (should see "✓ Newsletter article extracted" log)
- If extraction failed, response format may have changed

**Slack not responding to replies:**
- Ensure `poll_for_response()` uses `thread_ts` not `message_ts`
- Bot must be invited to channel: `/invite @First Cup Processor`
- Check scopes: `chat:write`, `channels:history`, `groups:history`

**Launch Agent not triggering:**
- Verify `.env` is loaded (check `run_processor.sh`)
- Ensure correct Python path in wrapper script
- Check `KeepAlive` is true in plist

## Code Modification Guidelines

**When modifying prompts:**
- Maintain clear section headers (TITLE OPTIONS, NEWSLETTER ARTICLE, etc.)
- Regex patterns depend on these headers - update both if changed
- Test with sample transcript after prompt changes

**When modifying Slack integration:**
- Always call `start_new_thread()` before processing new transcript
- Use `thread_ts` for threading, not `last_message_ts`
- Send all messages with `in_thread=True` except the first

**When adding new output files:**
- Add to `save_outputs()` function (line ~630)
- Follow naming pattern: lowercase with underscores
- Save to transcript-specific directory (not root outputs/)
