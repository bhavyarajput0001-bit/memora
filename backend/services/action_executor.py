"""Agentic action executor for MEMORA."""
import logging
import subprocess
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ActionContext:
    """Context for action execution."""
    action_type: str
    target: str
    parameters: dict = field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high


class ActionExecutor:
    """Execute proposed actions."""

    @staticmethod
    def execute_calendar_event(context: ActionContext) -> dict:
        """Create a calendar event using macOS Calendar."""
        try:
            title = context.target
            description = context.parameters.get("description", "")
            start_date = context.parameters.get("start_date", "")
            end_date = context.parameters.get("end_date", "")
            location = context.parameters.get("location", "")
            attendees = context.parameters.get("attendees", [])

            script = f'''
tell application "Calendar"
    tell calendar "{context.parameters.get('calendar', 'Personal')}"
        set theEvent to make new event with properties {{summary:"{title}", description:"{description}", start date:date "{start_date}", end date:date "{end_date}", location:"{location}"}}
        repeat with aName in {attendees}
            make new attachment at theEvent with properties {{name:aName}}
        end repeat
        return "Event created: " & summary of theEvent
    end tell
end tell
'''
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return {"success": True, "message": result.stdout.strip()}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def execute_reminder(context: ActionContext) -> dict:
        """Create a reminder using macOS Reminders."""
        try:
            title = context.target
            due_date = context.parameters.get("due_date", "")
            notes = context.parameters.get("notes", "")

            script = f'''
tell application "Reminders"
    tell list "{context.parameters.get('list', 'Reminders')}"
        make new reminder with properties {{name:"{title}", notes:"{notes}"}}
    end tell
end tell
'''
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return {"success": True, "message": "Reminder created"}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def execute_email_draft(context: ActionContext) -> dict:
        """Draft an email in macOS Mail."""
        try:
            recipient = context.parameters.get("recipient", "")
            subject = context.target
            body = context.parameters.get("body", "")

            script = f'''
tell application "Mail"
    set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:true}}
    tell newMessage
        make new to recipient at end of to recipients with properties {{name:"{recipient}", address:"{recipient}"}}
    end tell
end tell
'''
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return {"success": True, "message": "Email draft created"}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def execute_note(context: ActionContext) -> dict:
        """Create a note in Apple Notes."""
        try:
            title = context.target
            content = context.parameters.get("content", "")
            notebook = context.parameters.get("notebook", "Notes")

            script = f'''
tell application "Notes"
    tell account "iCloud"
        make new note at folder "{notebook}" with properties {{name:"{title}", body:"{content}"}}
    end tell
end tell
'''
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return {"success": True, "message": "Note created"}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def execute(context: ActionContext) -> dict:
        """Execute an action based on its type."""
        executors = {
            "calendar_event": ActionExecutor.execute_calendar_event,
            "reminder": ActionExecutor.execute_reminder,
            "email_draft": ActionExecutor.execute_email_draft,
            "note": ActionExecutor.execute_note,
        }

        executor = executors.get(context.action_type)
        if not executor:
            return {"success": False, "error": f"Unknown action type: {context.action_type}"}

        return executor(context)

    @staticmethod
    def get_available_actions() -> list[dict]:
        """Get list of available action types."""
        return [
            {
                "type": "calendar_event",
                "name": "Create Calendar Event",
                "description": "Create a new event in macOS Calendar",
                "parameters": ["title", "start_date", "end_date", "location", "attendees"],
            },
            {
                "type": "reminder",
                "name": "Create Reminder",
                "description": "Create a reminder in macOS Reminders",
                "parameters": ["title", "due_date", "notes"],
            },
            {
                "type": "email_draft",
                "name": "Draft Email",
                "description": "Create a draft email in macOS Mail",
                "parameters": ["recipient", "subject", "body"],
            },
            {
                "type": "note",
                "name": "Create Note",
                "description": "Create a note in Apple Notes",
                "parameters": ["title", "content", "notebook"],
            },
        ]
