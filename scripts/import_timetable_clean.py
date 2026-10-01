#!/usr/bin/env python3
"""
MEMORA Timetable Import Script - Clean & Color Coded
Organizes classes with distinct colors per subject
"""
import subprocess
import json
import sys
from datetime import datetime, timedelta

# Color palette for subjects
SUBJECT_COLORS = {
    "INT108": "6",      # Green
    "CSE326": "9",      # Red  
    "CSE111": "1",      # Blue
    "MTH165": "3",      # Yellow
    "INT335": "10",     # Pink
    "MEC136": "4",      # Orange
}

# Complete timetable from PDF
SCHEDULE = [
    # Monday - September 21, 2026
    {"day": "Monday", "date": "2026-09-21", "start_time": "09:20", "end_time": "10:10", "course": "MEC136", "type": "Tutorial", "room": "27-108", "color": SUBJECT_COLORS["MEC136"]},
    {"day": "Monday", "date": "2026-09-21", "start_time": "10:10", "end_time": "11:00", "course": "INT108", "type": "Lecture", "room": "26-", "color": SUBJECT_COLORS["INT108"]},
    {"day": "Monday", "date": "2026-09-21", "start_time": "11:00", "end_time": "11:50", "course": "CSE326", "type": "Practical", "room": "27-101A", "color": SUBJECT_COLORS["CSE326"]},
    {"day": "Monday", "date": "2026-09-21", "start_time": "11:50", "end_time": "12:40", "course": "CSE326", "type": "Practical", "room": "27-101A", "color": SUBJECT_COLORS["CSE326"]},
    {"day": "Monday", "date": "2026-09-21", "start_time": "12:40", "end_time": "13:30", "course": "INT108", "type": "Practical", "room": "27-108", "color": SUBJECT_COLORS["INT108"]},
    {"day": "Monday", "date": "2026-09-21", "start_time": "13:30", "end_time": "14:20", "course": "INT108", "type": "Lecture", "room": "27-101", "color": SUBJECT_COLORS["INT108"]},
    {"day": "Monday", "date": "2026-09-21", "start_time": "14:20", "end_time": "15:10", "course": "CSE111", "type": "Lecture", "room": "27-101", "color": SUBJECT_COLORS["CSE111"]},
    {"day": "Monday", "date": "2026-09-21", "start_time": "15:10", "end_time": "16:00", "course": "INT108", "type": "Practical", "room": "36-911", "color": SUBJECT_COLORS["INT108"]},
    {"day": "Monday", "date": "2026-09-21", "start_time": "16:00", "end_time": "16:50", "course": "INT108", "type": "Practical", "room": "36-911", "color": SUBJECT_COLORS["INT108"]},
    
    # Tuesday - September 22, 2026
    {"day": "Tuesday", "date": "2026-09-22", "start_time": "09:20", "end_time": "10:10", "course": "MEC136", "type": "Tutorial", "room": "27-108", "color": SUBJECT_COLORS["MEC136"]},
    {"day": "Tuesday", "date": "2026-09-22", "start_time": "10:10", "end_time": "11:00", "course": "MEC136", "type": "Tutorial", "room": "27-108", "color": SUBJECT_COLORS["MEC136"]},
    {"day": "Tuesday", "date": "2026-09-22", "start_time": "11:00", "end_time": "11:50", "course": "CSE326", "type": "Lecture", "room": "27-108", "color": SUBJECT_COLORS["CSE326"]},
    {"day": "Tuesday", "date": "2026-09-22", "start_time": "11:50", "end_time": "12:40", "course": "INT108", "type": "Practical", "room": "27-108", "color": SUBJECT_COLORS["INT108"]},
    {"day": "Tuesday", "date": "2026-09-22", "start_time": "12:40", "end_time": "13:30", "course": "MTH165", "type": "Lecture", "room": "28-508A", "color": SUBJECT_COLORS["MTH165"]},
    {"day": "Tuesday", "date": "2026-09-22", "start_time": "13:30", "end_time": "14:20", "course": "INT335", "type": "Lecture", "room": "27-403", "color": SUBJECT_COLORS["INT335"]},
    {"day": "Tuesday", "date": "2026-09-22", "start_time": "14:20", "end_time": "15:10", "course": "MTH165", "type": "Tutorial", "room": "27-403", "color": SUBJECT_COLORS["MTH165"]},
    
    # Wednesday - September 23, 2026
    {"day": "Wednesday", "date": "2026-09-23", "start_time": "10:10", "end_time": "11:00", "course": "CSE326", "type": "Lecture", "room": "27-108", "color": SUBJECT_COLORS["CSE326"]},
    {"day": "Wednesday", "date": "2026-09-23", "start_time": "11:50", "end_time": "12:40", "course": "INT108", "type": "Lecture", "room": "27-108", "color": SUBJECT_COLORS["INT108"]},
    {"day": "Wednesday", "date": "2026-09-23", "start_time": "12:40", "end_time": "13:30", "course": "MTH165", "type": "Lecture", "room": "28-505", "color": SUBJECT_COLORS["MTH165"]},
    {"day": "Wednesday", "date": "2026-09-23", "start_time": "13:30", "end_time": "14:20", "course": "CSE111", "type": "Lecture", "room": "28-505", "color": SUBJECT_COLORS["CSE111"]},
    {"day": "Wednesday", "date": "2026-09-23", "start_time": "14:20", "end_time": "15:10", "course": "CSE111", "type": "Lecture", "room": "27-403", "color": SUBJECT_COLORS["CSE111"]},
    
    # Thursday - September 24, 2026
    {"day": "Thursday", "date": "2026-09-24", "start_time": "11:50", "end_time": "12:40", "course": "CSE326", "type": "Practical", "room": "27-101A", "color": SUBJECT_COLORS["CSE326"]},
    {"day": "Thursday", "date": "2026-09-24", "start_time": "12:40", "end_time": "13:30", "course": "INT335", "type": "Lecture", "room": "27-505", "color": SUBJECT_COLORS["INT335"]},
    {"day": "Thursday", "date": "2026-09-24", "start_time": "13:30", "end_time": "14:20", "course": "MTH165", "type": "Lecture", "room": "27-504", "color": SUBJECT_COLORS["MTH165"]},
    {"day": "Thursday", "date": "2026-09-24", "start_time": "14:20", "end_time": "15:10", "course": "MEC136", "type": "Lecture", "room": "27-504", "color": SUBJECT_COLORS["MEC136"]},
    
    # Friday - September 25, 2026
    {"day": "Friday", "date": "2026-09-25", "start_time": "11:50", "end_time": "12:40", "course": "CSE326", "type": "Practical", "room": "27-101A", "color": SUBJECT_COLORS["CSE326"]},
    {"day": "Friday", "date": "2026-09-25", "start_time": "12:40", "end_time": "13:30", "course": "INT335", "type": "Lecture", "room": "27-505", "color": SUBJECT_COLORS["INT335"]},
    {"day": "Friday", "date": "2026-09-25", "start_time": "13:30", "end_time": "14:20", "course": "INT108", "type": "Practical", "room": "27-108", "color": SUBJECT_COLORS["INT108"]},
    {"day": "Friday", "date": "2026-09-25", "start_time": "14:20", "end_time": "15:10", "course": "INT108", "type": "Practical", "room": "36-911", "color": SUBJECT_COLORS["INT108"]},
]

def parse_time(time_str):
    """Parse time string like '10:10' to (hour, minute) tuple"""
    parts = time_str.split(":")
    return int(parts[0]), int(parts[1])

def create_event_data(event):
    """Create event data for Composio with color"""
    # Parse date and time
    date = datetime.strptime(event["date"], "%Y-%m-%d")
    start_hour, start_min = parse_time(event["start_time"])
    end_hour, end_min = parse_time(event["end_time"])
    
    start_dt = date.replace(hour=start_hour, minute=start_min, second=0)
    end_dt = date.replace(hour=end_hour, minute=end_min, second=0)
    
    title = f"[{event['course']}] {event['type']}"
    description = f"Course: {event['course']}\nType: {event['type']}\nRoom: {event['room']}"
    
    return {
        "calendar_id": "primary",
        "summary": title,
        "description": description,
        "start_datetime": start_dt.isoformat(),
        "end_datetime": end_dt.isoformat(),
        "location": f"Room {event['room']}",
        "color_id": event["color"]
    }

def main():
    print("=" * 70)
    print("🎨 MEMORA Timetable Import - Clean & Color Coded")
    print("=" * 70)
    print("\n📚 Subject Color Coding:")
    print("   🟢 INT108 (Python Programming) - Green")
    print("   🔴 CSE326 (Internet Programming) - Red")
    print("   🔵 CSE111 (Orientation) - Blue")
    print("   🟡 MTH165 (Mathematics) - Yellow")
    print("   🩷 INT335 (Design Thinking) - Pink")
    print("   🟠 MEC136 (Engineering Drawing) - Orange")
    print("=" * 70)
    
    success_count = 0
    failed_events = []
    
    # Group by day for better display
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    for day in days_order:
        day_events = [e for e in SCHEDULE if e["day"] == day]
        if not day_events:
            continue
            
        print(f"\n📅 {day.upper()} ({day_events[0]['date']}) - {len(day_events)} classes")
        print("-" * 70)
        
        for event in day_events:
            print(f"\n  ⏰ {event['start_time']} - {event['end_time']}")
            print(f"     Course: {event['course']} ({event['type']})")
            print(f"     Room: {event['room']}")
            print(f"     Color: {event['color']}")
            
            event_data = create_event_data(event)
            
            cmd = [
                "composio", "execute", "GOOGLECALENDAR_CREATE_EVENT",
                "-d", json.dumps(event_data)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"     ✅ Created")
                success_count += 1
            else:
                print(f"     ❌ Failed: {result.stderr[:100]}")
                failed_events.append(event)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 IMPORT SUMMARY")
    print("=" * 70)
    print(f"Total events: {len(SCHEDULE)}")
    print(f"✅ Successfully created: {success_count}")
    print(f"❌ Failed: {len(failed_events)}")
    
    if failed_events:
        print("\nFailed events:")
        for evt in failed_events:
            print(f"  - {evt['day']}: {evt['course']} at {evt['start_time']}")
    
    print("\n" + "=" * 70)
    if success_count == len(SCHEDULE):
        print("✅ ALL EVENTS IMPORTED SUCCESSFULLY!")
        print("\n📍 View your color-coded calendar:")
        print("   https://calendar.google.com/calendar")
        return 0
    else:
        print("⚠️  Some events failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())