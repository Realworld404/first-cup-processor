#!/usr/bin/env python3
"""
Lightweight HTTP server for triggering blog publishing via webhook.

This can be triggered by:
- Slack Workflow (emoji reaction → webhook)
- Manual curl request
- Any HTTP client

Usage:
    python publish_webhook.py              # Start server on port 8765
    python publish_webhook.py --port 9000  # Custom port

To trigger publishing:
    curl -X POST http://localhost:8765/publish
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from blog_publisher import publish_first_cup, find_most_recent_output
from slack_helper import SlackHelper

DEFAULT_PORT = 8765


class PublishHandler(BaseHTTPRequestHandler):
    """Handle webhook requests for blog publishing"""

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/publish':
            self.handle_publish()
        elif self.path == '/health':
            self.send_json(200, {"status": "ok"})
        else:
            self.send_json(404, {"error": "Not found"})

    def do_GET(self):
        """Handle GET requests (health check)"""
        if self.path in ['/', '/health']:
            self.send_json(200, {"status": "ok", "service": "first-cup-publisher"})
        else:
            self.send_json(404, {"error": "Not found"})

    def handle_publish(self):
        """Publish the most recent First Cup episode"""
        print("\n📤 Webhook triggered - publishing...")

        # Find most recent output
        output_dir = find_most_recent_output()
        if not output_dir:
            self.send_json(400, {"error": "No output directories found"})
            return

        print(f"   Found: {output_dir.name}")

        # Notify Slack that we're starting
        slack = SlackHelper()
        if slack.is_enabled():
            slack.send_message(
                f"📤 *Publishing via webhook...*\n`{output_dir.name}`",
                in_thread=False
            )

        # Publish
        success, message, post_info = publish_first_cup(str(output_dir))

        if success:
            print(f"   ✅ Success!")

            # Notify Slack
            if slack.is_enabled():
                slack.notify_publish_success(post_info)

            self.send_json(200, {
                "success": True,
                "post_id": post_info.get('id'),
                "edit_url": post_info.get('edit_url'),
                "youtube_url": post_info.get('youtube_url')
            })
        else:
            print(f"   ❌ Failed: {message}")

            # Notify Slack
            if slack.is_enabled():
                slack.notify_publish_error(message)

            self.send_json(500, {"success": False, "error": message})

    def send_json(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"  [{self.log_date_time_string()}] {args[0]}")


def run_server(port=DEFAULT_PORT):
    """Start the webhook server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, PublishHandler)

    print("🚀 First Cup Publisher Webhook Server")
    print("="*50)
    print(f"   Listening on: http://localhost:{port}")
    print(f"   Publish URL:  http://localhost:{port}/publish")
    print()
    print("To trigger publishing:")
    print(f"   curl -X POST http://localhost:{port}/publish")
    print()
    print("Press Ctrl+C to stop")
    print("="*50)
    print()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        httpd.shutdown()


if __name__ == '__main__':
    port = DEFAULT_PORT

    # Check for port argument
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--port', '-p'] and len(sys.argv) > 2:
            port = int(sys.argv[2])
        elif sys.argv[1] in ['--help', '-h']:
            print(__doc__)
            sys.exit(0)
        else:
            try:
                port = int(sys.argv[1])
            except ValueError:
                print(f"Invalid port: {sys.argv[1]}")
                sys.exit(1)

    run_server(port)
