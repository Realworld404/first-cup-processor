#!/usr/bin/env python3
"""Debug script to check what Slack API sees in the channel"""

import json
import requests

# Load config
with open('config.json') as f:
    config = json.load(f)

bot_token = config['slack']['bot_token']
channel_id = config['slack']['user_id']

headers = {"Authorization": f"Bearer {bot_token}"}

# Get recent messages in channel
print("Fetching recent messages from channel...")
response = requests.get(
    "https://slack.com/api/conversations.history",
    headers=headers,
    params={"channel": channel_id, "limit": 5}
)

data = response.json()
if not data.get('ok'):
    print(f"❌ Error: {data.get('error')}")
    exit(1)

print(f"\n✅ Found {len(data.get('messages', []))} recent messages\n")

for i, msg in enumerate(data.get('messages', []), 1):
    print(f"Message {i}:")
    print(f"  From: {msg.get('user', 'bot')} (bot={msg.get('bot_id', 'N/A')})")
    print(f"  Timestamp: {msg.get('ts')}")
    print(f"  Text: {msg.get('text', '')[:100]}...")
    print(f"  Thread replies: {msg.get('reply_count', 0)}")

    # If this has replies, fetch them
    if msg.get('reply_count', 0) > 0 or msg.get('thread_ts'):
        thread_ts = msg.get('thread_ts') or msg.get('ts')
        print(f"\n  Fetching thread replies for ts={thread_ts}...")

        reply_response = requests.get(
            "https://slack.com/api/conversations.replies",
            headers=headers,
            params={"channel": channel_id, "ts": thread_ts}
        )

        reply_data = reply_response.json()
        if reply_data.get('ok'):
            messages = reply_data.get('messages', [])
            print(f"  Thread has {len(messages)} total messages:")
            for j, rmsg in enumerate(messages):
                user = rmsg.get('user', 'N/A')
                text = rmsg.get('text', '')[:80]
                print(f"    {j}. User={user}: {text}")
        else:
            print(f"  ❌ Error fetching replies: {reply_data.get('error')}")

    print()
