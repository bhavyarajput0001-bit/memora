#!/usr/bin/env python3
"""
MEMORA Timetable Import Script - FINAL VERSION
Clean, color-coded, proper timezone handling
"""
import subprocess
import json
import sys
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

# Color mapping for subjects
COLORS = {
    'INT108': '6',      # Green
    'CSE326': '9',      # Red  
    'CSE111': '1',      # Blue
    'MTH165': '3',      # Yellow
    'INT335': '10',     # Pink
    'MEC136': '4',      # Orange
}

# Complete timetable from PDF
SCHEDULE = [
    # Monday - September 21, 2026
    {"day": "Monday", "date": "2026-09-21", "start": "09:20", "end": "10:10", "course": "MEC136", "type": "Tutorial", "room": "27-108"},
    {"day": "Monday", "date": "2026-09-21", "start": "10:10", "end": "11:00", "course": "INT108", "type": "Lecture", "room": "26-"},
    {"day": "Monday", "date": "2026-09-21", "start": "11:00", "end": "11:50", "course": "CSE326", "type": "Practical", "room": "27-101A"},
    {"day": "Monday", "date": "2026-09-21", "start": "11:50", "end": "12:40", "course": "CSE326", "type": "Practical", "room": "27-101A"},
    {"day": "Monday", "date": "2026-09-21", "start": "12:40", "end": "13:30", "course": "INT108", "type": "Practical", "room": "27-108"},
    {"day": "Monday", "date": "2026-09-21", "start": "13:30", "end": "14:20", "course": "INT108", "type": "Lecture", "room": "27-101"},
    {"day": "Monday", "date": "2026-09-21", "start": "14:20", "end": "15:10", "course": "CSE111", "type": "Lecture", "room": "27-101"},
    {"day": "Monday", "date": "2026-09-21", "start": "15:10", "end": "16:00", "course": "INT108", "type": "Practical", "room": "36-911"},
    {"day": "Monday", "date": "2026-09-21", "start": "16:00", "end": "16:50", "course": "INT108", "type": "Practical", "room": "36-911"},
    
    # Tuesday - September 22, 2026
    {"day": "Tuesday", "date": "2026-09-22", "start": "09:20", "end": "10:10", "course": "MEC136", "type": "Tutorial", "room": "27-108"},
    {"day": "Tuesday", "date": "2026-09-22", "start": "10:10", "end": "11:00", "course": "MEC136", "type": "Tutorial", "room": "27-108"},
    {"day": "Tuesday", "date": "2026-09-22", "start": "11:00", "end": "11:50", "course": "CSE326", "type": "Lecture", "room": "27-108"},
    {"day": "Tuesday", "date": "2026-09-22", "start": "11:50", "end": "12:40", "course": "INT108", "type": "Practical", "room": "27-108"},
    {"day": "Tuesday", "date": "2026-09-22", "start": "12:40", "end": "13:30", "course": "MTH165", "type": "Lecture", "room": "28-508A"},
    {"day": "Tuesday", "date": "2026-09-22", "start": "13:30", "end": "14:20", "course": "INT335", "type": "Lecture", "room": "27-403"},
    {"day": "Tuesday", "date": "2026-09-22", "start": "14:20", "end": "15:10", "course": "MTH165", "type": "Tutorial", "room": "27-403"},
    
    # Wednesday - September 23, 2026
    {"day": "Wednesday", "date": "2026-09-23", "start": "10:10", "end": "11:00", "course": "CSE326", "type": "Lecture", "room": "27-108"},
    {"day": "Wednesday", "date": "2026-09-23", "start": "11:50", "end": "12:40", "course": "INT108", "type": "Lecture", "room": "27-108"},
    {"day": "Wednesday", "date": "2026-09-23", "start": "12:40", "end": "13:30", "course": "MTH165", "type": "Lecture", "room": "28-505"},
    {"day": "Wednesday", "date": "2026-09-23", "start": "13:30", "end": "14:20", "course": "CSE111", "type": "Lecture", "room": "28-505"},
    {"day": "Wednesday", "date": "2026-09-23", "start": "14:20", "end": "15:10", "course": "CSE111", "type": "Lecture", "room": "27-403"},
    
    # Thursday - September 24, 2026
    {"day": "Thursday", "date": "2026-09-24", "start": "11:50", "end": "12:40", "course": "CSE326", "type": "Practical", "room": "27-101A"},
    {"day": "Thursday", "date": "2026-09-24", "start": "12:40", "end": "13:30", "course": "INT335", "type": "Lecture", "room": "27-505"},
    {"day": "Thursday", "date": "2026-09-24", "start": "13:30", "end": "14:20", "course": "MTH165", "type": "Lecture", "room": "27-504"},
    {"day": "Thursday", "date": "2026-09-24", "start": "14:20", "end": "15:10", "course": "MEC136", "type": "Lecture", "room": "27-504"},
    
    # Friday - September 25, 2026
    {"day": "Friday", "date": "2026-09-25", "start": "11:50", "end": "12:40", "course": "CSE326", "type": "Practical", "room": "27-101A"},
    {"day": "Friday", "date": "2026-09-25", "start": "12:40", "end": "13:30", "course": "INT335", "type": "Lecture", "room": "27-505"},
    {"day": "Friday", "date": "2026-09-25", "start": "13:30", "end": "14:20", "course": "INT108", "type": "Practical", "room": "27-108"},
    {"day": "Friday", "date": "2026-09-25", "start": "14:20", "end": "15:10", "course": "INT108", "type": "Practical", "room": "36-911"},
]

def create_event_data(event):
    """Create event data with proper IST timezone"""
    start_hour, start_min = map(int, event['start'].split(':'))
    end_hour, end_min = map(int, event['end'].split(':'))
    
    date_obj = datetime.strptime(event['date'], '%Y-%m-%d')
    start_dt = IST.localize(date_obj.replace(hour=start_hour, minute=start_min))
    end_dt = IST.localize(date_obj.replace(hour=end_hour, minute=end_min))
    
    return {
        'calendar_id': 'primary',
        'summary': f"[{event['course']}] {event['type']}",
        'description': f"Course: {event['course']}\nType: {event['type']}\nRoom: {event['room']}",
        'start_datetime': start_dt.isoformat(),
        'end_datetime': end_dt.isoformat(),
        'location': f"Room {event['room']}",
        'color_id': COLORS.get(event['course'], '1')
    }

def main():
    print("=" * 70)
    print("MEMORA Timetable Import - FINAL CLEAN VERSION")
    print("=" * 70)
    print("\nSubject Color Coding:")
    print("  [6] INT108 (Python Programming) - Green")
    print("  [9] CSE326 (Internet Programming) - Red")
    print("  [1] CSE111 (Orientation) - Blue")
    print("  [3] MTH165 (Mathematics) - Yellow")
    print("  [10] INT335 (Design Thinking) - Pink")
    print("  [4] MEC136 (Engineering Drawing) - Orange")
    print("=" * 70)
    
    success_count = 0
    failed_events = []
    
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    for day in days_order:
        day_events = [e for e in SCHEDULE if e['day'] == day]
        if not day_events:
            continue
            
        print(f"\n{day.upper()} ({day_events[0]['date']}) - {len(day_events)} classes")
        print("-" * 70)
        
        for event in day_events:
            print(f"\n  Time: {event['start']} - {event['end']}")
            print(f"  Course: {event['course']} ({event['type']})")
            print(f"  Room: {event['room']}")
            print(f"  Color: [{COLORS.get(event['course'], '1')}]")
            
            event_data = create_event_data(event)
            
            cmd = [
                'composio', 'execute', 'GOOGLECALENDAR_CREATE_EVENT',
                '-d', json.dumps(event_data)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and 'successful' in result.stdout:
                print(f"  Status: CREATED")
                success_count += 1
            else:
                print(f"  Status: FAILED")
                failed_events.append(event)
    
    # Summary
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"Total events: {len(SCHEDULE)}")
    print(f"Successfully created: {success_count}")
    print(f"Failed: {len(failed_events)}")
    
    print("\n" + "=" * 70)
    if success_count == len(SCHEDULE):
        print("ALL EVENTS IMPORTED SUCCESSFULLY!")
        print("\nView your calendar: https://calendar.google.com/calendar")
        return 0
    else:
        print("Some events failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())