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

    def is_enabled(self):
        """Check if Slack integration is properly configured"""
        return self.enabled

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

    def send_message(self, text, blocks=None, channel=None):
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

        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()

            if data.get("ok"):
                # Store message timestamp for threading
                self.last_message_ts = data.get("ts")
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
        return self.last_message_ts  # Return timestamp for polling

    def poll_for_response(self, message_ts, timeout_seconds=None):
        """
        Poll Slack for user's response to title selection
        Returns: (response_text, response_type) or (None, None) if timeout
        response_type: 'number', 'feedback', 'custom_title', or 'timeout'
        """
        if not self.bot_token or not message_ts:
            return None, None

        url = "https://slack.com/api/conversations.replies"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
        }

        params = {
            "channel": self.user_id,
            "ts": message_ts,
            "limit": 10
        }

        start_time = datetime.now()
        poll_interval = 5  # Check every 5 seconds

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
                        # Check if message is from a user (not bot)
                        if msg.get("user") and not msg.get("bot_id"):
                            reply_text = msg.get("text", "").strip()

                            # Detect response type
                            if reply_text.lower().startswith('title:'):
                                return reply_text[6:].strip(), 'custom_title'
                            elif reply_text.lower() == 'f' or reply_text.lower().startswith('f '):
                                feedback = reply_text[1:].strip() if len(reply_text) > 1 else ""
                                return feedback, 'feedback'
                            elif reply_text.isdigit() and 1 <= int(reply_text) <= 5:
                                return reply_text, 'number'
                            else:
                                # Invalid response, send help message
                                self.send_message(
                                    "⚠️ Invalid response. Please reply with:\n• A number (1-5)\n• 'f' for feedback\n• 'TITLE: Your Title'",
                                    channel=self.user_id
                                )

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
        text = f"""✅ *Processing Complete!*

📁 Outputs saved to:
`{output_path}`

*Files created:*
• SELECTED_TITLE.txt
• youtube_description.txt
• newsletter_article.txt
• keywords.txt
• description_components.txt

Ready to use! 🎉"""
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
