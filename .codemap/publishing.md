# publishing

**Purpose:** Publishes a processed First Cup episode to the Product Coffee WordPress site as a draft post — matches the episode to its YouTube video, uploads the thumbnail as a featured image, and creates the post under the "First Cup" category via the WordPress REST API.

## Key files
- `blog_publisher.py` → `BlogPublisher` — WP REST client (auth, category lookup/creation, image upload, post creation, markdown→HTML).
- `blog_publisher.py` → `BlogPublisher.__init__` — builds `HTTPBasicAuth` from `WP_SITE_URL`/`WP_USERNAME`/`WP_APP_PASSWORD` env vars; `self.auth` is `None` if any are missing.
- `blog_publisher.py` → `BlogPublisher.is_configured`, `test_connection` — config check and `GET /users/me` connectivity probe.
- `blog_publisher.py` → `BlogPublisher.get_first_cup_category_id` — finds-or-creates the "First Cup" category, caches id in `self._first_cup_category_id`.
- `blog_publisher.py` → `BlogPublisher.upload_featured_image` — downloads a YouTube thumbnail URL and `POST`s it to `/wp-json/wp/v2/media`, returns media id.
- `blog_publisher.py` → `BlogPublisher.create_post` — builds post JSON (`status: 'draft'`, category, `featured_media`), `POST`s to `/wp-json/wp/v2/posts`.
- `blog_publisher.py` → `BlogPublisher._markdown_to_html` — regex-based markdown→HTML (links, bold, italic, paragraphs, `##` headers) plus `{{YOUTUBE_URL}}` placeholder substitution.
- `blog_publisher.py` → `get_youtube_video_for_title` — wraps `youtube_helper.get_most_recent_video` (title-matched), attaches `thumbnail_url` (`maxresdefault.jpg`).
- `blog_publisher.py` → `publish_first_cup` — top-level orchestrator: reads `SELECTED_TITLE.txt` + `linkedin_blog_post.txt` from an output dir, resolves video, uploads image, creates post.
- `blog_publisher.py` → `find_most_recent_output` — picks newest dir under `outputs/` by mtime, for CLI `--publish` mode.
- `blog_publisher.py` → module-level `sys.path.insert` for `WEEKLY_BREW_PATH` — cross-repo import shim (see Mechanism notes).

## Key flows
- **CLI direct**: `python blog_publisher.py --publish` → `find_most_recent_output()` → `publish_first_cup(output_dir)` → prints edit URL.
- **Poller-triggered** (see publish-triggers): `publish_poller.py` detects 📤 reaction/"publish" reply → calls `publish_first_cup(output_dir, selected_title)`.
- **Inside `publish_first_cup`**: read title/content from disk → `get_youtube_video_for_title(title)` (falls back to `get_most_recent_video` if no title match) → `BlogPublisher()` init → `test_connection()` (hard-fails publish if this fails) → `upload_featured_image()` (soft-fail: `None` on error, post still created without image) → `create_post()` → returns `(success, message, post_info)` with `post_info['edit_url']` for Slack notification.

## Mechanism notes
- **Live footgun — `WP_APP_PASSWORD` contains spaces.** WordPress application passwords are space-separated groups (e.g. `abcd efgh ijkl mnop`). If this value is ever left unquoted in `.env`, `source .env` in `run_processor.sh` truncates it at the first space and WordPress auth fails silently (well-formed request, just wrong credential). It was fixed by quoting the value in `.env`, but nothing in code enforces this — anyone editing `.env` by hand can reintroduce the bug. There is no validation step here that would surface a truncated password distinctly from a wrong one; `test_connection()` just reports a generic API error/status code.
- **Cross-repo coupling.** `blog_publisher.py` does `WEEKLY_BREW_PATH = Path(__file__).parent.parent / "weekly-brew"` then `sys.path.insert(0, str(WEEKLY_BREW_PATH))` and imports `get_most_recent_video`, `FIRST_CUP_PLAYLIST_ID` from `youtube_helper` — a module that lives in the **sibling** `weekly-brew` project, not this repo. This only works because both projects are checked out as sibling directories on this machine. If `weekly-brew` is renamed, moved, or absent (e.g. a fresh clone of just this repo, or a CI/deploy environment), the `import` fails and the code degrades to `YOUTUBE_AVAILABLE = False` — publishing becomes impossible (`get_youtube_video_for_title` returns `None` immediately, `publish_first_cup` returns `"Could not find YouTube video"`) but the failure only surfaces at runtime, not at import time (import is wrapped in `try/except ImportError`).
- **Partial-failure / no-rollback state.** `upload_featured_image` failure is swallowed (returns `None`, logged as `⚠️`) and `create_post` proceeds without a featured image — this is an intentional soft-fail. But the reverse is not handled: if the image upload **succeeds** and `create_post` then fails (network error, WP down), the uploaded media item is orphaned in the WordPress media library with no post referencing it and no cleanup/rollback logic. Re-running `publish_first_cup` will upload a duplicate image.
- **No retries anywhere.** Every `requests.get`/`requests.post` call (`test_connection`, category lookup/create, image upload, post create) is a single attempt with only a timeout; transient network failures or WP 5xx responses just fail the whole publish flow immediately (caught by broad `except Exception` in each method, returned as a `(False, message)` tuple). Re-publishing is the only recovery path, and re-publishing after a partial success (see above) can duplicate media.
- **Idempotency**: none by design. `get_first_cup_category_id` avoids duplicate categories via the cached search-then-create pattern, but there is no equivalent check for posts or media — calling `publish_first_cup` twice for the same episode creates two draft posts and (if both uploads succeed) two media items.
- Posts are always created with `status: 'draft'` — never auto-published; a human must review and publish from the WP admin (`edit_url`) after the flow completes.
- `_markdown_to_html` is a hand-rolled regex converter (not a markdown library) — fragile to edge cases like nested emphasis or lists; only `##` headers, `**bold**`, `*italic*`, `[text](url)` links, and blank-line paragraphs are handled.

## Related subsystems
- **publish-triggers** (`publish_poller.py`, `publish_webhook.py`) — detects the 📤 reaction / "publish" reply that invokes `publish_first_cup`.
- **processor** (`youtube_processor.py`) — produces `SELECTED_TITLE.txt` and `linkedin_blog_post.txt` in the output dir that this subsystem reads.
- **slack** (`slack_helper.py`) — surfaces `post_info['edit_url']` back to the user after publish.
- **thumbnails** — YouTube `maxresdefault.jpg` URL convention is assumed to always exist for the video; no fallback to lower-resolution thumbnails if `maxresdefault` is unavailable for a given video.
