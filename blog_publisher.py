"""
Blog Publisher for First Cup Processor

Publishes First Cup blog posts to Product Coffee WordPress site.
Uses the WordPress REST API with application password authentication.

Features:
- Fetches YouTube video URL and thumbnail from First Cup playlist
- Creates WordPress post with featured image
- Sets "First Cup" category automatically
"""

import os
import sys
import re
import requests
from pathlib import Path
from datetime import datetime
from requests.auth import HTTPBasicAuth

# Add weekly-brew to path for YouTube helper
WEEKLY_BREW_PATH = Path(__file__).parent.parent / "weekly-brew"
sys.path.insert(0, str(WEEKLY_BREW_PATH))

try:
    from youtube_helper import get_most_recent_video, FIRST_CUP_PLAYLIST_ID
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("⚠️  YouTube helper not available. Install weekly-brew or check path.")


class BlogPublisher:
    """Publishes First Cup content to WordPress"""

    def __init__(self, site_url=None, username=None, app_password=None):
        """
        Initialize the blog publisher.

        Credentials can be passed directly or loaded from environment variables:
        - WP_SITE_URL: WordPress site URL (e.g., https://productcoffee.com)
        - WP_USERNAME: WordPress username
        - WP_APP_PASSWORD: WordPress application password
        """
        self.site_url = (site_url or os.environ.get('WP_SITE_URL', '')).rstrip('/')
        self.username = username or os.environ.get('WP_USERNAME', '')
        self.app_password = app_password or os.environ.get('WP_APP_PASSWORD', '')

        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.auth = HTTPBasicAuth(self.username, self.app_password) if self.username and self.app_password else None

        # Cache for category ID
        self._first_cup_category_id = None

    def is_configured(self):
        """Check if WordPress credentials are configured"""
        return bool(self.site_url and self.username and self.app_password)

    def test_connection(self):
        """Test WordPress API connection"""
        if not self.is_configured():
            return False, "WordPress credentials not configured. Check WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD."

        try:
            # Test with a simple API call
            response = requests.get(
                f"{self.api_base}/users/me",
                auth=self.auth,
                headers={'User-Agent': 'FirstCupProcessor/1.0'},
                timeout=10
            )

            if response.status_code == 200:
                user_data = response.json()
                return True, f"Connected as: {user_data.get('name', 'Unknown')}"
            else:
                return False, f"API error: {response.status_code} - {response.text[:200]}"

        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def get_first_cup_category_id(self):
        """Get or create the 'First Cup' category ID"""
        if self._first_cup_category_id:
            return self._first_cup_category_id

        try:
            # Search for existing category
            response = requests.get(
                f"{self.api_base}/categories",
                params={'search': 'First Cup'},
                headers={'User-Agent': 'FirstCupProcessor/1.0'},
                timeout=10
            )

            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    if cat.get('name', '').lower() == 'first cup':
                        self._first_cup_category_id = cat['id']
                        return self._first_cup_category_id

            # Category not found - create it
            print("  📁 Creating 'First Cup' category...")
            create_response = requests.post(
                f"{self.api_base}/categories",
                auth=self.auth,
                headers={'User-Agent': 'FirstCupProcessor/1.0'},
                json={
                    'name': 'First Cup',
                    'slug': 'first-cup',
                    'description': 'Weekly panel discussions from Product Coffee'
                },
                timeout=10
            )

            if create_response.status_code in [200, 201]:
                self._first_cup_category_id = create_response.json()['id']
                print(f"  ✓ Created category with ID: {self._first_cup_category_id}")
                return self._first_cup_category_id
            else:
                print(f"  ⚠️  Could not create category: {create_response.text[:200]}")
                return None

        except Exception as e:
            print(f"  ⚠️  Error getting category: {e}")
            return None

    def upload_featured_image(self, image_url, title):
        """
        Download image from URL and upload to WordPress media library.

        Args:
            image_url: URL of the image (YouTube thumbnail)
            title: Title for the media item

        Returns:
            Media ID if successful, None otherwise
        """
        try:
            print(f"  📷 Downloading thumbnail from YouTube...")

            # Download the image
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code != 200:
                print(f"  ⚠️  Could not download thumbnail: {img_response.status_code}")
                return None

            # Clean up title for filename
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)[:50]
            filename = f"first-cup-{safe_title}.jpg"

            print(f"  📤 Uploading to WordPress media library...")

            # Upload to WordPress
            upload_response = requests.post(
                f"{self.api_base}/media",
                auth=self.auth,
                headers={
                    'User-Agent': 'FirstCupProcessor/1.0',
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Type': 'image/jpeg'
                },
                data=img_response.content,
                timeout=60
            )

            if upload_response.status_code in [200, 201]:
                media_id = upload_response.json()['id']
                print(f"  ✓ Uploaded image (Media ID: {media_id})")
                return media_id
            else:
                print(f"  ⚠️  Could not upload image: {upload_response.text[:200]}")
                return None

        except Exception as e:
            print(f"  ⚠️  Error uploading image: {e}")
            return None

    def create_post(self, title, content, youtube_url, featured_image_id=None):
        """
        Create a WordPress blog post.

        Args:
            title: Post title
            content: Post content (markdown will be converted)
            youtube_url: YouTube video URL (for embedding)
            featured_image_id: WordPress media ID for featured image

        Returns:
            (success, message, post_url)
        """
        if not self.is_configured():
            return False, "WordPress not configured", None

        try:
            # Get category ID
            category_id = self.get_first_cup_category_id()

            # Convert markdown to HTML (basic conversion)
            html_content = self._markdown_to_html(content, youtube_url)

            # Build post data
            post_data = {
                'title': title,
                'content': html_content,
                'status': 'draft',  # Start as draft for review
                'format': 'standard'
            }

            if category_id:
                post_data['categories'] = [category_id]

            if featured_image_id:
                post_data['featured_media'] = featured_image_id

            print(f"  📝 Creating WordPress post...")

            response = requests.post(
                f"{self.api_base}/posts",
                auth=self.auth,
                headers={'User-Agent': 'FirstCupProcessor/1.0'},
                json=post_data,
                timeout=30
            )

            if response.status_code in [200, 201]:
                post = response.json()
                post_url = post.get('link', '')
                edit_url = f"{self.site_url}/wp-admin/post.php?post={post['id']}&action=edit"

                return True, f"Post created (ID: {post['id']})", {
                    'id': post['id'],
                    'url': post_url,
                    'edit_url': edit_url,
                    'status': 'draft'
                }
            else:
                return False, f"API error: {response.status_code} - {response.text[:200]}", None

        except Exception as e:
            return False, f"Error creating post: {str(e)}", None

    def _markdown_to_html(self, markdown_text, youtube_url):
        """
        Convert markdown to WordPress-friendly HTML.

        Also replaces {{YOUTUBE_URL}} placeholder with actual URL.
        """
        html = markdown_text

        # Replace YouTube URL placeholder
        html = html.replace('{{YOUTUBE_URL}}', youtube_url)
        html = html.replace('{YOUTUBE_URL}', youtube_url)

        # Convert markdown links [text](url) to HTML
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

        # Convert **bold** to <strong>
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)

        # Convert *italic* to <em> (but not within URLs or already converted)
        html = re.sub(r'(?<![*<])\*([^*]+)\*(?![*>])', r'<em>\1</em>', html)

        # Convert paragraphs (double newlines)
        paragraphs = html.split('\n\n')
        html = '\n\n'.join(f'<p>{p.strip()}</p>' if not p.strip().startswith('<') and not p.strip().startswith('##') else p for p in paragraphs if p.strip())

        # Convert ## headers to h2
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)

        return html


def get_youtube_video_for_title(title):
    """
    Find the YouTube video matching the given title.

    Args:
        title: The selected title to match

    Returns:
        Dictionary with video info or None
    """
    if not YOUTUBE_AVAILABLE:
        return None

    try:
        # Try to find video matching the title
        video = get_most_recent_video(
            playlist_id=FIRST_CUP_PLAYLIST_ID,
            title_match=title
        )

        if video:
            # Add thumbnail URL
            video['thumbnail_url'] = f"https://img.youtube.com/vi/{video['video_id']}/maxresdefault.jpg"
            return video

        return None

    except Exception as e:
        print(f"⚠️  Error fetching YouTube video: {e}")
        return None


def publish_first_cup(output_dir, selected_title=None):
    """
    Main function to publish a First Cup episode.

    Args:
        output_dir: Path to the output directory containing the blog post
        selected_title: Optional title to use (reads from SELECTED_TITLE.txt if not provided)

    Returns:
        (success, message, post_info)
    """
    output_path = Path(output_dir)

    # Read the selected title if not provided
    if not selected_title:
        title_file = output_path / "SELECTED_TITLE.txt"
        if title_file.exists():
            content = title_file.read_text()
            # Extract title from the file
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('='):
                    selected_title = line
                    break

    if not selected_title:
        return False, "No title found", None

    # Read the blog post content
    blog_file = output_path / "linkedin_blog_post.txt"
    if not blog_file.exists():
        return False, f"Blog post file not found: {blog_file}", None

    blog_content = blog_file.read_text()

    print(f"\n📰 Publishing First Cup: {selected_title}")
    print("="*60)

    # Get YouTube video info
    print("  🎬 Finding YouTube video...")
    video = get_youtube_video_for_title(selected_title)

    if not video:
        print("  ⚠️  Could not find matching YouTube video")
        print("  Using most recent video from First Cup playlist...")
        video = get_most_recent_video(FIRST_CUP_PLAYLIST_ID)

    if not video:
        return False, "Could not find YouTube video", None

    print(f"  ✓ Found video: {video['title']}")
    print(f"  ✓ URL: {video['share_url']}")

    # Initialize publisher
    publisher = BlogPublisher()

    if not publisher.is_configured():
        return False, "WordPress credentials not configured. Set WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD in .env", None

    # Test connection
    success, msg = publisher.test_connection()
    if not success:
        return False, f"WordPress connection failed: {msg}", None
    print(f"  ✓ {msg}")

    # Upload thumbnail as featured image
    featured_image_id = publisher.upload_featured_image(
        video['thumbnail_url'],
        selected_title
    )

    # Create the post
    success, message, post_info = publisher.create_post(
        title=f"First Cup: {selected_title}",
        content=blog_content,
        youtube_url=video['share_url'],
        featured_image_id=featured_image_id
    )

    if success:
        print(f"\n✅ Blog post created successfully!")
        print(f"   Edit URL: {post_info['edit_url']}")
        print(f"   Status: {post_info['status']} (review and publish when ready)")

        # Add YouTube info to post_info for Slack notification
        post_info['youtube_url'] = video['share_url']
        post_info['youtube_title'] = video['title']

    return success, message, post_info


def find_most_recent_output():
    """Find the most recent output directory"""
    outputs_dir = Path(__file__).parent / "outputs"
    if not outputs_dir.exists():
        return None

    # Get all output directories sorted by modification time
    dirs = [d for d in outputs_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    if not dirs:
        return None

    # Sort by modification time, most recent first
    dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return dirs[0]


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    # Check for command line argument
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--publish', '-p', 'publish']:
            # Publish the most recent episode
            print("📰 Publishing most recent First Cup episode...")
            print("="*60)

            output_dir = find_most_recent_output()
            if not output_dir:
                print("❌ No output directories found")
                sys.exit(1)

            print(f"📁 Found: {output_dir.name}")

            success, message, post_info = publish_first_cup(str(output_dir))

            if success:
                print(f"\n✅ Success!")
                print(f"   Edit: {post_info['edit_url']}")
            else:
                print(f"\n❌ Failed: {message}")
                sys.exit(1)

            sys.exit(0)

        elif sys.argv[1] in ['--test', '-t', 'test']:
            # Test connections
            pass  # Fall through to test code below

        elif sys.argv[1] in ['--help', '-h', 'help']:
            print("Blog Publisher for First Cup Processor")
            print()
            print("Usage:")
            print("  python blog_publisher.py --publish    Publish most recent episode")
            print("  python blog_publisher.py --test       Test connections")
            print("  python blog_publisher.py --help       Show this help")
            sys.exit(0)

    # Test the publisher
    print("🧪 Blog Publisher Test")
    print("="*60)

    publisher = BlogPublisher()

    if not publisher.is_configured():
        print("\n❌ WordPress credentials not configured")
        print("\nAdd these to your .env file:")
        print("  WP_SITE_URL=https://productcoffee.com")
        print("  WP_USERNAME=your_username")
        print("  WP_APP_PASSWORD=your_app_password")
        print("\nTo create an application password:")
        print("  1. Go to WordPress Dashboard > Users > Profile")
        print("  2. Scroll to 'Application Passwords'")
        print("  3. Enter a name and click 'Add New'")
        sys.exit(1)

    success, message = publisher.test_connection()
    print(f"\nConnection test: {'✅' if success else '❌'} {message}")

    if success:
        # Test YouTube integration
        if YOUTUBE_AVAILABLE:
            print("\n🎬 Testing YouTube integration...")
            video = get_youtube_video_for_title("AI")  # Generic search
            if video:
                print(f"   ✅ Found video: {video['title']}")
                print(f"   URL: {video['share_url']}")
                print(f"   Thumbnail: {video['thumbnail_url']}")
            else:
                print("   ⚠️  Could not fetch YouTube video")
        else:
            print("\n⚠️  YouTube helper not available")
