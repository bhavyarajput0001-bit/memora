#!/bin/bash
# MEMORA Timetable Import Script - Quick Start
# This script automates the process of importing your class schedule to Google Calendar

echo "=========================================="
echo "MEMORA Timetable Import Helper"
echo "=========================================="
echo ""

# Check if Composio is installed
if ! command -v composio &> /dev/null; then
    echo "❌ Composio CLI is not installed."
    echo "   Please install it first: curl -fsSL https://composio.dev/install | sh"
    exit 1
fi

# Check login status
echo "📋 Checking Composio status..."
if ! composio whoami &> /dev/null; then
    echo "⚠️  Not logged in to Composio."
    echo ""
    echo "   Please run: composio login"
    echo "   Then re-run this script."
    exit 1
fi
echo "✅ Composio is logged in"

# Connect to Google Calendar
echo ""
echo "📅 Connecting to Google Calendar..."
echo "   Running: composio link google_calendar"
echo ""
composio link google_calendar

if [ $? -ne 0 ]; then
    echo "⚠️  Failed to connect to Google Calendar."
    echo "   Please complete the OAuth flow manually."
    exit 1
fi
echo "✅ Google Calendar connected"

# Run the Python import script
echo ""
echo "📋 Running timetable import..."
python3 "$(dirname "$0")/import_timetable.py"

echo ""
echo "=========================================="
echo "Import complete!"
echo "=========================================="