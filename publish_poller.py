#!/usr/bin/env python3
"""
Publish Poller - Standalone daemon that monitors Slack for publish triggers.

This process runs in the background after transcript processing completes,
polling Slack every minute for either:
- An emoji reaction (📤) on the completion message
- A "publish" text reply in the thread

The process automatically terminates after:
- Successfully publishing the blog post
- 24 hours have elapsed (timeout)
- The state file is deleted (manual cancellation)

Usage:
    python publish_poller.py                    # Uses default state file
    python publish_poller.py --state /path/to/state.json
    python publish_poller.py --timeout 12       # 12 hours instead of 24

State File Format (JSON):
{
    "channel": "U01234567890",
    "message_ts": "1234567890.123456",
    "thread_ts": "1234567890.123456",
    "output_path": "/path/to/outputs/episode_name",
    "selected_title": "The Episode Title",
    "created_at": "2025-12-04T10:30:00"
}
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from blog_publisher import publish_first_cup
from slack_helper import SlackHelper

# Configuration
DEFAULT_STATE_FILE = Path(__file__).parent / ".publish_poller_state.json"
DEFAULT_POLL_INTERVAL = 60  # 1 minute
DEFAULT_TIMEOUT_HOURS = 24
PUBLISH_EMOJI = "outbox_tray"  # 📤


def load_state(state_file):
    """Load poller state from JSON file"""
    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing state file: {e}")
        return None


def delete_state(state_file):
    """Delete state file after completion"""
    try:
        os.remove(state_file)
        print(f"  🗑️ Cleaned up state file")
    except Exception as e:
        print(f"  ⚠️ Could not delete state file: {e}")


def check_for_emoji_reaction(channel, message_ts, bot_token, emoji_name=PUBLISH_EMOJI):
    """Check if a specific emoji reaction was added to the message"""
    url = "https://slack.com/api/reactions.get"
    headers = {"Authorization": f"Bearer {bot_token}"}
    params = {
        "channel": channel,
        "timestamp": message_ts
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes

        try:
            data = response.json()
        except ValueError as e:
            print(f"  ⚠️ Invalid JSON response from Slack API: {e}")
            print(f"  Response content: {response.text[:200]}")
            return False

        if data.get("ok") and data.get("message", {}).get("reactions"):
            reactions = data["message"]["reactions"]
            for reaction in reactions:
                if reaction.get("name") == emoji_name:
                    return True
        elif not data.get("ok"):
            error = data.get("error", "unknown")
            if error != "no_reaction":  # no_reaction is expected when no reactions exist
                print(f"  ⚠️ Slack API error: {error}")

    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ HTTP request error: {e}")
    except Exception as e:
        print(f"  ⚠️ Error checking reactions: {e}")

    return False


def check_for_publish_reply(channel, thread_ts, bot_token):
    """Check if someone replied 'publish' in the thread"""
    url = "https://slack.com/api/conversations.replies"
    headers = {"Authorization": f"Bearer {bot_token}"}
    params = {
        "channel": channel,
        "ts": thread_ts,
        "limit": 20
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes

        try:
            data = response.json()
        except ValueError as e:
            print(f"  ⚠️ Invalid JSON response from Slack API: {e}")
            print(f"  Response content: {response.text[:200]}")
            return False

        if data.get("ok") and data.get("messages"):
            messages = data["messages"]

            # Skip the original message, look for replies
            for msg in messages[1:]:
                if msg.get("user") and not msg.get("bot_id"):
                    reply_text = msg.get("text", "").strip().lower()
                    if reply_text == "publish":
                        return True

    except Exception as e:
        print(f"  ⚠️ Error checking replies: {e}")

    return False


def send_slack_notification(bot_token, channel, thread_ts, message):
    """Send a notification to Slack"""
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": message,
        "thread_ts": thread_ts
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json().get("ok", False)
    except Exception as e:
        print(f"  ⚠️ Error sending Slack message: {e}")
        return False


def run_poller(state_file, poll_interval=DEFAULT_POLL_INTERVAL, timeout_hours=DEFAULT_TIMEOUT_HOURS):
    """Main polling loop"""
    print("📤 First Cup Publish Poller")
    print("=" * 50)

    # Load state
    state = load_state(state_file)
    if not state:
        print(f"❌ No state file found at: {state_file}")
        print("   The poller needs a state file to know what to monitor.")
        sys.exit(1)

    # Extract state values
    channel = state.get("channel")
    message_ts = state.get("message_ts")
    thread_ts = state.get("thread_ts")
    output_path = state.get("output_path")
    selected_title = state.get("selected_title")
    created_at = state.get("created_at")

    # Validate state
    if not all([channel, message_ts, output_path]):
        print("❌ Invalid state file - missing required fields")
        sys.exit(1)

    # Get bot token
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not set in environment")
        sys.exit(1)

    # Calculate timeout
    start_time = datetime.now()
    if created_at:
        try:
            start_time = datetime.fromisoformat(created_at)
        except:
            pass
    timeout_at = start_time + timedelta(hours=timeout_hours)

    print(f"   Output: {Path(output_path).name}")
    print(f"   Title: {selected_title or 'Unknown'}")
    print(f"   Polling: Every {poll_interval} seconds")
    print(f"   Timeout: {timeout_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Waiting for publish trigger...")
    print("   • React with 📤 on the completion message")
    print("   • Or reply 'publish' in the thread")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 50)
    print()

    poll_count = 0

    try:
        while True:
            poll_count += 1

            # Check for timeout
            if datetime.now() > timeout_at:
                print(f"\n⏰ Timeout reached ({timeout_hours} hours)")
                print("   Poller shutting down. You can manually publish with:")
                print(f"   python blog_publisher.py --publish")
                delete_state(state_file)
                sys.exit(0)

            # Check if state file was deleted (manual cancellation)
            if not os.path.exists(state_file):
                print("\n🛑 State file removed - shutting down")
                sys.exit(0)

            # Log progress periodically (every 10 polls = ~10 minutes)
            if poll_count % 10 == 0:
                remaining = timeout_at - datetime.now()
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                print(f"  ⏳ Still waiting... ({hours}h {minutes}m remaining)")

            # Check for emoji reaction
            if check_for_emoji_reaction(channel, message_ts, bot_token):
                print("\n📤 Publish emoji detected!")
                break

            # Check for text reply
            if thread_ts and check_for_publish_reply(channel, thread_ts, bot_token):
                print("\n📤 Publish reply detected!")
                break

            # Wait before next poll
            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\n\n👋 Poller stopped by user")
        print("   State file preserved - restart to continue monitoring")
        sys.exit(0)

    # Trigger publish
    print("\n" + "=" * 50)
    print("🚀 Publishing blog post...")
    print("=" * 50)

    # Notify Slack that we're starting
    send_slack_notification(
        bot_token, channel, thread_ts,
        "📤 *Publishing to Product Coffee blog...*\n\nThis may take a moment..."
    )

    # Publish
    success, message, post_info = publish_first_cup(output_path, selected_title)

    if success:
        print(f"\n✅ Blog post created successfully!")
        print(f"   Edit URL: {post_info.get('edit_url')}")

        # Notify Slack
        success_msg = f"""✅ *Blog Post Created!*

📝 *Title:* First Cup: {post_info.get('youtube_title', selected_title or 'Episode')}
🔗 *Edit URL:* {post_info.get('edit_url', 'N/A')}
📺 *YouTube:* {post_info.get('youtube_url', 'N/A')}
📊 *Status:* Draft (ready for review)

The post has been created as a draft. Review and publish it when ready!"""
        send_slack_notification(bot_token, channel, thread_ts, success_msg)

    else:
        print(f"\n❌ Publishing failed: {message}")

        # Notify Slack
        error_msg = f"""❌ *Blog Publishing Failed*

Error: `{message}`

You can retry manually with:
`python blog_publisher.py --publish`"""
        send_slack_notification(bot_token, channel, thread_ts, error_msg)

    # Cleanup
    delete_state(state_file)
    print("\n👋 Poller finished")


def main():
    parser = argparse.ArgumentParser(
        description="Poll Slack for publish triggers after transcript processing"
    )
    parser.add_argument(
        "--state", "-s",
        type=str,
        default=str(DEFAULT_STATE_FILE),
        help=f"Path to state file (default: {DEFAULT_STATE_FILE})"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=DEFAULT_POLL_INTERVAL,
        help=f"Poll interval in seconds (default: {DEFAULT_POLL_INTERVAL})"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=DEFAULT_TIMEOUT_HOURS,
        help=f"Timeout in hours (default: {DEFAULT_TIMEOUT_HOURS})"
    )

    args = parser.parse_args()
    run_poller(args.state, args.interval, args.timeout)


if __name__ == "__main__":
    main()
