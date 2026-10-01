#!/usr/bin/env python3
"""
MEMORA Timetable Import Script
Parses timetable.jpeg and creates Google Calendar events via Composio
"""
import subprocess
import json
import sys
import os
from datetime import datetime, timedelta

# Timetable data extracted from OCR
SCHEDULE = [
    # Monday classes
    {
        "day": "Monday",
        "start_time": "10:10",
        "end_time": "11:00",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 26",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "11:00",
        "end_time": "11:50",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 106",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "11:50",
        "end_time": "12:40",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 101A",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "13:30",
        "end_time": "14:20",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 27-",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "14:20",
        "end_time": "15:10",
        "course": "CSE111",
        "type": "Lecture",
        "room": "Room 27-",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "15:10",
        "end_time": "16:00",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 911",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "16:00",
        "end_time": "16:50",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 911",
        "instructor": "Prof. K3P26WK"
    },
    
    # Tuesday classes
    {
        "day": "Tuesday",
        "start_time": "10:10",
        "end_time": "11:00",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 26",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "11:00",
        "end_time": "11:50",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 106",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "11:50",
        "end_time": "12:40",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 101",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "13:30",
        "end_time": "14:20",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 27-",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "14:20",
        "end_time": "15:10",
        "course": "CSE111",
        "type": "Practical",
        "room": "Room 911",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "15:10",
        "end_time": "16:00",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 36-911",
        "instructor": "Prof. K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "16:00",
        "end_time": "16:50",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 911",
        "instructor": "Prof. K3P26WK"
    },
]

DAY_MAP = {
    "Monday": "MO",
    "Tuesday": "TU",
    "Wednesday": "WE",
    "Thursday": "TH",
    "Friday": "FR",
    "Saturday": "SA",
    "Sunday": "SU",
}

def parse_time(time_str):
    """Parse time string like '10:10' to datetime object"""
    return datetime.strptime(time_str, "%H:%M")

def create_calendar_event_cmd(event):
    """Create Composio execute command for a calendar event"""
    # Use next Monday/Tuesday as a reference date
    today = datetime.now()
    day_name = event["day"]
    
    # Calculate next occurrence of this day
    day_offsets = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    
    today_weekday = today.weekday()  # 0 = Monday
    target_weekday = day_offsets[day_name]
    days_until = (target_weekday - today_weekday) % 7
    if days_until == 0:
        days_until = 7  # Next week if today
    
    start_date = today + timedelta(days=days_until)
    
    start_time = parse_time(event["start_time"])
    end_time = parse_time(event["end_time"])
    
    start_dt = start_date.replace(
        hour=start_time.hour,
        minute=start_time.minute,
        second=0
    )
    end_dt = start_date.replace(
        hour=end_time.hour,
        minute=end_time.minute,
        second=0
    )
    
    title = f"{event['course']} - {event['type']}"
    description = f"Course: {event['course']}\nType: {event['type']}\nRoom: {event['room']}\nInstructor: {event['instructor']}"
    
    cmd = f'composio execute GOOGLE_CALENDAR_CREATE_EVENT -d \'{{"calendar_id": "primary", "summary": "{title}", "description": "{description}", "start_time": "{start_dt.isoformat()}Z", "end_time": "{end_dt.isoformat()}Z", "location": "{event["room"]}"}}\''
    
    return cmd, event

def main():
    print("=" * 70)
    print("MEMORA Timetable Import to Google Calendar")
    print("=" * 70)
    
    # Check if Composio is logged in
    print("\n📋 Checking Composio login status...")
    result = subprocess.run(["composio", "whoami"], capture_output=True, text=True)
    
    if "not logged in" in result.stdout.lower() or "no active session" in result.stdout.lower():
        print("❌ Not logged in to Composio. Please run: composio login")
        print("   Then re-run this script.")
        return 1
    
    print("✅ Composio is logged in")
    
    # Check Google Calendar connection
    print("\n📋 Checking Google Calendar connection...")
    result = subprocess.run(["composio", "execute", "GOOGLE_CALENDAR_GET_MY_CALENDARS"], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("⚠️  Google Calendar not connected. Run: composio link google_calendar")
        print("   Then re-run this script.")
        return 1
    
    print("✅ Google Calendar is connected")
    
    # Create events
    print("\n📅 Creating calendar events...")
    print("-" * 70)
    
    success_count = 0
    failed_events = []
    
    for event in SCHEDULE:
        cmd, evt_data = create_calendar_event_cmd(event)
        
        print(f"\n[{evt_data['day']}] {evt_data['course']} ({evt_data['type']})")
        print(f"  Time: {evt_data['start_time']} - {evt_data['end_time']}")
        print(f"  Room: {evt_data['room']}")
        
        # Execute the command
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Created successfully")
            success_count += 1
        else:
            print(f"  ❌ Failed: {result.stderr[:100]}")
            failed_events.append(evt_data)
    
    # Summary
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"Total events: {len(SCHEDULE)}")
    print(f"Successfully created: {success_count}")
    print(f"Failed: {len(failed_events)}")
    
    if failed_events:
        print("\nFailed events:")
        for evt in failed_events:
            print(f"  - {evt['day']}: {evt['course']} at {evt['start_time']}")
    
    print("\n" + "=" * 70)
    if success_count == len(SCHEDULE):
        print("✅ All events imported successfully!")
        return 0
    else:
        print("⚠️  Some events failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())