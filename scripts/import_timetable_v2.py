#!/usr/bin/env python3
"""
MEMORA Timetable Import Script v2
Parses the official PDF timetable and updates Google Calendar
"""
import subprocess
import json
import sys
from datetime import datetime, timedelta

# Updated timetable from PDF rptTimeTableStudent.pdf
SCHEDULE = [
    # Monday
    {
        "day": "Monday",
        "start_time": "09:20",
        "end_time": "10:10",
        "course": "MEC136",
        "type": "Tutorial",
        "room": "Room 27-108",
        "instructor": "Dr. Aman Deep"
    },
    {
        "day": "Monday",
        "start_time": "10:10",
        "end_time": "11:00",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 26-",
        "instructor": "Prof. Gurpreet Kaur"
    },
    {
        "day": "Monday",
        "start_time": "11:00",
        "end_time": "11:50",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 27-101A",
        "instructor": "Prof. Dr. Puneet Thapar"
    },
    {
        "day": "Monday",
        "start_time": "11:50",
        "end_time": "12:40",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 27-101A",
        "instructor": "Prof. Dr. Puneet Thapar"
    },
    {
        "day": "Monday",
        "start_time": "12:40",
        "end_time": "01:30",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 27-108",
        "instructor": "Prof. Gurpreet Kaur"
    },
    {
        "day": "Monday",
        "start_time": "01:30",
        "end_time": "02:20",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 27-101",
        "instructor": "Prof. Gurpreet Kaur"
    },
    {
        "day": "Monday",
        "start_time": "02:20",
        "end_time": "03:10",
        "course": "CSE111",
        "type": "Lecture",
        "room": "Room 27-101",
        "instructor": "Prof. Dr. Ayush Singh"
    },
    {
        "day": "Monday",
        "start_time": "03:10",
        "end_time": "04:00",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 36-911",
        "instructor": "Prof. Gurpreet Kaur"
    },
    {
        "day": "Monday",
        "start_time": "04:00",
        "end_time": "04:50",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 36-911",
        "instructor": "Prof. Gurpreet Kaur"
    },
    
    # Tuesday
    {
        "day": "Tuesday",
        "start_time": "09:20",
        "end_time": "10:10",
        "course": "MEC136",
        "type": "Tutorial",
        "room": "Room 27-108",
        "instructor": "Dr. Aman Deep"
    },
    {
        "day": "Tuesday",
        "start_time": "10:10",
        "end_time": "11:00",
        "course": "MEC136",
        "type": "Tutorial",
        "room": "Room 27-108",
        "instructor": "Dr. Aman Deep"
    },
    {
        "day": "Tuesday",
        "start_time": "11:00",
        "end_time": "11:50",
        "course": "CSE326",
        "type": "Lecture",
        "room": "Room 27-108",
        "instructor": "Prof. Dr. Puneet Thapar"
    },
    {
        "day": "Tuesday",
        "start_time": "11:50",
        "end_time": "12:40",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 27-108",
        "instructor": "Prof. Gurpreet Kaur"
    },
    {
        "day": "Tuesday",
        "start_time": "12:40",
        "end_time": "01:30",
        "course": "MTH165",
        "type": "Lecture",
        "room": "Room 28-508A",
        "instructor": "Prof. Sachin Pal"
    },
    {
        "day": "Tuesday",
        "start_time": "01:30",
        "end_time": "02:20",
        "course": "INT335",
        "type": "Lecture",
        "room": "Room 27-403",
        "instructor": "Dr. R Kalidasan"
    },
    {
        "day": "Tuesday",
        "start_time": "02:20",
        "end_time": "03:10",
        "course": "MTH165",
        "type": "Tutorial",
        "room": "Room 27-403",
        "instructor": "Prof. Sachin Pal"
    },
    
    # Wednesday
    {
        "day": "Wednesday",
        "start_time": "10:10",
        "end_time": "11:00",
        "course": "CSE326",
        "type": "Lecture",
        "room": "Room 27-108",
        "instructor": "Prof. Dr. Puneet Thapar"
    },
    {
        "day": "Wednesday",
        "start_time": "11:50",
        "end_time": "12:40",
        "course": "INT108",
        "type": "Lecture",
        "room": "Room 27-108",
        "instructor": "Prof. Gurpreet Kaur"
    },
    {
        "day": "Wednesday",
        "start_time": "12:40",
        "end_time": "01:30",
        "course": "MTH165",
        "type": "Lecture",
        "room": "Room 28-505",
        "instructor": "Prof. Sachin Pal"
    },
    {
        "day": "Wednesday",
        "start_time": "01:30",
        "end_time": "02:20",
        "course": "CSE111",
        "type": "Lecture",
        "room": "Room 28-505",
        "instructor": "Prof. Dr. Ayush Singh"
    },
    {
        "day": "Wednesday",
        "start_time": "02:20",
        "end_time": "03:10",
        "course": "CSE111",
        "type": "Lecture",
        "room": "Room 27-403",
        "instructor": "Prof. Dr. Ayush Singh"
    },
    
    # Thursday
    {
        "day": "Thursday",
        "start_time": "11:50",
        "end_time": "12:40",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 27-101A",
        "instructor": "Prof. Dr. Puneet Thapar"
    },
    {
        "day": "Thursday",
        "start_time": "12:40",
        "end_time": "01:30",
        "course": "INT335",
        "type": "Lecture",
        "room": "Room 27-505",
        "instructor": "Dr. R Kalidasan"
    },
    {
        "day": "Thursday",
        "start_time": "01:30",
        "end_time": "02:20",
        "course": "MTH165",
        "type": "Lecture",
        "room": "Room 27-504",
        "instructor": "Prof. Sachin Pal"
    },
    {
        "day": "Thursday",
        "start_time": "02:20",
        "end_time": "03:10",
        "course": "MEC136",
        "type": "Lecture",
        "room": "Room 27-504",
        "instructor": "Dr. Aman Deep"
    },
    
    # Friday
    {
        "day": "Friday",
        "start_time": "11:50",
        "end_time": "12:40",
        "course": "CSE326",
        "type": "Practical",
        "room": "Room 27-101A",
        "instructor": "Prof. Dr. Puneet Thapar"
    },
    {
        "day": "Friday",
        "start_time": "12:40",
        "end_time": "01:30",
        "course": "INT335",
        "type": "Lecture",
        "room": "Room 27-505",
        "instructor": "Dr. R Kalidasan"
    },
    {
        "day": "Friday",
        "start_time": "01:30",
        "end_time": "02:20",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 27-108",
        "instructor": "Prof. Gurpreet Kaur"
    },
    {
        "day": "Friday",
        "start_time": "02:20",
        "end_time": "03:10",
        "course": "INT108",
        "type": "Practical",
        "room": "Room 36-911",
        "instructor": "Prof. Gurpreet Kaur"
    },
]

DAY_MAP = {
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
    target_weekday = DAY_MAP[day_name]
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7  # Next week if today
    return today + timedelta(days=days_ahead)

def create_event_data(event):
    """Create event data for Composio"""
    start_date = get_next_weekday(event["day"])
    start_hour, start_min = parse_time(event["start_time"])
    
    # Handle end time that might be next day (rare)
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
    print("MEMORA Timetable Import v2 - FROM PDF")
    print("=" * 70)
    
    # First, clear old events
    print("\n🗑️  Clearing old timetable events...")
    clear_cmd = 'composio execute GOOGLECALENDAR_CLEAR_CALENDAR -d \'{"calendar_id": "primary"}\' 2>&1'
    # Note: This clears ALL events, so we need to be careful
    # Instead, let's find and delete events with course codes
    
    success_count = 0
    failed_events = []
    
    print(f"\n📅 Creating {len(SCHEDULE)} new calendar events...")
    print("-" * 70)
    
    for i, event in enumerate(SCHEDULE, 1):
        print(f"\n[{i}/{len(SCHEDULE)}] {event['course']} ({event['type']})")
        print(f"  Day: {event['day']}")
        print(f"  Time: {event['start_time']} - {event['end_time']}")
        print(f"  Room: {event['room']}")
        print(f"  Instructor: {event['instructor']}")
        
        event_data = create_event_data(event)
        
        # Build command
        cmd = [
            "composio", "execute", "GOOGLECALENDAR_CREATE_EVENT",
            "-d", json.dumps(event_data)
        ]
        
        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ Created")
            success_count += 1
        else:
            print(f"  ❌ Failed: {result.stderr[:100]}")
            failed_events.append(event)
    
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
        print("\nView your calendar: https://calendar.google.com/calendar")
        return 0
    else:
        print("⚠️  Some events failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())