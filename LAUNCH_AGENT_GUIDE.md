# Launch Agent Setup Guide

This guide explains how to set up automatic processing using macOS Launch Agents.

## 🎯 What You Get

With the Launch Agent installed:
- ✅ **Automatic triggering** - Drop a transcript file, processing starts immediately
- ✅ **Zero manual intervention** - No need to run scripts manually
- ✅ **Background operation** - Runs without keeping terminal open
- ✅ **Slack notifications** - Get updates on your phone/desktop (if configured)
- ✅ **Persistent** - Survives reboots, runs on login
- ✅ **Zero resource usage when idle** - Only runs when files are added

## 🚀 Quick Installation

### Prerequisites

1. **ANTHROPIC_API_KEY set** (or you'll be prompted):
   ```bash
   export ANTHROPIC_API_KEY='sk-ant-...'
   ```

2. **Slack configured** (optional but recommended):
   - See `SLACK_SETUP_GUIDE.md`
   - Update `config.json` with Slack credentials

### Install

```bash
cd /Users/jasonbrett/developer/productcoffee/first-cup-processor
./install_launch_agent.sh
```

That's it! The installer will:
- ✅ Create necessary directories
- ✅ Install Python dependencies
- ✅ Configure the Launch Agent
- ✅ Start watching for files

---

## 📖 How It Works

### The Flow

1. **You drop a transcript** → `./transcripts/episode_24.txt`
2. **Launch Agent detects** → New file in watched directory
3. **Script runs automatically** → Processes the transcript
4. **Slack notifies you** → "Title options ready!"
5. **You reply in Slack** → Select title or provide feedback
6. **Processing continues** → Generates description & newsletter
7. **Completion notification** → "Processing complete!"
8. **Outputs ready** → `./outputs/episode_24_20251026_153022/`

### macOS Launch Agent

The Launch Agent uses macOS's built-in `launchd` system:
- **WatchPaths** - Monitors `./transcripts/` for new files
- **Throttle** - Prevents rapid-fire triggering (5 second minimum)
- **Background** - Runs without user interaction
- **Logs** - Writes to `./logs/stdout.log` and `./logs/stderr.log`

---

## 🎮 Usage

### Process a Transcript

Just drop a file in the transcripts folder:

```bash
# Copy transcript to watched folder
cp ~/Downloads/my-transcript.txt ./transcripts/

# That's it! Processing starts automatically.
# Check Slack for title options (or check logs if Slack not configured)
```

### Check Status

```bash
# See if Launch Agent is running
launchctl list | grep firstcup

# View live logs
tail -f logs/stdout.log

# View errors
tail -f logs/stderr.log
```

### View Outputs

```bash
# List all processed episodes
ls -la outputs/

# Open latest output
open outputs/$(ls -t outputs/ | head -1)
```

---

## 🔧 Management

### Disable (Temporarily)

```bash
launchctl unload ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
```

Processing will stop until you re-enable it.

### Re-enable

```bash
launchctl load ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
```

### Update Configuration

If you change `config.json` or update the script:

```bash
# Reload the Launch Agent
launchctl unload ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
launchctl load ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
```

### Complete Uninstall

```bash
# Remove Launch Agent
launchctl unload ~/Library/LaunchAgents/com.productcoffee.firstcup.plist
rm ~/Library/LaunchAgents/com.productcoffee.firstcup.plist

# Optionally remove data
rm -rf transcripts/* outputs/* logs/*
```

---

## 🐛 Troubleshooting

### Agent Not Running

**Check if loaded:**
```bash
launchctl list | grep firstcup
```

**If not listed:**
```bash
# Reload it
./install_launch_agent.sh
```

### Files Not Processing

**Check logs for errors:**
```bash
tail -50 logs/stderr.log
```

**Common issues:**
- API key not set or invalid
- Python dependencies not installed
- File permissions issues

**Solution:**
```bash
# Reinstall
./install_launch_agent.sh
```

### Slack Not Working

**If Slack notifications aren't appearing:**

1. Check `config.json`:
   ```json
   "slack": {
     "enabled": true,
     "webhook_url": "https://hooks.slack.com/...",
     "bot_token": "xoxb-...",
     "user_id": "U..."
   }
   ```

2. Test Slack connection:
   ```bash
   python3 youtube_processor.py --test-slack
   ```

3. Check Slack app permissions (see `SLACK_SETUP_GUIDE.md`)

### Processing Hanging

**If the script seems stuck:**

Check if it's waiting for Slack response:
```bash
tail logs/stdout.log
```

If you see "Waiting for your response in Slack...", check your Slack messages and reply.

### Multiple Files Triggering Simultaneously

The Launch Agent has a 5-second throttle to prevent this, but if multiple files are added very quickly:
- They'll be queued
- Processed one at a time
- This is normal behavior

---

## 📊 Monitoring

### View Recent Activity

```bash
# Last 20 log lines
tail -20 logs/stdout.log

# Watch logs in real-time
tail -f logs/stdout.log
```

### Check Processed Files

```bash
# View tracking file
cat outputs/.processed_transcripts.json
```

This lists all files that have been processed (prevents reprocessing).

### Log Rotation

Logs can grow large over time. To clear them:

```bash
# Clear logs (keeps files)
> logs/stdout.log
> logs/stderr.log

# Or delete and recreate
rm logs/*.log
mkdir -p logs
```

---

## 🎯 Tips & Best Practices

### File Naming

Use descriptive names for transcripts:
```
✅ Good: Product-Coffee-2025-10-26-First-Cup.txt
❌ Bad: transcript.txt
```

Outputs will use the filename as the base name.

### Batch Processing

If you have multiple transcripts:

```bash
# Process them one at a time (recommended)
cp transcript1.txt ./transcripts/
# Wait for completion notification in Slack

cp transcript2.txt ./transcripts/
# Wait for completion...
```

Or copy all at once - they'll be queued and processed sequentially.

### Backup Outputs

Outputs are saved locally. Consider backing them up:

```bash
# Create backup
zip -r outputs-backup-$(date +%Y%m%d).zip outputs/

# Or use Time Machine / cloud backup
```

### Testing

Test with the sample transcript:

```bash
cp sample_transcript.txt ./transcripts/test-$(date +%s).txt
```

Watch logs to verify it processes correctly.

---

## 🔐 Security

### API Keys

The Launch Agent stores your API key in the plist file:
- Located at: `~/Library/LaunchAgents/com.productcoffee.firstcup.plist`
- Only readable by your user account
- Not committed to git

### Slack Tokens

Slack credentials are in `config.json`:
- Ignored by git (in `.gitignore`)
- Only readable by your user account
- Never share this file

### Rotate Keys

If you need to rotate API keys or Slack tokens:

1. Update environment variable or `config.json`
2. Reinstall Launch Agent:
   ```bash
   ./install_launch_agent.sh
   ```

---

## 📚 Advanced

### Custom Paths

To use different directories, edit `config.json`:

```json
{
  "directories": {
    "transcripts": "/custom/path/transcripts",
    "outputs": "/custom/path/outputs"
  }
}
```

Then reinstall the Launch Agent.

### Multiple Instances

You can run multiple instances for different projects:

1. Copy the project folder
2. Edit `config.json` with different paths
3. Edit `com.productcoffee.firstcup.plist` and change the Label
4. Install with a different name

### Integration with Other Tools

The Launch Agent can trigger other automations:
- Hazel rules on the outputs folder
- Shortcuts that run when outputs are created
- AppleScript to open files automatically

---

## 🆘 Getting Help

**Logs show errors?**
- Check `SETUP_GUIDE.md` for configuration help
- Verify API key is valid
- Ensure Python dependencies are installed

**Slack not working?**
- See `SLACK_SETUP_GUIDE.md`
- Test with `python3 youtube_processor.py --test-slack`

**Launch Agent won't load?**
- Check syntax: `plutil ~/Library/LaunchAgents/com.productcoffee.firstcup.plist`
- View system logs: `log show --predicate 'subsystem == "com.apple.launchd"' --last 1h`

---

## ✅ Verification Checklist

After installation, verify everything works:

- [ ] Launch Agent is loaded: `launchctl list | grep firstcup`
- [ ] Logs directory exists: `ls logs/`
- [ ] Slack test passes (if configured): `python3 youtube_processor.py --test-slack`
- [ ] Sample transcript processes: `cp sample_transcript.txt transcripts/test.txt`
- [ ] Outputs appear: `ls outputs/`
- [ ] Slack notifications received (if configured)

---

**Ready to use!** Just drop transcripts in `./transcripts/` and watch the magic happen. 🎉
