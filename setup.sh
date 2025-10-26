#!/bin/bash

# YouTube Transcript Processor - Quick Setup Script
#
# Copyright (C) 2025 Jason Brett
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

echo "=================================="
echo "YouTube Transcript Processor Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Check for API key
echo "Checking for ANTHROPIC_API_KEY..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set in environment"
    echo ""
    read -p "Enter your Anthropic API key: " API_KEY
    export ANTHROPIC_API_KEY="$API_KEY"
    
    # Ask if user wants to persist
    read -p "Add to ~/.bashrc for persistence? (y/n): " PERSIST
    if [ "$PERSIST" = "y" ]; then
        echo "" >> ~/.bashrc
        echo "# Anthropic API Key for YouTube Processor" >> ~/.bashrc
        echo "export ANTHROPIC_API_KEY='$API_KEY'" >> ~/.bashrc
        echo "✓ Added to ~/.bashrc"
    fi
else
    echo "✓ ANTHROPIC_API_KEY found"
fi
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --break-system-packages
echo ""

# Create directories
echo "Creating directories..."
mkdir -p ~/youtube_transcripts
mkdir -p ~/youtube_outputs
echo "✓ Created ~/youtube_transcripts"
echo "✓ Created ~/youtube_outputs"
echo ""

# Make script executable
chmod +x youtube_processor.py
echo "✓ Made youtube_processor.py executable"
echo ""

# Copy sample transcript
if [ -f sample_transcript.txt ]; then
    echo "Would you like to test with the sample transcript? (y/n)"
    read -p "> " TEST
    if [ "$TEST" = "y" ]; then
        cp sample_transcript.txt ~/youtube_transcripts/
        echo "✓ Copied sample transcript to ~/youtube_transcripts/"
        echo ""
        echo "Starting processor..."
        echo "The sample will be processed automatically."
        echo "Press Ctrl+C to stop when done."
        echo ""
        sleep 2
        python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs
    fi
fi

echo ""
echo "=================================="
echo "Setup complete! 🎉"
echo "=================================="
echo ""
echo "Usage:"
echo "  python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs"
echo ""
echo "Drop transcript files (.txt, .md, .json) into:"
echo "  ~/youtube_transcripts/"
echo ""
echo "Find outputs in:"
echo "  ~/youtube_outputs/"
echo ""
echo "To run in background:"
echo "  screen -S youtube-processor"
echo "  python3 youtube_processor.py ~/youtube_transcripts ~/youtube_outputs"
echo "  (Press Ctrl+A then D to detach)"
echo ""