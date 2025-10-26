#!/bin/bash

###############################################################################
# First Cup Processor - Launch Agent Installer
#
# This script installs a macOS Launch Agent that automatically triggers
# the First Cup Processor when you add a transcript file to the watched folder.
#
# What it does:
# 1. Creates logs directory
# 2. Configures the Launch Agent plist with your paths and API key
# 3. Installs it to ~/Library/LaunchAgents/
# 4. Loads the agent so it starts watching immediately
#
# Usage:
#   ./install_launch_agent.sh
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_TEMPLATE="$SCRIPT_DIR/com.productcoffee.firstcup.plist"
PLIST_NAME="com.productcoffee.firstcup.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   First Cup Processor - Launch Agent Installer        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if plist template exists
if [ ! -f "$PLIST_TEMPLATE" ]; then
    echo -e "${RED}❌ Error: plist template not found at $PLIST_TEMPLATE${NC}"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  ANTHROPIC_API_KEY environment variable not set${NC}"
    echo ""
    echo "Please enter your Anthropic API key:"
    read -r API_KEY
    if [ -z "$API_KEY" ]; then
        echo -e "${RED}❌ API key cannot be empty${NC}"
        exit 1
    fi
else
    API_KEY="$ANTHROPIC_API_KEY"
    echo -e "${GREEN}✓ Using ANTHROPIC_API_KEY from environment${NC}"
fi

# Get paths from config.json or use defaults
TRANSCRIPTS_DIR="$SCRIPT_DIR/transcripts"
OUTPUTS_DIR="$SCRIPT_DIR/outputs"

if [ -f "$SCRIPT_DIR/config.json" ]; then
    echo -e "${GREEN}✓ Found config.json${NC}"
    # Could parse JSON here, but for simplicity, we'll use the defaults
fi

# Create necessary directories
echo ""
echo -e "${BLUE}📁 Creating directories...${NC}"

mkdir -p "$TRANSCRIPTS_DIR"
echo -e "  ${GREEN}✓${NC} $TRANSCRIPTS_DIR"

mkdir -p "$OUTPUTS_DIR"
echo -e "  ${GREEN}✓${NC} $OUTPUTS_DIR"

mkdir -p "$SCRIPT_DIR/logs"
echo -e "  ${GREEN}✓${NC} $SCRIPT_DIR/logs"

mkdir -p "$LAUNCH_AGENTS_DIR"
echo -e "  ${GREEN}✓${NC} $LAUNCH_AGENTS_DIR"

# Create the plist file with substitutions
echo ""
echo -e "${BLUE}📝 Configuring Launch Agent...${NC}"

# Read the template and substitute placeholders
sed -e "s|SCRIPT_PATH_PLACEHOLDER|$SCRIPT_DIR|g" \
    -e "s|API_KEY_PLACEHOLDER|$API_KEY|g" \
    -e "s|TRANSCRIPTS_PATH_PLACEHOLDER|$TRANSCRIPTS_DIR|g" \
    "$PLIST_TEMPLATE" > "$INSTALLED_PLIST"

echo -e "  ${GREEN}✓${NC} Created $INSTALLED_PLIST"

# Set proper permissions
chmod 644 "$INSTALLED_PLIST"
echo -e "  ${GREEN}✓${NC} Set permissions"

# Unload existing agent if running
if launchctl list | grep -q "com.productcoffee.firstcup"; then
    echo ""
    echo -e "${YELLOW}⚠️  Existing Launch Agent found, unloading...${NC}"
    launchctl unload "$INSTALLED_PLIST" 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Unloaded old agent"
fi

# Load the Launch Agent
echo ""
echo -e "${BLUE}🚀 Loading Launch Agent...${NC}"
launchctl load "$INSTALLED_PLIST"

if launchctl list | grep -q "com.productcoffee.firstcup"; then
    echo -e "  ${GREEN}✓${NC} Launch Agent loaded successfully"
else
    echo -e "${RED}❌ Failed to load Launch Agent${NC}"
    echo "Check the logs at: $SCRIPT_DIR/logs/"
    exit 1
fi

# Install Python dependencies
echo ""
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    python3 -m pip install -r "$SCRIPT_DIR/requirements.txt" --break-system-packages --quiet
    echo -e "  ${GREEN}✓${NC} Dependencies installed"
else
    echo -e "  ${YELLOW}⚠️${NC} requirements.txt not found, skipping"
fi

# Success message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 ✅ Installation Complete!              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}How it works:${NC}"
echo -e "  1. Drop a transcript file into: ${YELLOW}$TRANSCRIPTS_DIR${NC}"
echo -e "  2. The processor automatically runs"
echo -e "  3. Outputs appear in: ${YELLOW}$OUTPUTS_DIR${NC}"
echo ""
echo -e "${BLUE}Monitoring:${NC}"
echo -e "  • Check status: ${YELLOW}launchctl list | grep firstcup${NC}"
echo -e "  • View logs: ${YELLOW}tail -f $SCRIPT_DIR/logs/stdout.log${NC}"
echo -e "  • View errors: ${YELLOW}tail -f $SCRIPT_DIR/logs/stderr.log${NC}"
echo ""
echo -e "${BLUE}Management:${NC}"
echo -e "  • Disable: ${YELLOW}launchctl unload $INSTALLED_PLIST${NC}"
echo -e "  • Re-enable: ${YELLOW}launchctl load $INSTALLED_PLIST${NC}"
echo -e "  • Uninstall: ${YELLOW}rm $INSTALLED_PLIST && launchctl remove com.productcoffee.firstcup${NC}"
echo ""
echo -e "${GREEN}🎉 Ready to process transcripts automatically!${NC}"
echo ""
