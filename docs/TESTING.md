# Testing: First Cup Processor

**Last Updated:** 2026-03-01

---

## Test Files

| File | Purpose | Tests |
|------|---------|-------|
| `test_parse_response.py` | Regression tests for response parsing functions | 6 |
| `test_pipeline.py` | Integration-style validation of the multi-step pipeline | Smoke test |

---

## Running Tests

```bash
# Run parsing regression tests
python3 test_parse_response.py

# Validate multi-step pipeline (requires valid ANTHROPIC_API_KEY)
python3 test_pipeline.py

# Test Slack integration connectivity
python3 youtube_processor.py --test-slack
```

---

## test_parse_response.py (Regression Suite)

Tests the parsing functions that extract structured data from Claude responses. These tests protect against regressions when Claude response formats change or parsers are modified.

**Coverage:**

| Test | Function Tested | Scenario |
|------|----------------|---------|
| `test_parse_youtube_description_valid` | `parse_youtube_description_response()` | Full valid response with all sections |
| `test_parse_youtube_description_missing_keywords` | `parse_youtube_description_response()` | Missing keywords section |
| `test_parse_newsletter_teaser_valid` | `parse_newsletter_teaser_response()` | Standard newsletter format |
| `test_parse_newsletter_teaser_missing` | `parse_newsletter_teaser_response()` | No NEWSLETTER TEASER: header |
| `test_parse_blog_post_valid` | `parse_blog_post_response()` | Standard blog post format |
| `test_parse_blog_post_linkedin_format` | `parse_blog_post_response()` | LINKEDIN/BLOG POST: header variant |

**Key assertions:**
- Markdown is NOT stripped from newsletter and blog content
- YouTube description components (hook, keywords, etc.) have markdown stripped
- Missing sections return empty strings with warnings, not exceptions
- Keywords validated for completeness (must have commas, >20 chars)

---

## test_pipeline.py (Pipeline Smoke Test)

Validates that the four-step pipeline executes end-to-end without errors using a sample transcript. Requires a live Anthropic API key.

**What it checks:**
- Each step calls the API successfully
- Parsed output from each step is non-empty
- Step 3 receives the hook from Step 2
- Output files are written correctly

**When to run:** After changes to prompt functions, parsing functions, or the pipeline orchestration in `process_transcript_file()`.

---

## Manual Testing Checklist

Before deploying changes:

- [ ] Drop `sample_transcript.txt` into `transcripts/` and verify full pipeline completes
- [ ] Verify Slack thread is created and title options appear
- [ ] Select a title and confirm downstream content generates
- [ ] Check `outputs/[episode_name]/` contains all 6 output files
- [ ] Confirm `full_response.txt` exists for each step (for debugging)
- [ ] Test credits exhaustion path: temporarily use invalid API key, verify "paused" message and no FAILED_ file created
- [ ] Test Slack resume: verify "resume" reply triggers retry
- [ ] Test rate limit path: verify file IS marked FAILED_ (different from credits path)

---

## Adding Regression Tests

When fixing a parsing bug:

1. Add a test case to `test_parse_response.py` with input that reproduced the bug
2. Confirm the test fails before the fix
3. Apply the fix
4. Confirm the test passes
5. Run the full test suite to check for regressions

When modifying prompt output format:

1. Update expected strings in `test_parse_response.py` to match the new format
2. Run `python3 test_parse_response.py` to verify all tests pass

---

## Test Philosophy

**No shared state:** Each test function creates its own input string; no global fixtures.

**Parse functions are pure:** They take a string, return structured data. Tests verify specific field values extracted from known inputs.

**Error cases tested:** Tests exist for partial/missing sections to ensure graceful degradation (warnings, not exceptions).
