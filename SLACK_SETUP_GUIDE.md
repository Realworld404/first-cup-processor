# Slack Integration Setup Guide

This guide will walk you through setting up the Slack app for First Cup Processor automation.

## Overview

The Slack integration allows you to:
- 📬 Receive title options in Slack when a transcript is processed
- 💬 Reply with your choice directly in Slack
- 📊 Get processing status updates
- ❌ Receive error notifications
- ✅ Get completion notifications with file links

---

## Part 1: Create Slack App (5 minutes)

### Step 1: Go to Slack API Dashboard

1. Open your browser and go to: https://api.slack.com/apps
2. Click **"Create New App"**
3. Choose **"From scratch"**

### Step 2: Configure Basic Information

1. **App Name**: `First Cup Processor` (or any name you prefer)
2. **Workspace**: Select `Product Coffee` (productcoffeeshop.slack.com)
3. Click **"Create App"**

### Step 3: Enable Incoming Webhooks

1. In the left sidebar, click **"Incoming Webhooks"**
2. Toggle the switch to **"On"**
3. Scroll down and click **"Add New Webhook to Workspace"**
4. Select the channel where you want notifications (e.g., `#first-cup` or DM yourself)
5. Click **"Allow"**
6. **COPY the Webhook URL** - it looks like:
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```
7. **Save this URL** - you'll need it in a moment!

### Step 4: Add Bot Token Scopes

1. In the left sidebar, click **"OAuth & Permissions"**
2. Scroll down to **"Scopes"** → **"Bot Token Scopes"**
3. Click **"Add an OAuth Scope"** and add these scopes:
   - `chat:write` - Send messages
   - `channels:history` - Read channel messages
   - `channels:read` - View channel info
   - `groups:history` - Read private channel messages (if using private channel)
   - `im:history` - Read DM messages (if using DMs)
   - `users:read` - Read user info

### Step 5: Install App to Workspace

1. Scroll to the top of the **"OAuth & Permissions"** page
2. Click **"Install to Workspace"**
3. Click **"Allow"**
4. **COPY the "Bot User OAuth Token"** - it starts with `xoxb-`
   ```
   xoxb-YOUR-BOT-TOKEN-HERE
   ```
5. **Save this token** - you'll need it!

### Step 6: Find Your User ID (for DMs)

**Option A: From Slack Desktop/Web**
1. Click your profile picture in Slack
2. Click **"Profile"**
3. Click the **"⋯ More"** button
4. Click **"Copy member ID"**
5. You'll get something like: `U01234ABCDE`

**Option B: Use Slack API**
1. Go to: https://api.slack.com/methods/users.list/test
2. Select your app token
3. Click **"Test Method"**
4. Find your name in the response and copy your `id`

---

## Part 2: Configure First Cup Processor

Now you have:
- ✅ Webhook URL
- ✅ Bot User OAuth Token
- ✅ Your User ID (or channel ID)

### Add Credentials to .env File

Edit your `.env` file in the project directory:

```bash
# Edit .env file
nano .env

# Add these lines (replace with your actual values):
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
SLACK_BOT_TOKEN=xoxb-YOUR-BOT-TOKEN-HERE
SLACK_USER_ID=U01234ABCDE
```

**Note:** You can use either a User ID (for DMs) or Channel ID (for channel posts). The example above uses a User ID.

### Enable Slack in config.json

Edit `config.json` and set Slack to enabled:

```json
{
  "slack": {
    "enabled": true
  }
}
```

That's it! All your secrets are safely in `.env` (which is not committed to git), and your configuration is clean.

---

## Part 3: Test the Integration

Once the code is updated, you can test with:

```bash
python3 youtube_processor.py --test-slack
```

This will send a test message to your Slack channel/DM.

---

## Slack Message Flow

### When you drop a transcript:

**1. Processing Started**
```
🎬 First Cup Processor
Processing: episode_24_transcript.txt
Status: Generating title options...
```

**2. Title Selection**
```
📝 Title Options Ready!

1. AI Agents: The Future of Productivity in 2025
2. Why This Year Is the Year AI Gets Autonomous
3. Stop Using AI Tools Wrong (Here's the Right Way)
4. The Agent Mindset: Next-Level AI Productivity
5. AI Agents Will Transform Your Workflow (Ready?)

Reply with:
• A number (1-5) to select that title
• 'f' followed by feedback for new titles
• 'TITLE: Your Custom Title Here'

Waiting for your response...
```

**3. You Reply in Thread**
```
3
```

**4. Processing Continues**
```
✅ Selected: Stop Using AI Tools Wrong (Here's the Right Way)
📝 Generating description and newsletter...
```

**5. Completion**
```
✅ Processing Complete!

📁 Outputs saved to:
/Users/jasonbrett/developer/productcoffee/first-cup-processor/outputs/episode_24_20251026_153022/

Files created:
• SELECTED_TITLE.txt
• youtube_description.txt
• newsletter_article.txt
• keywords.txt
• description_components.txt
```

### If there's an error:

```
❌ Error Processing Transcript

File: episode_24_transcript.txt
Error: API key invalid

Please check your configuration and try again.
```

---

## Troubleshooting

### "Message not sending"
- Verify webhook URL is correct
- Check that the app is installed in your workspace
- Ensure the channel/user ID is correct

### "Can't read replies"
- Verify bot token is correct
- Check that bot has required scopes
- Ensure bot is in the channel (invite it: `/invite @First Cup Processor`)

### "Rate limited"
- Slack has rate limits (1 message per second)
- The processor includes delays to prevent this

### "Messages appear in wrong channel"
- Update `SLACK_USER_ID` to the correct channel or user ID
- Use `C0123456` for public channels
- Use `U0123456` for DMs
- Use `G0123456` for private channels

---

## Security Notes

⚠️ **Never commit tokens to git!**
- Use environment variables
- Or add to `config.json` and ensure it's in `.gitignore` (already done)
- Rotate tokens if accidentally exposed

---

## Next Steps

Once you've completed the Slack setup:
1. ✅ Set environment variables or update config.json
2. ✅ Test the integration
3. ✅ Set up the Launch Agent (see LAUNCH_AGENT_SETUP.md)
4. ✅ Drop a transcript and watch the magic!

---

**Need Help?**
- Slack API Docs: https://api.slack.com/
- Testing Messages: Use https://api.slack.com/methods/chat.postMessage/test
- Scopes Reference: https://api.slack.com/scopes
