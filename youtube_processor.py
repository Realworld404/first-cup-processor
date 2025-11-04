#!/usr/bin/env python3
"""
YouTube Transcript Processor
Watches a directory for new transcript files and automatically generates:
1. SEO-optimized title options
2. YouTube description with timestamps
3. Newsletter article

Supports Slack integration for interactive title selection and notifications.

Usage:
    python youtube_processor.py /path/to/transcripts /path/to/outputs
    python youtube_processor.py --test-slack  # Test Slack connection

TODO: Future Enhancement - Create macOS menubar app for drag-and-drop processing
      with visual status updates and quick access to outputs. Would provide:
      - Drag transcript file onto menubar icon to process
      - Live processing status in menubar
      - Click to view/copy outputs
      - Settings panel for configuration
"""

import os
import sys
import time
import json
import re
from pathlib import Path
from datetime import datetime
import anthropic

# Import Slack helper (optional - gracefully handles if not available)
try:
    from slack_helper import SlackHelper
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    print("⚠️  Slack integration not available (slack_helper.py not found)")

# Configuration - will be loaded from config.json
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
WATCH_INTERVAL = 10  # seconds between directory checks
PROCESSED_FILE = '.processed_transcripts.json'

def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "config.json"

    # Default configuration
    default_config = {
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
            "enabled": False,
            "webhook_url": "",
            "bot_token": "",
            "user_id": ""
        }
    }

    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        except Exception as e:
            print(f"⚠️  Error loading config.json: {e}")
            print(f"   Using default configuration")
            return default_config
    else:
        print(f"⚠️  config.json not found, using default configuration")
        return default_config

def to_title_case(text):
    """Convert text to proper title case with smart handling of common words"""
    # Words that should be lowercase in titles (unless first/last word)
    lowercase_words = {
        'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'of',
        'on', 'or', 'the', 'to', 'with', 'vs', 'via'
    }

    words = text.split()
    if not words:
        return text

    result = []
    for i, word in enumerate(words):
        # First and last words are always capitalized
        if i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        # Check if word should be lowercase
        elif word.lower() in lowercase_words:
            result.append(word.lower())
        else:
            result.append(word.capitalize())

    return ' '.join(result)

def load_processed_files(output_dir):
    """Load list of already processed files"""
    processed_file = Path(output_dir) / PROCESSED_FILE
    if processed_file.exists():
        with open(processed_file, 'r') as f:
            return json.load(f)
    return []

def save_processed_file(output_dir, filename):
    """Mark a file as processed"""
    processed_file = Path(output_dir) / PROCESSED_FILE
    processed = load_processed_files(output_dir)
    if filename not in processed:
        processed.append(filename)
        with open(processed_file, 'w') as f:
            json.dump(processed, f, indent=2)

def create_prompt(transcript, newsletter_examples=None):
    """Create the mega-prompt for Claude"""

    # Get current date for context
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_year = datetime.now().year

    # Add newsletter examples if provided
    examples_section = ""
    if newsletter_examples:
        examples_section = f"""

NEWSLETTER WRITING EXAMPLES:
Below are examples of high-quality newsletter articles in the desired style and tone. Study these examples and match this style when creating the newsletter article.

{newsletter_examples}

Use these examples to understand:
- The conversational, engaging tone
- How to use specific names and examples
- The structure and flow
- Subject line patterns
- How to create curiosity and value
"""

    return f"""Analyze this YouTube show transcript and create three deliverables:

CURRENT DATE CONTEXT:
Today's date is {current_date}. The current year is {current_year}. DO NOT reference years like 2024 unless they are explicitly mentioned in the transcript. When discussing current trends or future predictions, use the correct year ({current_year}) or say "this year" instead of assuming 2024.

IMPORTANT CONTEXT ABOUT THE SHOW FORMAT:
This is "First Cup" - a panel discussion show. The main content (approximately the first 25 minutes) is a panel discussion on a specific topic. In the last ~5 minutes, there is a transition/teaser for the main session that follows.

CRITICAL INSTRUCTIONS:
- The TITLES should focus ONLY on the First Cup panel discussion topic (first 25 minutes)
- The DESCRIPTION should focus ONLY on the First Cup panel discussion
- The teaser/transition to the main session should be included in the timestamps section but should NOT be described in the main description text or key topics
- The NEWSLETTER should focus ONLY on the First Cup panel discussion
- For TITLES, DESCRIPTION, and KEYWORDS: Use plain text only (NO markdown formatting)
- For NEWSLETTER ARTICLE: Use full markdown formatting including hyperlinks (see specific instructions below)

TRANSCRIPT:
{transcript}
{examples_section}

DELIVERABLES:

1. TITLE OPTIONS (5 options)
Create 5 title options that are:
- Keyword-rich for SEO
- Optimized for virality (curiosity gap, emotional trigger, or bold claim)
- Under 60 characters
- Focused ONLY on the First Cup panel discussion topic (NOT the teaser/main session at the end)
- Accurately represent the panel discussion content

Format each on a new line as:
TITLE 1: [title]
TITLE 2: [title]
TITLE 3: [title]
TITLE 4: [title]
TITLE 5: [title]

2. YOUTUBE DESCRIPTION COMPONENTS
Generate these components separately (they will be inserted into a template):

A) HOOK (2-3 engaging sentences that create curiosity about the PANEL DISCUSSION)
Format: Start with "HOOK:" then the text
IMPORTANT: Use plain text only - NO markdown formatting like ** or __

B) KEY TOPICS (3-5 bullet points about what's covered in the PANEL DISCUSSION ONLY)
Format: Start with "KEY_TOPICS:" then list each topic on a new line with "• " prefix
Do NOT describe the teaser/main session content
IMPORTANT: Use plain text only - NO markdown formatting

C) TIMESTAMPS (Chapter markers with exact timestamps)
Format: Start with "TIMESTAMPS:" then list timestamps like:
00:00 - Introduction
05:23 - [Panel discussion topic name]
12:45 - [Panel discussion topic name]
25:00 - [Create an enticing teaser about the main session - extract the most interesting/compelling topic or guest from that section]
[Include ALL timestamps from the transcript]

IMPORTANT for the LAST timestamp (main session teaser):
- DO NOT just say "Transition to Main Session" or "Main Session Begins"
- Extract something SPECIFIC and INTERESTING from the main session portion
- Make it enticing so viewers want to watch through to the end
- Examples: "25:00 - Why 87% of AI Projects Fail (Main Session Preview)"
- Examples: "26:30 - Special Guest: Sarah Chen on Enterprise AI Strategy"
- Examples: "25:15 - The Controversial Take That Changes Everything"

D) PANELISTS (List of panelists who participated in this episode)
Format: Start with "PANELISTS:" then list each panelist with their name and title/company:
• [Name] - [Title/Company or brief description]
• [Name] - [Title/Company or brief description]
Extract this information from the transcript. If titles/companies aren't mentioned, just use their names.

E) KEYWORDS (5-10 relevant keywords, comma-separated, NO hashtags)
Format: Start with "KEYWORDS:" then comma-separated keywords on ONE LINE
Example: artificial intelligence, productivity, business automation, AI agents, workflow optimization
These should be SEO-relevant keywords for the PANEL DISCUSSION topic only.
IMPORTANT: Put ALL keywords on a single line, comma-separated, with NO extra text or numbering after

3. NEWSLETTER ARTICLE
Write a ~150 word newsletter article.

CRITICAL FIRST LINE FORMAT:
The article MUST start with this EXACT format:
☕️ First Cup: [selected title]

For example, if the selected title is "Why Product Managers Fail", the first line must be:
☕️ First Cup: Why Product Managers Fail

DO NOT write just the title alone. DO NOT skip the "☕️ First Cup:" prefix. This prefix is MANDATORY.

Article requirements:
- First line: ☕️ First Cup: [selected title] (MANDATORY - do not skip this!)
- Recaps the First Cup panel discussion segment
- Includes context about the topic/prompt discussed
- Highlights key discussion points with specific examples
- Features ONE compelling quote from a panelist when possible (use actual names)
- Presents contrasting perspectives when they occurred
- Ends with a clear, actionable key takeaway
- Includes a CTA to watch the full video on YouTube with a hyperlink
- Uses a conversational, engaging tone
{f"- IMPORTANT: Match the style, tone, and structure shown in the newsletter examples above" if newsletter_examples else ""}

MARKDOWN FORMATTING REQUIREMENTS for newsletter article (MANDATORY):
You MUST use full markdown formatting in the newsletter article. This is REQUIRED, not optional.

REQUIRED MARKDOWN ELEMENTS:
1. **Bold text** - Use for:
   - Panelist names on first mention (e.g., **Steve Johnson**)
   - Key terms and concepts (e.g., **product mindset**, **ZIRP-era**)
   - Important phrases (e.g., **progress, not sacrilege**)
   - At least 3-5 bold items throughout the article

2. *Italic text* - Use for:
   - Direct quotes from panelists (e.g., *"We shouldn't keep adding to the plate"*)
   - Emphasis on specific words (e.g., *real reactions*, *test strategy*)
   - At least 2-3 italic items

3. Hyperlinks - REQUIRED, use for:
   - YouTube video: [Watch the full discussion]({{YOUTUBE_URL}}) or [Watch it here]({{YOUTUBE_URL}})
   - Company names: [Company Name](https://company.com)
   - Products/tools: [Product Name](https://product.com)
   - Panelist names if they're public figures with LinkedIn

EXAMPLE OUTPUT FORMAT:
"This week's First Cup tackled **Figma Make** and instant prototyping. **Valerie King** says it's *progress, not sacrilege*—but only if teams align first. [Watch the full discussion]({{YOUTUBE_URL}})."

DO NOT output plain text - you must include **bold**, *italics*, and [hyperlinks]().

CRITICAL: Keep the article to approximately 150 words. Be concise and punchy.

Start this section with "NEWSLETTER ARTICLE:" header.

CRITICAL FORMATTING REMINDERS:
- Use markdown formatting ONLY in the NEWSLETTER ARTICLE section
- For TITLES, DESCRIPTION, and KEYWORDS: use plain text only (NO markdown)
- Keywords must be on ONE line only, comma-separated
- Do not add extra numbering or text after the keywords line

Please format your response with clear section headers so outputs can be easily parsed."""

def get_titles_from_claude(transcript, api_key, feedback=None, newsletter_examples=None):
    """Get title options from Claude, optionally with feedback for iteration"""
    client = anthropic.Anthropic(api_key=api_key)

    # Get current date for context
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_year = datetime.now().year

    if feedback:
        prompt = f"""Based on this transcript, generate 5 NEW title options incorporating this feedback:

CURRENT DATE CONTEXT:
Today's date is {current_date}. The current year is {current_year}. DO NOT reference 2024 unless explicitly in the transcript. Use {current_year} or "this year" for current/future references.

FEEDBACK: {feedback}

TRANSCRIPT:
{transcript}

IMPORTANT CONTEXT:
This is "First Cup" - a panel discussion show. Focus ONLY on the panel discussion topic (first ~25 minutes), NOT the teaser at the end.

Create 5 NEW title options that are:
- Keyword-rich for SEO
- Optimized for virality (curiosity gap, emotional trigger, or bold claim)
- Under 60 characters
- Focused ONLY on the First Cup panel discussion topic
- Address the feedback provided above

Format each on a new line as:
TITLE 1: [title]
TITLE 2: [title]
TITLE 3: [title]
TITLE 4: [title]
TITLE 5: [title]"""
    else:
        prompt = f"""Analyze this transcript and create 5 title options:

CURRENT DATE CONTEXT:
Today's date is {current_date}. The current year is {current_year}. DO NOT reference 2024 unless explicitly in the transcript. Use {current_year} or "this year" for current/future references.

TRANSCRIPT:
{transcript}

IMPORTANT CONTEXT:
This is "First Cup" - a panel discussion show. Focus ONLY on the panel discussion topic (first ~25 minutes), NOT the teaser at the end.

Create 5 title options that are:
- Keyword-rich for SEO
- Optimized for virality (curiosity gap, emotional trigger, or bold claim)
- Under 60 characters
- Focused ONLY on the First Cup panel discussion topic

Format each on a new line as:
TITLE 1: [title]
TITLE 2: [title]
TITLE 3: [title]
TITLE 4: [title]
TITLE 5: [title]"""
    
    print("  Generating titles from Claude API...")
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    
    # Extract titles
    title_pattern = r'TITLE \d+: (.+?)(?=\n|$)'
    titles = re.findall(title_pattern, response_text)
    
    return titles

def interactive_title_selection(transcript, api_key, newsletter_examples=None, slack=None, filename=""):
    """Interactive title selection with iteration capability and custom title support

    Supports both CLI and Slack interaction modes.
    """
    print("\n" + "="*60)
    print("TITLE SELECTION")
    print("="*60)

    titles = get_titles_from_claude(transcript, api_key, newsletter_examples=newsletter_examples)

    # Slack mode
    if slack and slack.is_enabled():
        return interactive_title_selection_slack(titles, transcript, api_key, newsletter_examples, slack, filename)

    # CLI mode (original)
    return interactive_title_selection_cli(titles, transcript, api_key, newsletter_examples)


def interactive_title_selection_cli(titles, transcript, api_key, newsletter_examples):
    """CLI-based title selection (original behavior)"""
    while True:
        print("\n📝 Title Options:\n")
        for i, title in enumerate(titles, 1):
            print(f"  {i}. {title}")

        print("\n" + "-"*60)
        print("Options:")
        print("  • Enter a number (1-5) to select that title")
        print("  • Enter 'f' to provide feedback OR specify a custom title")
        print("  • Enter 'q' to quit without processing")
        print("-"*60)

        choice = input("\nYour choice: ").strip().lower()

        if choice == 'q':
            print("\n❌ Processing cancelled.")
            return None

        elif choice == 'f':
            print("\n💬 Provide feedback or specify a custom title:")
            print("   • Feedback: 'Focus more on AI', 'Make it more specific', etc.")
            print("   • Custom title: 'TITLE: Your Exact Title Here'")
            feedback = input("\nInput: ").strip()

            if not feedback:
                print("⚠️  No input provided, keeping current titles.")
                continue

            # Check if user is specifying a custom title
            if feedback.lower().startswith('title:'):
                custom_title = feedback[6:].strip()  # Remove 'title:' prefix

                # Apply proper title case
                custom_title = to_title_case(custom_title)

                print(f"\n✅ Using your custom title: {custom_title}")
                confirm = input("\n🔍 Confirm this title? (y/n): ").strip().lower()
                if confirm == 'y':
                    return custom_title
                else:
                    print("\n↩️  Let's try again...")
            else:
                # Regular feedback - generate new titles
                print("\n🔄 Generating new titles based on your feedback...")
                titles = get_titles_from_claude(transcript, api_key, feedback, newsletter_examples)

        elif choice.isdigit() and 1 <= int(choice) <= 5:
            selected_title = titles[int(choice) - 1]
            print(f"\n✅ Selected: {selected_title}")

            confirm = input("\n🔍 Confirm this title? (y/n): ").strip().lower()
            if confirm == 'y':
                return selected_title
            else:
                print("\n↩️  Let's choose again...")

        else:
            print("⚠️  Invalid choice. Please try again.")


def interactive_title_selection_slack(titles, transcript, api_key, newsletter_examples, slack, filename):
    """Slack-based title selection"""
    while True:
        # Send title options to Slack
        message_ts = slack.send_title_options(titles, filename)

        if not message_ts:
            print("⚠️  Failed to send Slack message, falling back to CLI mode")
            return interactive_title_selection_cli(titles, transcript, api_key, newsletter_examples)

        # Poll for response (wait indefinitely)
        response, response_type = slack.poll_for_response(message_ts, timeout_seconds=None)

        if response_type == 'number':
            # User selected a number
            selected_index = int(response) - 1
            selected_title = titles[selected_index]
            slack.notify_title_selected(selected_title)
            print(f"  ✅ Selected via Slack: {selected_title}")
            return selected_title

        elif response_type == 'custom_title':
            # User specified a custom title
            custom_title = to_title_case(response)
            slack.notify_title_selected(custom_title)
            print(f"  ✅ Custom title via Slack: {custom_title}")
            return custom_title

        elif response_type == 'feedback':
            # User wants new titles based on feedback
            slack.notify_generating_new_titles()
            print(f"  🔄 Generating new titles based on feedback: {response}")
            titles = get_titles_from_claude(transcript, api_key, response, newsletter_examples)
            # Loop continues with new titles

        else:
            # Shouldn't happen with infinite wait, but handle gracefully
            print("⚠️  No response received from Slack")
            return None

def process_with_claude(transcript, api_key, selected_title, newsletter_examples=None):
    """Send transcript to Claude and get processed outputs with the selected title"""
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = create_prompt(transcript, newsletter_examples)
    
    # Add the selected title to the prompt
    prompt = f"""{prompt}

IMPORTANT: The user has selected this title for the video:
"{selected_title}"

Use this exact title as context when writing the description and newsletter article. The description and newsletter should align with and support this chosen title."""
    
    print("\n  📝 Generating description and newsletter...")
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    print(f"  ✓ Response received ({len(response_text)} chars)")
    
    return response_text

def parse_response(response_text):
    """Parse Claude's response into structured outputs"""
    outputs = {
        'hook': '',
        'key_topics': '',
        'timestamps': '',
        'panelists': '',
        'keywords': '',
        'newsletter': ''
    }
    
    # Extract hook
    hook_match = re.search(r'HOOK:(.*?)(?=KEY_TOPICS:|TIMESTAMPS:|PANELISTS:|KEYWORDS:|NEWSLETTER|$)', 
                          response_text, re.DOTALL | re.IGNORECASE)
    if hook_match:
        hook = hook_match.group(1).strip()
        # Remove markdown formatting
        hook = re.sub(r'\*\*', '', hook)
        hook = re.sub(r'__', '', hook)
        outputs['hook'] = hook
    
    # Extract key topics
    topics_match = re.search(r'KEY_TOPICS:(.*?)(?=TIMESTAMPS:|PANELISTS:|KEYWORDS:|NEWSLETTER|$)', 
                            response_text, re.DOTALL | re.IGNORECASE)
    if topics_match:
        topics = topics_match.group(1).strip()
        # Remove markdown formatting
        topics = re.sub(r'\*\*', '', topics)
        topics = re.sub(r'__', '', topics)
        outputs['key_topics'] = topics
    
    # Extract timestamps
    timestamps_match = re.search(r'TIMESTAMPS:(.*?)(?=PANELISTS:|KEYWORDS:|NEWSLETTER|$)', 
                                response_text, re.DOTALL | re.IGNORECASE)
    if timestamps_match:
        timestamps = timestamps_match.group(1).strip()
        # Remove markdown formatting
        timestamps = re.sub(r'\*\*', '', timestamps)
        timestamps = re.sub(r'__', '', timestamps)
        outputs['timestamps'] = timestamps
    
    # Extract panelists
    panelists_match = re.search(r'PANELISTS:(.*?)(?=KEYWORDS:|NEWSLETTER|$)', 
                               response_text, re.DOTALL | re.IGNORECASE)
    if panelists_match:
        panelists = panelists_match.group(1).strip()
        # Remove markdown formatting
        panelists = re.sub(r'\*\*', '', panelists)
        panelists = re.sub(r'__', '', panelists)
        outputs['panelists'] = panelists
    
    # Extract keywords
    keywords_match = re.search(r'KEYWORDS:(.*?)(?=NEWSLETTER|$)', 
                              response_text, re.DOTALL | re.IGNORECASE)
    if keywords_match:
        keywords_raw = keywords_match.group(1).strip()
        # Clean up keywords - remove hashtags if present, ensure comma separation
        keywords_raw = keywords_raw.replace('#', '').strip()
        # Remove markdown formatting
        keywords_raw = re.sub(r'\*\*', '', keywords_raw)
        keywords_raw = re.sub(r'__', '', keywords_raw)
        # Take only the first line if there are multiple lines
        keywords_lines = keywords_raw.split('\n')
        keywords_raw = keywords_lines[0].strip()
        # Remove any trailing numbers or periods (like "3.")
        keywords_raw = re.sub(r'\s*\d+\.\s*$', '', keywords_raw)
        outputs['keywords'] = keywords_raw
    
    # Extract newsletter article
    newsletter_match = re.search(r'NEWSLETTER\s+ARTICLE:\s*(.*?)$',
                                response_text, re.DOTALL | re.IGNORECASE)
    if newsletter_match:
        newsletter = newsletter_match.group(1).strip()

        # Strip the email subject line - look for the "☕️ First Cup:" header
        first_cup_match = re.search(r'(☕️\s*First Cup:.*)', newsletter, re.DOTALL | re.IGNORECASE)
        if first_cup_match:
            newsletter = first_cup_match.group(1).strip()
            print(f"  ✓ Newsletter article extracted (removed subject line, {len(newsletter)} chars)")
        else:
            print(f"  ✓ Newsletter article extracted ({len(newsletter)} chars)")
            print(f"  ⚠️  Warning: Could not find '☕️ First Cup:' header, keeping full content")

        # Keep markdown formatting (bold, italics, links)
        outputs['newsletter'] = newsletter
    else:
        print("  ⚠️  WARNING: Newsletter article not found in response")
        print("  Response structure might have changed. Saving what we have...")
        # Try to extract anything after a newsletter-related header
        fallback_match = re.search(r'(?:newsletter|article).*?:\s*(.*?)$',
                                   response_text, re.DOTALL | re.IGNORECASE)
        if fallback_match:
            outputs['newsletter'] = fallback_match.group(1).strip()
            print(f"  ℹ️  Used fallback extraction ({len(outputs['newsletter'])} chars)")

    # Final validation
    if not outputs['newsletter']:
        print("  ❌ ERROR: Newsletter article is empty!")
        print("  This may indicate a parsing issue. Check full_response.txt for the raw output.")

    return outputs

def load_template(template_path):
    """Load the YouTube description template"""
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Return a basic default template if file doesn't exist
        return """{{HOOK}}

{{KEY_TOPICS}}

⏱️ TIMESTAMPS:
{{TIMESTAMPS}}

---

Keywords: {{KEYWORDS}}
"""

def load_newsletter_examples(examples_path):
    """Load newsletter examples for few-shot learning"""
    if examples_path.exists():
        with open(examples_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Only return the examples section, not the instructions
            # Look for actual examples (marked with "## Example")
            if "## Example 1:" in content:
                return content
            else:
                return None
    return None

def populate_template(template, outputs):
    """Populate the template with parsed outputs"""
    description = template.replace('{{HOOK}}', outputs['hook'])
    description = description.replace('{{KEY_TOPICS}}', outputs['key_topics'])
    description = description.replace('{{TIMESTAMPS}}', outputs['timestamps'])
    description = description.replace('{{PANELISTS}}', outputs['panelists'])
    description = description.replace('{{KEYWORDS}}', outputs['keywords'])
    
    # Also handle case variations
    description = description.replace('{{Panelists}}', outputs['panelists'])
    
    return description

def save_outputs(outputs, output_dir, base_filename, selected_title, description_text):
    """Save processed outputs to files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(output_dir)
    
    # Create subdirectory for this transcript
    transcript_dir = output_dir / f"{base_filename}_{timestamp}"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    
    # Save selected title
    title_file = transcript_dir / "SELECTED_TITLE.txt"
    with open(title_file, 'w') as f:
        f.write("=== SELECTED TITLE ===\n\n")
        f.write(f"{selected_title}\n")
    
    # Save YouTube description (populated from template)
    desc_file = transcript_dir / "youtube_description.txt"
    with open(desc_file, 'w') as f:
        f.write(description_text)
    
    # Save keywords separately (only once)
    keywords_file = transcript_dir / "keywords.txt"
    with open(keywords_file, 'w') as f:
        f.write("=== KEYWORDS (comma-separated) ===\n\n")
        f.write(outputs['keywords'])
        f.write("\n")
    
    # Save newsletter article with headline
    newsletter_file = transcript_dir / "newsletter_article.txt"
    with open(newsletter_file, 'w') as f:
        # Add the mandatory headline and remove any duplicate headline from Claude's output
        newsletter_content = outputs['newsletter']

        # Remove the first line(s) if they look like headlines
        lines = newsletter_content.split('\n')
        while lines:
            first_line = lines[0].strip()
            # Check if first line is a headline (doesn't start with ** for bold content, or is a ☕️ headline)
            if (first_line and
                not first_line.startswith('**') and
                (not first_line.startswith('*') or '☕️' in first_line or 'First Cup' in first_line) and
                not first_line.startswith('##')):
                # Remove this headline line
                lines.pop(0)
            else:
                break

        newsletter_content = '\n'.join(lines).lstrip()

        # Add our formatted headline
        newsletter_content = f"## ☕️ First Cup: {selected_title}\n\n{newsletter_content}"

        f.write(newsletter_content)
    
    # Save components separately for reference/editing
    components_file = transcript_dir / "description_components.txt"
    with open(components_file, 'w') as f:
        f.write("=== DESCRIPTION COMPONENTS ===\n\n")
        f.write(f"HOOK:\n{outputs['hook']}\n\n")
        f.write(f"KEY TOPICS:\n{outputs['key_topics']}\n\n")
        f.write(f"TIMESTAMPS:\n{outputs['timestamps']}\n\n")
        f.write(f"PANELISTS:\n{outputs['panelists']}\n\n")
        f.write(f"KEYWORDS:\n{outputs['keywords']}\n")
    
    # Save full response for reference
    full_file = transcript_dir / "full_response.txt"
    with open(full_file, 'w') as f:
        f.write(f"=== SELECTED TITLE ===\n\n{selected_title}")
        f.write(f"\n\n=== YOUTUBE DESCRIPTION (with template) ===\n\n{description_text}")
        f.write(f"\n\n=== NEWSLETTER ARTICLE ===\n\n{outputs['newsletter']}")
    
    print(f"  ✓ Outputs saved to: {transcript_dir}")
    return transcript_dir

def process_transcript_file(filepath, output_dir, api_key, template_path, examples_path, slack=None):
    """Process a single transcript file"""
    print(f"\n📄 Processing: {filepath.name}")

    # Start a new thread for this transcript (keeps each processing session organized)
    if slack and slack.is_enabled():
        slack.start_new_thread()
        slack.notify_processing_start(filepath.name)

    try:
        # Read transcript
        with open(filepath, 'r', encoding='utf-8') as f:
            transcript = f.read()

        print(f"  Transcript length: {len(transcript)} characters")

        # Load newsletter examples
        newsletter_examples = load_newsletter_examples(examples_path)
        if newsletter_examples:
            print(f"  📚 Using newsletter examples for style matching")

        # Interactive title selection (supports both CLI and Slack)
        selected_title = interactive_title_selection(
            transcript,
            api_key,
            newsletter_examples,
            slack=slack,
            filename=filepath.name
        )

        if selected_title is None:
            print("\n⚠️  Skipping this file (user cancelled)")
            if slack and slack.is_enabled():
                slack.notify_cancelled(filepath.name)
            return None

        # Process with Claude using the selected title and examples
        response = process_with_claude(transcript, api_key, selected_title, newsletter_examples)

        # Parse response into components
        outputs = parse_response(response)

        # Load and populate template
        template = load_template(template_path)
        description_text = populate_template(template, outputs)

        # Save outputs including the populated description
        base_filename = filepath.stem
        output_path = save_outputs(outputs, output_dir, base_filename, selected_title, description_text)

        # Mark as processed
        save_processed_file(output_dir, filepath.name)

        print(f"\n  ✅ Complete!")

        # Notify completion via Slack
        if slack and slack.is_enabled():
            slack.notify_completion(str(output_path), filepath.name)

        return output_path

    except Exception as e:
        print(f"\n  ❌ Error processing {filepath.name}: {e}")

        # Notify error via Slack
        if slack and slack.is_enabled():
            slack.notify_error(filepath.name, str(e))

        raise

def watch_directory(watch_dir, output_dir, api_key, template_path, examples_path, config=None):
    """Watch directory for new transcript files"""
    watch_path = Path(watch_dir)
    output_path = Path(output_dir)

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize Slack helper if configured
    slack = None
    if config and SLACK_AVAILABLE:
        slack_config = config.get('slack', {})
        if slack_config.get('enabled'):
            # Slack credentials are read from environment variables (.env)
            slack = SlackHelper()
            if slack.is_enabled():
                print(f"✅ Slack integration enabled")
            else:
                print(f"⚠️  Slack enabled in config but missing credentials")
                slack = None

    # Check for template file
    if template_path.exists():
        print(f"📄 Using template: {template_path}")
    else:
        print(f"⚠️  Template not found at {template_path}")
        print(f"   Using basic default template")

    # Check for newsletter examples
    if examples_path.exists():
        print(f"📚 Using newsletter examples: {examples_path}")
    else:
        print(f"ℹ️  No newsletter examples found at {examples_path}")
        print(f"   Will generate newsletters without style examples")

    print(f"👀 Watching directory: {watch_path}")
    print(f"📁 Output directory: {output_path}")
    print(f"⏱️  Checking every {WATCH_INTERVAL} seconds...")
    print(f"\n🔔 Waiting for transcript files (.txt, .md, .json)...\n")

    processed = load_processed_files(output_dir)

    while True:
        try:
            # Find all transcript files
            transcript_files = []
            for ext in ['*.txt', '*.md', '*.json']:
                transcript_files.extend(watch_path.glob(ext))

            # Process new files
            for filepath in transcript_files:
                if filepath.name == PROCESSED_FILE:
                    continue

                # Skip the template and examples files
                if filepath.name == template_path.name or filepath.name == examples_path.name:
                    continue

                if filepath.name not in processed:
                    try:
                        process_transcript_file(
                            filepath,
                            output_dir,
                            api_key,
                            template_path,
                            examples_path,
                            slack=slack
                        )
                        processed.append(filepath.name)
                    except Exception as e:
                        print(f"  ❌ Error processing {filepath.name}: {e}")

            time.sleep(WATCH_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n👋 Stopping watcher. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(WATCH_INTERVAL)

def main():
    """Main entry point"""
    # Load configuration
    config = load_config()

    # Check for special commands
    if len(sys.argv) == 2:
        if sys.argv[1] == '--test-slack':
            # Test Slack integration
            if not SLACK_AVAILABLE:
                print("❌ Slack integration not available")
                print("   Make sure slack_helper.py exists and requests is installed")
                sys.exit(1)

            slack_config = config.get('slack', {})
            if not slack_config.get('enabled'):
                print("❌ Slack is not enabled in config.json")
                print("   Set slack.enabled to true and add credentials to .env")
                sys.exit(1)

            # Slack credentials are read from environment variables (.env)
            slack = SlackHelper()

            success, message = slack.test_connection()
            if success:
                print(f"✅ {message}")
                sys.exit(0)
            else:
                print(f"❌ {message}")
                sys.exit(1)

        elif sys.argv[1] in ['-h', '--help', 'help']:
            print("Usage: python youtube_processor.py [watch_directory] [output_directory] [template_file]")
            print("\n🔧 Configuration:")
            print("   • Uses config.json for default paths")
            print("   • Command-line args override config.json")
            print("\n📖 Examples:")
            print("   python youtube_processor.py                    # Use config.json defaults")
            print("   python youtube_processor.py ./transcripts ./outputs")
            print("   python youtube_processor.py ./transcripts ./outputs ./my_template.txt")
            print("   python youtube_processor.py --test-slack       # Test Slack integration")
            print("\n🔑 Environment:")
            print("   export ANTHROPIC_API_KEY='your-api-key-here'")
            print("\n📄 Template placeholders:")
            print("   {{HOOK}}, {{KEY_TOPICS}}, {{TIMESTAMPS}}, {{PANELISTS}}, {{KEYWORDS}}")
            print("\n💬 Slack Integration:")
            print("   See SLACK_SETUP_GUIDE.md for setup instructions")
            sys.exit(0)

    # Command-line arguments override config
    if len(sys.argv) >= 3:
        watch_dir = sys.argv[1]
        output_dir = sys.argv[2]
        print(f"📝 Using command-line directories:")
        print(f"   Watch: {watch_dir}")
        print(f"   Output: {output_dir}")
    else:
        # Use config.json defaults
        script_dir = Path(__file__).parent
        watch_dir = (script_dir / config['directories']['transcripts']).resolve()
        output_dir = (script_dir / config['directories']['outputs']).resolve()
        print(f"📝 Using config.json directories:")
        print(f"   Watch: {watch_dir}")
        print(f"   Output: {output_dir}")

    # Check for custom template from command-line, otherwise use config
    if len(sys.argv) >= 4:
        template_file = sys.argv[3]
    else:
        script_dir = Path(__file__).parent
        template_file = script_dir / config['templates']['youtube_description']

    template_path = Path(template_file)

    # Look for newsletter examples file from config
    script_dir = Path(__file__).parent
    examples_path = script_dir / config['templates']['newsletter_examples']

    # Check for API key
    if not ANTHROPIC_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Validate/create directories
    watch_path = Path(watch_dir)
    output_path = Path(output_dir)

    if not watch_path.exists():
        print(f"⚠️  Watch directory does not exist: {watch_dir}")
        create = input(f"   Create it? (y/n): ").strip().lower()
        if create == 'y':
            watch_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ Created: {watch_dir}")
        else:
            print(f"❌ Cannot proceed without watch directory")
            sys.exit(1)

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created output directory: {output_dir}")

    print("=" * 60)
    print("🎬 YouTube Transcript Processor")
    print("=" * 60)

    # Start watching (pass config for Slack integration)
    watch_directory(watch_dir, output_dir, ANTHROPIC_API_KEY, template_path, examples_path, config=config)

if __name__ == "__main__":
    main()