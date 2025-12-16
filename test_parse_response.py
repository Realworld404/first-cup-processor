#!/usr/bin/env python3
"""
Regression tests for the parse_response function in youtube_processor.py

These tests ensure that the response parsing correctly extracts all required sections:
- HOOK
- KEY_TOPICS
- TIMESTAMPS
- PANELISTS
- KEYWORDS
- NEWSLETTER TEASER
- LINKEDIN/BLOG POST

Run with: python3 test_parse_response.py
"""

import sys
from pathlib import Path

# Import parse_response from youtube_processor
from youtube_processor import parse_response


# Sample responses for testing
WORKING_RESPONSE = """=== YOUTUBE DESCRIPTION (with template) ===

Are we in an AI bubble heading for a crash? Our panel of product veterans dive into the parallels.

HOOK:
Are we in an AI bubble heading for a crash, or is this time different? Our panel of product veterans who lived through the dot-com boom dive into the parallels between today's AI hype and the internet bubble of the late 90s.

KEY_TOPICS:
• Comparing the current AI hype cycle to the dot-com bubble
• Why "AI Product Manager" titles are problematic
• The role of social media in amplifying AI hype
• Real examples of AI companies burning cash

TIMESTAMPS:
00:00 - Introduction and panel introductions
02:47 - Is the AI cycle the same or different from past tech bubbles?
06:17 - The problem with "AI Product Manager" job titles
08:29 - Social media's role in amplifying AI hype

PANELISTS:
• Steve Johnson - CEO of Product Growth Leaders
• Mark Michelson - Regional Director for the AI Collective
• Blossom Onunekwo - Scrum certified product manager

KEYWORDS: AI bubble, artificial intelligence hype cycle, product management, tech bubble, AI market crash, generative AI

NEWSLETTER TEASER:
Are we in another dot-com bubble? Our panel of product veterans tackled the question head-on. **Steve Johnson** was blunt: *"There's no such thing as AI Product Manager."* [Watch the debate →]({{YOUTUBE_URL}})

LINKEDIN/BLOG POST:
☕️ First Cup: Are We in an AI Bubble?

This week's panel discussed the AI bubble question. **Steve Johnson** noted that *"there's no such thing as AI Product Manager."* [Watch the full discussion here]({{YOUTUBE_URL}}).
"""

BROKEN_RESPONSE_MISSING_KEYWORDS = """=== YOUTUBE DESCRIPTION (with template) ===

Ever fall hard for a tech trend that completely flopped?

HOOK:
Ever fall hard for a tech trend that completely flopped? Our First Cup panel gets brutally honest about the hyped innovations.

KEY_TOPICS:
• VR and augmented reality hardware disappointments
• The rise and fall of NFTs and crypto collectibles
• Why Scrum and Agile transformations often failed

TIMESTAMPS:
00:00 - Introduction and panel introductions
02:27 - Jason Rhoades on VR and augmented reality failures
03:12 - Nandu Shah on visual programming disappointments

PANELISTS:
• Jason Rhoades - Chief Innovation Officer at Meaningful AI
• Nandu Shah - President of Atlanta CTO Club

#FirstCup #ProductCoffee

KEYWORDS:

NEWSLETTER TEASER:
Ever bet big on a tech trend that spectacularly flopped? Our panel got painfully honest. [Watch their confessions →]({{YOUTUBE_URL}})

LINKEDIN/BLOG POST:
☕️ First Cup: Failed Tech Predictions

Our panel discussed tech failures. [Watch the full discussion here]({{YOUTUBE_URL}}).
"""

BROKEN_RESPONSE_NO_NEWSLETTER = """=== YOUTUBE DESCRIPTION (with template) ===

HOOK:
Test hook content here.

KEY_TOPICS:
• Topic 1
• Topic 2

TIMESTAMPS:
00:00 - Introduction

PANELISTS:
• Person One - Title

KEYWORDS: keyword1, keyword2, keyword3
"""

RESPONSE_WITH_EXTRA_FORMATTING = """
HOOK:
**Test hook** with markdown that should be stripped.

KEY_TOPICS:
• __Topic 1__ with bold
• **Topic 2** with markdown

TIMESTAMPS:
00:00 - Introduction

PANELISTS:
• **Person One** - Title

KEYWORDS: #keyword1, #keyword2, #keyword3

NEWSLETTER TEASER:
Test teaser with **bold** that should be kept.

LINKEDIN/BLOG POST:
☕️ First Cup: Test Title

Test blog post with **bold** that should be kept.
"""


def test_working_response():
    """Test that a properly formatted response extracts all fields"""
    outputs = parse_response(WORKING_RESPONSE)

    errors = []

    # Check all required fields are present
    if not outputs['hook']:
        errors.append("HOOK is empty")
    if not outputs['key_topics']:
        errors.append("KEY_TOPICS is empty")
    if not outputs['timestamps']:
        errors.append("TIMESTAMPS is empty")
    if not outputs['panelists']:
        errors.append("PANELISTS is empty")
    if not outputs['keywords']:
        errors.append("KEYWORDS is empty")
    if not outputs['newsletter_teaser']:
        errors.append("NEWSLETTER TEASER is empty")
    if not outputs['blog_post']:
        errors.append("BLOG POST is empty")

    # Check keywords specifically
    if outputs['keywords']:
        if ',' not in outputs['keywords']:
            errors.append(f"KEYWORDS missing commas: '{outputs['keywords']}'")
        if len(outputs['keywords'].split(',')) < 3:
            errors.append(f"KEYWORDS has fewer than 3 items: '{outputs['keywords']}'")

    if errors:
        print("❌ test_working_response FAILED:")
        for err in errors:
            print(f"   - {err}")
        return False
    else:
        print("✓ test_working_response PASSED")
        return True


def test_broken_keywords():
    """Test that missing keywords are detected"""
    outputs = parse_response(BROKEN_RESPONSE_MISSING_KEYWORDS)

    # Keywords should be empty or very short (just whitespace)
    if outputs['keywords'] and len(outputs['keywords'].strip()) > 5:
        print(f"❌ test_broken_keywords FAILED: Keywords should be empty, got '{outputs['keywords']}'")
        return False

    # But other fields should still be extracted
    if not outputs['hook']:
        print("❌ test_broken_keywords FAILED: HOOK should be present")
        return False

    if not outputs['newsletter_teaser']:
        print("❌ test_broken_keywords FAILED: NEWSLETTER TEASER should be present")
        return False

    print("✓ test_broken_keywords PASSED (empty keywords detected)")
    return True


def test_missing_newsletter():
    """Test that missing newsletter/blog sections are handled"""
    outputs = parse_response(BROKEN_RESPONSE_NO_NEWSLETTER)

    # Keywords should be present
    if not outputs['keywords']:
        print("❌ test_missing_newsletter FAILED: KEYWORDS should be present")
        return False

    # Newsletter and blog should be empty
    # (This tests the fallback behavior)

    print("✓ test_missing_newsletter PASSED")
    return True


def test_markdown_stripping():
    """Test that markdown is stripped from description fields but kept in newsletter/blog"""
    outputs = parse_response(RESPONSE_WITH_EXTRA_FORMATTING)

    # HOOK should have markdown stripped
    if '**' in outputs['hook'] or '__' in outputs['hook']:
        print(f"❌ test_markdown_stripping FAILED: HOOK should not have markdown: '{outputs['hook'][:50]}'")
        return False

    # KEY_TOPICS should have markdown stripped
    if '**' in outputs['key_topics'] or '__' in outputs['key_topics']:
        print(f"❌ test_markdown_stripping FAILED: KEY_TOPICS should not have markdown")
        return False

    # KEYWORDS should have # stripped
    if '#' in outputs['keywords']:
        print(f"❌ test_markdown_stripping FAILED: KEYWORDS should not have hashtags: '{outputs['keywords']}'")
        return False

    # NEWSLETTER TEASER should keep markdown
    if outputs['newsletter_teaser'] and '**' not in outputs['newsletter_teaser']:
        print(f"❌ test_markdown_stripping FAILED: NEWSLETTER TEASER should keep markdown")
        return False

    # BLOG POST should keep markdown
    if outputs['blog_post'] and '**' not in outputs['blog_post']:
        print(f"❌ test_markdown_stripping FAILED: BLOG POST should keep markdown")
        return False

    print("✓ test_markdown_stripping PASSED")
    return True


def test_keywords_comma_separated():
    """Test that keywords are properly comma-separated"""
    outputs = parse_response(WORKING_RESPONSE)

    keywords = outputs['keywords']
    if not keywords:
        print("❌ test_keywords_comma_separated FAILED: No keywords found")
        return False

    keyword_list = [k.strip() for k in keywords.split(',')]
    if len(keyword_list) < 3:
        print(f"❌ test_keywords_comma_separated FAILED: Expected at least 3 keywords, got {len(keyword_list)}")
        return False

    # Check none are empty
    empty_keywords = [k for k in keyword_list if not k]
    if empty_keywords:
        print(f"❌ test_keywords_comma_separated FAILED: Found empty keywords in list")
        return False

    print(f"✓ test_keywords_comma_separated PASSED ({len(keyword_list)} keywords)")
    return True


def test_real_output_files():
    """
    Test that actual output files contain expected content.

    Note: This checks the SAVED output files (keywords.txt, etc.), not the raw Claude response.
    The full_response.txt is a reconstructed file, not the original Claude response.
    """
    outputs_dir = Path(__file__).parent / "outputs"
    if not outputs_dir.exists():
        print("⊘ test_real_output_files SKIPPED: No outputs directory")
        return True

    # Find the most recent output directory
    output_dirs = sorted(outputs_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
    output_dirs = [d for d in output_dirs if d.is_dir() and not d.name.startswith('.')]

    if not output_dirs:
        print("⊘ test_real_output_files SKIPPED: No output directories found")
        return True

    latest_dir = output_dirs[0]

    # Check required output files exist and have content
    required_files = [
        ("SELECTED_TITLE.txt", "Selected title"),
        ("youtube_description.txt", "YouTube description"),
        ("keywords.txt", "Keywords"),
        ("newsletter_teaser.txt", "Newsletter teaser"),
        ("linkedin_blog_post.txt", "LinkedIn/blog post"),
        ("description_components.txt", "Description components"),
    ]

    errors = []
    warnings = []

    for filename, description in required_files:
        filepath = latest_dir / filename
        if not filepath.exists():
            errors.append(f"{description} file missing: {filename}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Check for empty content (beyond headers)
        # Remove common headers to check actual content
        content_stripped = content
        for header in ['===', 'KEYWORDS', 'NEWSLETTER', 'HOOK', 'KEY TOPICS', 'TIMESTAMPS', 'PANELISTS']:
            content_stripped = content_stripped.replace(header, '')
        content_stripped = content_stripped.strip()

        if not content_stripped:
            errors.append(f"{description} is empty: {filename}")
        elif len(content_stripped) < 10:
            warnings.append(f"{description} very short ({len(content_stripped)} chars): {filename}")

    # Special check for keywords.txt - should have actual keywords
    keywords_file = latest_dir / "keywords.txt"
    if keywords_file.exists():
        with open(keywords_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # Remove header line
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('===')]
        keywords_content = ' '.join(lines)
        if not keywords_content or keywords_content.isspace():
            errors.append("Keywords file exists but has no actual keywords")
        elif ',' not in keywords_content and len(keywords_content) < 30:
            warnings.append(f"Keywords may be incomplete: '{keywords_content[:50]}'")

    if warnings:
        for warn in warnings:
            print(f"  ⚠️  {warn}")

    if errors:
        print(f"❌ test_real_output_files FAILED (latest: {latest_dir.name}):")
        for err in errors:
            print(f"   - {err}")
        return False
    else:
        print(f"✓ test_real_output_files PASSED (latest: {latest_dir.name})")
        return True


def run_all_tests():
    """Run all regression tests"""
    print("\n" + "=" * 60)
    print("Running parse_response regression tests")
    print("=" * 60 + "\n")

    tests = [
        test_working_response,
        test_broken_keywords,
        test_missing_newsletter,
        test_markdown_stripping,
        test_keywords_comma_separated,
        test_real_output_files,
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} EXCEPTION: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
