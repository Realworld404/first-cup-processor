"""
Slack Integration Helper for First Cup Processor

Handles all Slack communication:
- Sending notifications
- Posting title options
- Polling for user responses
- Error notifications
"""

import os
import time
import json
import requests
from datetime import datetime, timedelta


class SlackHelper:
    def __init__(self, webhook_url=None, bot_token=None, user_id=None):
        """Initialize Slack helper with credentials"""
        self.webhook_url = webhook_url or os.environ.get('SLACK_WEBHOOK_URL', '')
        self.bot_token = bot_token or os.environ.get('SLACK_BOT_TOKEN', '')
        self.user_id = user_id or os.environ.get('SLACK_USER_ID', '')
        self.enabled = bool(self.webhook_url and self.bot_token and self.user_id)
        self.last_message_ts = None  # Track message timestamp for threading
        self.thread_ts = None  # Track the main thread timestamp for entire conversation
        self.last_output_path = None  # Track the output path for publish command
        self.last_selected_title = None  # Track the selected title for publish command
        self.publish_callback = None  # Callback function for handling publish commands

    def is_enabled(self):
        """Check if Slack integration is properly configured"""
        return self.enabled

    def start_new_thread(self):
        """Reset thread tracking for a new processing session"""
        self.thread_ts = None
        self.last_message_ts = None

    def send_webhook(self, text, blocks=None):
        """Send message via webhook (simple, no threading)"""
        if not self.webhook_url:
            return False

        payload = {"text": text}
        if blocks:
            payload["blocks"] = blocks

        try:
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Slack webhook error: {e}")
            return False

    def send_message(self, text, blocks=None, channel=None, in_thread=True):
        """Send message using bot token (supports threading)"""
        if not self.bot_token:
            return None

        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "channel": channel or self.user_id,
            "text": text
        }

        if blocks:
            payload["blocks"] = blocks

        # Add to thread if we have a thread_ts and in_thread is True
        if in_thread and self.thread_ts:
            payload["thread_ts"] = self.thread_ts

        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()

            if data.get("ok"):
                # Store message timestamp
                self.last_message_ts = data.get("ts")

                # If this is the first message (no thread_ts yet), set it as the thread root
                if not self.thread_ts:
                    self.thread_ts = data.get("ts")

                return data
            else:
                print(f"❌ Slack API error: {data.get('error')}")
                return None
        except Exception as e:
            print(f"❌ Slack message error: {e}")
            return None

    def notify_processing_start(self, filename):
        """Notify that processing has started"""
        text = f"🎬 *First Cup Processor*\n\nProcessing: `{filename}`\nStatus: Generating title options..."
        self.send_message(text)

    def send_title_options(self, titles, filename):
        """Send title options and request selection"""
        title_list = "\n".join([f"{i}. {title}" for i, title in enumerate(titles, 1)])

        text = f"""📝 *Title Options Ready!*

{title_list}

*Reply with:*
• A number (1-5) to select that title
• 'f' followed by feedback for new titles
• 'TITLE: Your Custom Title Here'

_Waiting for your response..._"""

        self.send_message(text)
        # Return the THREAD timestamp, not the message timestamp
        # This is needed for polling replies
        return self.thread_ts

    def poll_for_response(self, message_ts=None, timeout_seconds=None, allow_publish=False):
        """
        Poll Slack for user's response to title selection in the thread
        Returns: (response_text, response_type) or (None, None) if timeout
        response_type: 'number', 'feedback', 'custom_title', 'publish', or 'timeout'

        Args:
            message_ts: Specific message timestamp to poll from
            timeout_seconds: Optional timeout (None = wait forever)
            allow_publish: If True, also listen for 'publish' command
        """
        if not self.bot_token:
            return None, None

        # Use thread_ts if no specific message_ts provided
        thread_ts_to_use = message_ts or self.thread_ts
        if not thread_ts_to_use:
            return None, None

        url = "https://slack.com/api/conversations.replies"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
        }

        params = {
            "channel": self.user_id,
            "ts": thread_ts_to_use,
            "limit": 10
        }

        start_time = datetime.now()
        poll_interval = 5  # Check every 5 seconds
        processed_messages = set()  # Track messages we've already processed

        print("  ⏳ Waiting for your response in Slack...")

        while True:
            # Check for timeout
            if timeout_seconds:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > timeout_seconds:
                    return None, 'timeout'

            try:
                response = requests.get(url, headers=headers, params=params)
                data = response.json()

                if data.get("ok") and data.get("messages"):
                    messages = data["messages"]

                    # Skip the original message, look for replies
                    for msg in messages[1:]:  # Skip first message (our prompt)
                        msg_ts = msg.get("ts", "")

                        # Skip already processed messages
                        if msg_ts in processed_messages:
                            continue

                        # Check if message is from a user (not bot)
                        if msg.get("user") and not msg.get("bot_id"):
                            reply_text = msg.get("text", "").strip()
                            processed_messages.add(msg_ts)

                            # Detect response type
                            if reply_text.lower().startswith('title:'):
                                return reply_text[6:].strip(), 'custom_title'
                            elif reply_text.lower() == 'publish' and allow_publish:
                                return reply_text, 'publish'
                            elif reply_text.lower() == 'f' or reply_text.lower().startswith('f '):
                                feedback = reply_text[1:].strip() if len(reply_text) > 1 else ""
                                return feedback, 'feedback'
                            elif reply_text.isdigit() and 1 <= int(reply_text) <= 5:
                                return reply_text, 'number'
                            else:
                                # Invalid response, send help message
                                help_text = "⚠️ Invalid response. Please reply with:\n• A number (1-5)\n• 'f' for feedback\n• 'TITLE: Your Title'"
                                if allow_publish:
                                    help_text += "\n• 'publish' to post to blog"
                                self.send_message(help_text, channel=self.user_id)

            except Exception as e:
                print(f"  ⚠️ Error polling Slack: {e}")

            # Wait before next poll
            time.sleep(poll_interval)

    def notify_title_selected(self, title):
        """Notify that title was selected"""
        text = f"✅ *Selected Title*\n`{title}`\n\n📝 Generating description and newsletter..."
        self.send_message(text)

    def notify_generating_new_titles(self):
        """Notify that new titles are being generated"""
        text = "🔄 Generating new titles based on your feedback..."
        self.send_message(text)

    def notify_completion(self, output_path, filename):
        """Notify that processing is complete"""
        # Store output path for potential publish command
        self.last_output_path = output_path

        text = f"""✅ *Processing Complete!*

📁 Outputs saved to:
`{output_path}`

*Files created:*
• SELECTED_TITLE.txt
• youtube_description.txt
• newsletter_teaser.txt
• linkedin_blog_post.txt
• keywords.txt
• description_components.txt

Ready to use! 🎉

💡 *To publish to Product Coffee blog:*
• React with 📤 on this message, OR
• Reply with `publish`

_You have 24 hours to publish._"""
        self.send_message(text)

    def notify_error(self, filename, error_message):
        """Notify that an error occurred"""
        text = f"""❌ *Error Processing Transcript*

File: `{filename}`
Error: `{error_message}`

Please check your configuration and try again."""
        self.send_message(text)

    def notify_cancelled(self, filename):
        """Notify that processing was cancelled"""
        text = f"""⚠️ *Processing Cancelled*

File: `{filename}`

The transcript was not processed."""
        self.send_message(text)

    def test_connection(self):
        """Test Slack connection and send a test message"""
        if not self.is_enabled():
            return False, "Slack not configured. Check config.json or environment variables."

        test_text = f"""🧪 *Slack Integration Test*

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: ✅ Connected

Your First Cup Processor Slack integration is working!"""

        result = self.send_message(test_text)

        if result:
            return True, "Test message sent successfully!"
        else:
            return False, "Failed to send test message. Check your tokens and permissions."

    def notify_publish_started(self):
        """Notify that blog publishing has started"""
        text = "📤 *Publishing to Product Coffee blog...*\n\nThis may take a moment..."
        self.send_message(text)

    def notify_publish_success(self, post_info):
        """Notify that blog post was published successfully"""
        text = f"""✅ *Blog Post Created!*

📝 *Title:* First Cup: {post_info.get('youtube_title', 'Episode')}
🔗 *Edit URL:* {post_info.get('edit_url', 'N/A')}
📺 *YouTube:* {post_info.get('youtube_url', 'N/A')}
📊 *Status:* Draft (ready for review)

The post has been created as a draft. Review and publish it when ready!"""
        self.send_message(text)

    def notify_publish_error(self, error_message):
        """Notify that blog publishing failed"""
        text = f"""❌ *Blog Publishing Failed*

Error: `{error_message}`

Please check WordPress credentials and try again."""
        self.send_message(text)

    def set_publish_callback(self, callback):
        """
        Set a callback function to handle publish commands.
        The callback should accept (output_path, selected_title) and return (success, message, post_info).
        """
        self.publish_callback = callback

    def check_for_publish_command(self):
        """
        Non-blocking check for publish command in the current thread.
        Called during idle periods (e.g., while watching for new files).

        Returns: True if publish was handled, False otherwise
        """
        if not self.is_enabled() or not self.thread_ts or not self.last_output_path:
            return False

        if not self.publish_callback:
            return False

        # Quick non-blocking check for new messages
        url = "https://slack.com/api/conversations.replies"
        headers = {"Authorization": f"Bearer {self.bot_token}"}
        params = {
            "channel": self.user_id,
            "ts": self.thread_ts,
            "limit": 10
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            data = response.json()

            if data.get("ok") and data.get("messages"):
                messages = data["messages"]

                # Look for publish command in recent messages
                for msg in messages[1:]:  # Skip first message (our original)
                    if msg.get("user") and not msg.get("bot_id"):
                        reply_text = msg.get("text", "").strip().lower()

                        if reply_text == 'publish':
                            # Found publish command - execute it
                            print("\n  📤 Publish command received!")
                            self.notify_publish_started()

                            success, message, post_info = self.publish_callback(
                                self.last_output_path,
                                self.last_selected_title
                            )

                            if success:
                                self.notify_publish_success(post_info)
                            else:
                                self.notify_publish_error(message)

                            # Clear the stored data so we don't publish again
                            self.last_output_path = None
                            self.last_selected_title = None
                            self.thread_ts = None

                            return True

        except Exception as e:
            # Silent fail - this is a non-blocking check
            pass

        return False

    def check_for_emoji_reaction(self, emoji_name="outbox_tray"):
        """
        Check if a specific emoji reaction was added to the completion message.
        Default emoji is 📤 (outbox_tray).

        Args:
            emoji_name: Slack emoji name without colons (e.g., 'outbox_tray' for 📤)

        Returns: True if the emoji reaction was found, False otherwise
        """
        if not self.is_enabled() or not self.last_message_ts:
            return False

        url = "https://slack.com/api/reactions.get"
        headers = {"Authorization": f"Bearer {self.bot_token}"}
        params = {
            "channel": self.user_id,
            "timestamp": self.last_message_ts
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            data = response.json()

            if data.get("ok") and data.get("message", {}).get("reactions"):
                reactions = data["message"]["reactions"]

                for reaction in reactions:
                    if reaction.get("name") == emoji_name:
                        return True

        except Exception as e:
            # Silent fail - this is a non-blocking check
            pass

        return False

    def get_completion_message_info(self):
        """
        Get information needed for the publish poller to monitor for reactions.

        Returns: dict with channel, message_ts, thread_ts, output_path, selected_title
                 or None if not available
        """
        if not self.last_message_ts or not self.last_output_path:
            return None

        return {
            "channel": self.user_id,
            "message_ts": self.last_message_ts,
            "thread_ts": self.thread_ts,
            "output_path": self.last_output_path,
            "selected_title": self.last_selected_title
        }

    def save_poller_state(self, filepath):
        """
        Save the state needed for the publish poller to a JSON file.
        This allows a separate process to pick up and monitor for publish triggers.

        Args:
            filepath: Path to save the state file
        """
        state = self.get_completion_message_info()
        if not state:
            return False

        state["created_at"] = datetime.now().isoformat()

        try:
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            print(f"  ⚠️ Error saving poller state: {e}")
            return False
