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

2. YOUTUBE DESCRIPTION
Write a compelling description including:
- Hook paragraph (2-3 sentences) that entices viewers about the PANEL DISCUSSION topic
- Key topics covered in the PANEL DISCUSSION ONLY (3-5 bullet points with brief descriptions)
- DO NOT describe the teaser/main session content in the main description
- Chapter breaks with timestamps in this EXACT format:
  00:00 - Introduction
  05:23 - [Panel discussion topic name]
  12:45 - [Panel discussion topic name]
  25:00 - Transition to Main Session (or similar - include this timestamp but keep it brief)
  [derive all timestamps and topics from the transcript content]
- Call to action (subscribe, like, comment)
- 5-10 relevant hashtags related to the PANEL DISCUSSION topic

Start this section with "YOUTUBE DESCRIPTION:" header.

3. NEWSLETTER ARTICLE
Write a 200-300 word newsletter article that:
- Opens with an engaging hook that creates curiosity about the PANEL DISCUSSION
- Summarizes the PANEL DISCUSSION ONLY in 2-3 paragraphs
- DO NOT mention or describe the teaser/main session at the end
- Highlights ONE specific, actionable key takeaway from the PANEL DISCUSSION
- Ends with a clear CTA to watch the full video on YouTube
- Uses a conversational, friendly tone (not overly promotional)
- Include a suggested subject line at the top focused on the panel discussion topic

Start this section with "NEWSLETTER ARTICLE:" header.

Please format your response with clear section headers so outputs can be easily parsed."""

def process_with_claude(transcript, api_key):
    """Send transcript to Claude and get processed outputs"""
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = create_prompt(transcript)
    
    print("  Sending to Claude API...")
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    print(f"  Response received ({len(response_text)} chars)")
    
    return response_text

def parse_response(response_text):
    """Parse Claude's response into structured outputs"""
    outputs = {
        'titles': [],
        'description': '',
        'newsletter': ''
    }
    
    # Extract titles
    title_pattern = r'TITLE \d+: (.+?)(?=\n|$)'
    titles = re.findall(title_pattern, response_text)
    outputs['titles'] = titles
    
    # Extract YouTube description
    desc_match = re.search(r'YOUTUBE DESCRIPTION:(.*?)(?=NEWSLETTER ARTICLE:|$)',
                          response_text, re.DOTALL | re.IGNORECASE)
    if desc_match:
        outputs['description'] = desc_match.group(1).strip()
    
    # Extract newsletter article
    newsletter_match = re.search(r'NEWSLETTER ARTICLE:(.*?)$',
                                response_text, re.DOTALL | re.IGNORECASE)
    if newsletter_match:
        outputs['newsletter'] = newsletter_match.group(1).strip()
    
    return outputs

def save_outputs(outputs, output_dir, base_filename):
    """Save processed outputs to files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(output_dir)
    
    # Create subdirectory for this transcript
    transcript_dir = output_dir / f"{base_filename}_{timestamp}"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    
    # Save titles
    titles_file = transcript_dir / "titles.txt"
    with open(titles_file, 'w') as f:
        f.write("=== TITLE OPTIONS ===\n\n")
        for i, title in enumerate(outputs['titles'], 1):
            f.write(f"{i}. {title}\n")
    
    # Save YouTube description
    desc_file = transcript_dir / "youtube_description.txt"
    with open(desc_file, 'w') as f:
        f.write(outputs['description'])
    
    # Save newsletter article
    newsletter_file = transcript_dir / "newsletter_article.txt"
    with open(newsletter_file, 'w') as f:
        f.write(outputs['newsletter'])
    
    # Save full response for reference
    full_file = transcript_dir / "full_response.txt"
    with open(full_file, 'w') as f:
        f.write("=== TITLES ===\n\n")
        for i, title in enumerate(outputs['titles'], 1):
            f.write(f"{i}. {title}\n")
        f.write(f"\n\n=== YOUTUBE DESCRIPTION ===\n\n{outputs['description']}")
        f.write(f"\n\n=== NEWSLETTER ARTICLE ===\n\n{outputs['newsletter']}")
    
    print(f"  ✓ Outputs saved to: {transcript_dir}")
    return transcript_dir

def process_transcript_file(filepath, output_dir, api_key):
    """Process a single transcript file"""
    print(f"\n📄 Processing: {filepath.name}")
    
    # Read transcript
    with open(filepath, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    print(f"  Transcript length: {len(transcript)} characters")
    
    # Process with Claude
    response = process_with_claude(transcript, api_key)
    
    # Parse response
    outputs = parse_response(response)
    
    # Save outputs
    base_filename = filepath.stem
    output_path = save_outputs(outputs, output_dir, base_filename)
    
    # Mark as processed
    save_processed_file(output_dir, filepath.name)
    
    print(f"  ✅ Complete!")
    return output_path

def watch_directory(watch_dir, output_dir, api_key):
    """Watch directory for new transcript files"""
    watch_path = Path(watch_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
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
                    
                if filepath.name not in processed:
                    try:
                        process_transcript_file(filepath, output_dir, api_key)
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
        print("Usage: python youtube_processor.py <watch_directory> <output_directory>")
        print("\nExample:")
        print("  python youtube_processor.py ./transcripts ./processed")
        print("\nMake sure to set ANTHROPIC_API_KEY environment variable:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    watch_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
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
    watch_directory(watch_dir, output_dir, ANTHROPIC_API_KEY)

if __name__ == "__main__":
    main()
