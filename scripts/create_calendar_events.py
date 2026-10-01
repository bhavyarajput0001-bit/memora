#!/usr/bin/env python3
"""
Create timetable events in Google Calendar using Composio
"""
import subprocess
import json
import sys
from datetime import datetime, timedelta

# Timetable data extracted from the image
SCHEDULE = [
    # Monday classes
    {
        "day": "Monday",
        "start_time": "10:10",
        "end_time": "11:00",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 26",
        "instructor": "K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "11:00",
        "end_time": "11:50",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 106",
        "instructor": "K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "11:50",
        "end_time": "12:40",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 101A",
        "instructor": "K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "13:30",
        "end_time": "14:20",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 27-",
        "instructor": "K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "14:20",
        "end_time": "15:10",
        "course": "CSE111",
        "type": "Lecture",
        "room": "Room 27-",
        "instructor": "K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "15:10",
        "end_time": "16:00",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 911",
        "instructor": "K3P26WK"
    },
    {
        "day": "Monday",
        "start_time": "16:00",
        "end_time": "16:50",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 911",
        "instructor": "K3P26WK"
    },
    
    # Tuesday classes
    {
        "day": "Tuesday",
        "start_time": "10:10",
        "end_time": "11:00",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 26",
        "instructor": "K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "11:00",
        "end_time": "11:50",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 106",
        "instructor": "K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "11:50",
        "end_time": "12:40",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 101",
        "instructor": "K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "13:30",
        "end_time": "14:20",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 27-",
        "instructor": "K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "14:20",
        "end_time": "15:10",
        "course": "CSE111",
        "type": "Practical",
        "room": "Room 911",
        "instructor": "K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "15:10",
        "end_time": "16:00",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 36-911",
        "instructor": "K3P26WK"
    },
    {
        "day": "Tuesday",
        "start_time": "16:00",
        "end_time": "16:50",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 911",
        "instructor": "K3P26WK"
    },
]

DAY_TO_WEEKDAY = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

def parse_time(time_str):
    """Parse time string like '10:10' to (hour, minute) tuple"""
    parts = time_str.split(":")
    return int(parts[0]), int(parts[1])

def get_next_weekday(day_name):
    """Get the date for the next occurrence of the given day name"""
    today = datetime.now()
    target_weekday = DAY_TO_WEEKDAY[day_name]
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7  # Next week if today
    return today + timedelta(days=days_ahead)

def create_event_data(event):
    """Create event data for Composio"""
    start_date = get_next_weekday(event["day"])
    start_hour, start_min = parse_time(event["start_time"])
    end_hour, end_min = parse_time(event["end_time"])
    
    start_dt = start_date.replace(hour=start_hour, minute=start_min, second=0)
    end_dt = start_date.replace(hour=end_hour, minute=end_min, second=0)
    
    title = f"{event['course']} - {event['type']}"
    description = f"Course: {event['course']}\nType: {event['type']}\nRoom: {event['room']}\nInstructor: {event['instructor']}"
    
    return {
        "calendar_id": "primary",
        "summary": title,
        "description": description,
        "start_datetime": start_dt.isoformat(),
        "end_datetime": end_dt.isoformat(),
        "location": event["room"]
    }

def main():
    print("=" * 70)
    print("Creating Timetable Events in Google Calendar via Composio")
    print("=" * 70)
    
    success_count = 0
    failed_events = []
    
    for i, event in enumerate(SCHEDULE, 1):
        print(f"\n[{i}/{len(SCHEDULE)}] Creating: {event['course']} ({event['type']})")
        print(f"  Day: {event['day']}")
        print(f"  Time: {event['start_time']} - {event['end_time']}")
        print(f"  Room: {event['room']}")
        
        event_data = create_event_data(event)
        
        # Build command
        cmd = [
            "composio", "execute", "GOOGLECALENDAR_CREATE_EVENT",
            "-d", json.dumps(event_data)
        ]
        
        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ Created successfully")
            success_count += 1
        else:
            print(f"  ❌ Failed: {result.stderr[:200]}")
            failed_events.append(event)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
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
        print("✅ All events imported successfully to Google Calendar!")
        return 0
    else:
        print("⚠️  Some events failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())