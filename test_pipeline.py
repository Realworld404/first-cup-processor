#!/usr/bin/env python3
"""Quick test script for the new multi-step pipeline"""

import os
from youtube_processor import process_with_claude_pipeline

# Load API key
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not set")
    exit(1)

# Load transcript
transcript_path = "transcripts/First Cup-2025-12-17b.txt"
with open(transcript_path, 'r') as f:
    transcript = f.read()

# Test selected title (from previous failed run)
selected_title = "iPhone vs Jaguar: What Product Naming Teaches Us"

print(f"Testing multi-step pipeline...")
print(f"Transcript: {len(transcript)} chars")
print(f"Title: {selected_title}")
print("\n" + "="*80 + "\n")

# Run the pipeline
full_response, outputs = process_with_claude_pipeline(
    transcript,
    api_key,
    selected_title,
    newsletter_examples=None
)

print("\n" + "="*80)
print("\nRESULTS:")
print("="*80)
print(f"\nHook: {len(outputs.get('hook', ''))} chars")
print(f"Key Topics: {len(outputs.get('key_topics', ''))} chars")
print(f"Timestamps: {len(outputs.get('timestamps', ''))} chars")
print(f"Panelists: {len(outputs.get('panelists', ''))} chars")
print(f"Keywords: {outputs.get('keywords', '')}")
print(f"Newsletter Teaser: {len(outputs.get('newsletter_teaser', ''))} chars")
print(f"Blog Post: {len(outputs.get('blog_post', ''))} chars")

print("\n" + "="*80)
print("\nNEWSLETTER TEASER:")
print("="*80)
print(outputs.get('newsletter_teaser', '(empty)'))

print("\n" + "="*80)
print("\nBLOG POST:")
print("="*80)
print(outputs.get('blog_post', '(empty)'))

# Check for failures
failures = []
if not outputs.get('hook'): failures.append('hook')
if not outputs.get('key_topics'): failures.append('key_topics')
if not outputs.get('timestamps'): failures.append('timestamps')
if not outputs.get('panelists'): failures.append('panelists')
if not outputs.get('keywords'): failures.append('keywords')
if not outputs.get('newsletter_teaser'): failures.append('newsletter_teaser')
if not outputs.get('blog_post'): failures.append('blog_post')

if failures:
    print(f"\n❌ FAILED: Missing {', '.join(failures)}")
    exit(1)
else:
    print(f"\n✅ SUCCESS: All components generated!")
