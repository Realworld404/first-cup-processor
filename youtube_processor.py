#!/usr/bin/env python3
"""
YouTube Transcript Processor
Watches a directory for new transcript files and automatically generates:
1. SEO-optimized title options
2. YouTube description with timestamps
3. Newsletter article

Usage:
    python youtube_processor.py /path/to/transcripts /path/to/outputs
"""

import os
import sys
import time
import json
import re
from pathlib import Path
from datetime import datetime
import anthropic

# Configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
WATCH_INTERVAL = 10  # seconds between directory checks
PROCESSED_FILE = '.processed_transcripts.json'

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

def create_prompt(transcript):
    """Create the mega-prompt for Claude"""
    return f"""Analyze this YouTube show transcript and create three deliverables:

IMPORTANT CONTEXT ABOUT THE SHOW FORMAT:
This is "First Cup" - a panel discussion show. The main content (approximately the first 25 minutes) is a panel discussion on a specific topic. In the last ~5 minutes, there is a transition/teaser for the main session that follows.

CRITICAL INSTRUCTIONS:
- The TITLES should focus ONLY on the First Cup panel discussion topic (first 25 minutes)
- The DESCRIPTION should focus ONLY on the First Cup panel discussion
- The teaser/transition to the main session should be included in the timestamps section but should NOT be described in the main description text or key topics
- The NEWSLETTER should focus ONLY on the First Cup panel discussion
- DO NOT use markdown formatting like ** or __ in any output
- Use plain text only

TRANSCRIPT:
{transcript}

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
25:00 - Transition to Main Session
[Include ALL timestamps from the transcript]

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
Write a 200-300 word newsletter article that:
- Opens with an engaging hook that creates curiosity about the PANEL DISCUSSION
- Summarizes the PANEL DISCUSSION ONLY in 2-3 paragraphs
- DO NOT mention or describe the teaser/main session at the end
- Highlights ONE specific, actionable key takeaway from the PANEL DISCUSSION
- Ends with a clear CTA to watch the full video on YouTube
- Uses a conversational, friendly tone (not overly promotional)
- Include a suggested subject line at the top focused on the panel discussion topic
- Use plain text only - NO markdown formatting like ** or __

Start this section with "NEWSLETTER ARTICLE:" header.

CRITICAL FORMATTING REMINDERS:
- NO markdown formatting (**, __, etc.) anywhere in your response
- Keywords must be on ONE line only, comma-separated
- Use plain text throughout
- Do not add extra numbering or text after the keywords line

Please format your response with clear section headers so outputs can be easily parsed."""

def get_titles_from_claude(transcript, api_key, feedback=None):
    """Get title options from Claude, optionally with feedback for iteration"""
    client = anthropic.Anthropic(api_key=api_key)
    
    if feedback:
        prompt = f"""Based on this transcript, generate 5 NEW title options incorporating this feedback:

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
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    
    # Extract titles
    title_pattern = r'TITLE \d+: (.+?)(?=\n|$)'
    titles = re.findall(title_pattern, response_text)
    
    return titles

def interactive_title_selection(transcript, api_key):
    """Interactive title selection with iteration capability"""
    print("\n" + "="*60)
    print("TITLE SELECTION")
    print("="*60)
    
    titles = get_titles_from_claude(transcript, api_key)
    
    while True:
        print("\n📝 Title Options:\n")
        for i, title in enumerate(titles, 1):
            print(f"  {i}. {title}")
        
        print("\n" + "-"*60)
        print("Options:")
        print("  • Enter a number (1-5) to select that title")
        print("  • Enter 'f' to provide feedback and generate new titles")
        print("  • Enter 'q' to quit without processing")
        print("-"*60)
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'q':
            print("\n❌ Processing cancelled.")
            return None
        
        elif choice == 'f':
            print("\n💬 Provide feedback for title generation:")
            print("   (e.g., 'Focus more on AI', 'Make it more specific', 'Too generic')")
            feedback = input("\nFeedback: ").strip()
            
            if feedback:
                print("\n🔄 Generating new titles based on your feedback...")
                titles = get_titles_from_claude(transcript, api_key, feedback)
            else:
                print("⚠️  No feedback provided, keeping current titles.")
        
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

def process_with_claude(transcript, api_key, selected_title):
    """Send transcript to Claude and get processed outputs with the selected title"""
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = create_prompt(transcript)
    
    # Add the selected title to the prompt
    prompt = f"""{prompt}

IMPORTANT: The user has selected this title for the video:
"{selected_title}"

Use this exact title as context when writing the description and newsletter article. The description and newsletter should align with and support this chosen title."""
    
    print("\n  📝 Generating description and newsletter...")
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
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
    newsletter_match = re.search(r'NEWSLETTER ARTICLE:(.*?)$', 
                                response_text, re.DOTALL | re.IGNORECASE)
    if newsletter_match:
        newsletter = newsletter_match.group(1).strip()
        # Remove markdown formatting
        newsletter = re.sub(r'\*\*', '', newsletter)
        newsletter = re.sub(r'__', '', newsletter)
        outputs['newsletter'] = newsletter
    
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
    
    # Save newsletter article
    newsletter_file = transcript_dir / "newsletter_article.txt"
    with open(newsletter_file, 'w') as f:
        f.write(outputs['newsletter'])
    
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

def process_transcript_file(filepath, output_dir, api_key, template_path):
    """Process a single transcript file"""
    print(f"\n📄 Processing: {filepath.name}")
    
    # Read transcript
    with open(filepath, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    print(f"  Transcript length: {len(transcript)} characters")
    
    # Interactive title selection
    selected_title = interactive_title_selection(transcript, api_key)
    
    if selected_title is None:
        print("\n⚠️  Skipping this file (user cancelled)")
        return None
    
    # Process with Claude using the selected title
    response = process_with_claude(transcript, api_key, selected_title)
    
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
    return output_path

def watch_directory(watch_dir, output_dir, api_key, template_path):
    """Watch directory for new transcript files"""
    watch_path = Path(watch_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Check for template file
    if template_path.exists():
        print(f"📄 Using template: {template_path}")
    else:
        print(f"⚠️  Template not found at {template_path}")
        print(f"   Using basic default template")
    
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
                
                # Skip the template file
                if filepath.name == template_path.name:
                    continue
                    
                if filepath.name not in processed:
                    try:
                        process_transcript_file(filepath, output_dir, api_key, template_path)
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
    if len(sys.argv) < 3:
        print("Usage: python youtube_processor.py <watch_directory> <output_directory> [template_file]")
        print("\nExample:")
        print("  python youtube_processor.py ./transcripts ./processed")
        print("  python youtube_processor.py ./transcripts ./processed ./my_template.txt")
        print("\nMake sure to set ANTHROPIC_API_KEY environment variable:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nTemplate file should contain placeholders:")
        print("  {{HOOK}}, {{KEY_TOPICS}}, {{TIMESTAMPS}}, {{KEYWORDS}}")
        sys.exit(1)
    
    watch_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Check for custom template, otherwise use default
    if len(sys.argv) >= 4:
        template_file = sys.argv[3]
    else:
        # Look for template in the watch directory
        template_file = Path(watch_dir) / "youtube_description_template.txt"
        if not template_file.exists():
            # Try current directory
            template_file = Path("youtube_description_template.txt")
    
    template_path = Path(template_file)
    
    # Check for API key
    if not ANTHROPIC_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Validate directories
    if not Path(watch_dir).exists():
        print(f"❌ Error: Watch directory does not exist: {watch_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("🎬 YouTube Transcript Processor")
    print("=" * 60)
    
    # Start watching
    watch_directory(watch_dir, output_dir, ANTHROPIC_API_KEY, template_path)

if __name__ == "__main__":
    main()