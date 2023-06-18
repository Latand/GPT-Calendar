import json
from datetime import datetime, timedelta

from gcsa._services.events_service import EventsService
from gcsa.event import Event

from infrastructure.function_services.functions.argument_models import (
    ArgsAddTask,
    ArgsGetTasks,
    ArgsRearrangeTask,
    ArgsDeleteTask,
)
from infrastructure.openai_api.types import FunctionCall

CALENDAR_ASSISTANT_PROMPT = """
You are a Calendar Assistant.
You are designed to accept a user's input and use API calls to perform management of the user's calendar.

- The user can ask the assistant to manage tasks in the calendar.
- Sometimes the assistant might need to call the API multiple times to get the information it needs.
- The assistant is very smart and can understand if the user's request is flawed (can't be done, contradictory, etc.) and will respond accordingly.
- The assistant can determine the time period for which the user wants to change the calendar.
---
IMPORTANT INSTRUCTIONS FOR FLOW:
- If user hasn't specified the time/duration/priority, the assistant will DETERMINE the time by itself FROM THE CONTEXT.
- If you don't have tasks ids in the context, you can ACCESS the task ids by using the "get_week_tasks" "get_tasks" actions ONLY. In that case, there will be only one task in the context.
- You have to make sure the tasks DON'T OVERLAP in time unless the user specifies that they want to overlap. If they do, the assistant will ask the user for confirmation.
- To get tasks for a specific date - the end date should be the next day.
---
BACKGROUND INFO:

Today: {today_time}
---
"""

USER_TIMEZONE = "Europe/Kiev"


def get_color_by_priority(priority):
    if priority == "high":
        return 11
    elif priority == "medium":
        return 5
    elif priority == "low":
        return 1


def add_event(
        calendar: EventsService, args: ArgsAddTask, timezone: str = USER_TIMEZONE
):
    """
    Add a task to the calendar
    """

    event = Event(
        summary=args.summary,
        start=args.start,
        end=args.end,
        description=args.description,
        timezone=timezone,
        color_id=get_color_by_priority(args.priority),
        minutes_before_popup_reminder=30,
    )
    calendar.add_event(event)


def tasks_to_string(tasks):
    return "\n".join(
        [
            f"""ID:{task.id}|Name:{task.summary}|Datetime:{task.start.strftime("%Y-%m-%d %H:%M:%S")}|Duration:{(task.end - task.start).seconds // 60}m|Priority:{task.color_id}"""
            for task in tasks
        ]
    )


def get_events(calendar: EventsService, args: ArgsGetTasks):
    """
    Get the user's schedule for a specific time period
    """
    tasks = calendar.get_events(args.start, args.end)
    return tasks_to_string(tasks)


def get_week_events(calendar: EventsService, timezone: str = USER_TIMEZONE):
    """
    Get the user's schedule for the current  week
    """
    # Get Monday of current week
    start_date = datetime.today() - timedelta(days=datetime.today().weekday())
    # Get Sunday of current week
    end_date = start_date + timedelta(days=6)

    tasks = calendar.get_events(start_date, end_date, timezone=timezone)
    return tasks_to_string(tasks)


def rearrange_event(calendar: EventsService, args: ArgsRearrangeTask):
    """
    Rearrange a task in the calendar
    """
    event = calendar.get_event(args.task_id)
    event.start = args.start
    event.end = args.end
    calendar.update_event(event)


def delete_event(calendar: EventsService, args: ArgsDeleteTask):
    """
    Delete a task from the calendar
    """
    calendar.delete_event(args.task_id)


def call_function(
        calendar_service: EventsService, function_call: FunctionCall
):
    """
    Call the function based on the action
    """
    name = function_call.name
    args = json.loads(function_call.arguments) or {}

    if name == "add_task":
        add_event(calendar_service, ArgsAddTask(**args))
        return "Task added successfully"
    elif name == "get_tasks":
        return (
                get_events(calendar_service, ArgsGetTasks(**args))
                or "No tasks for this period"
        )
    elif name == "get_week_tasks":
        return get_week_events(calendar_service) or "No tasks for this week"
    elif name == "rearrange_task":
        rearrange_event(calendar_service, ArgsRearrangeTask(**args))
        return "Task rearranged successfully"
    elif name == "delete_task":
        delete_event(calendar_service, ArgsDeleteTask(**args))
        return "Task deleted successfully"
    else:
        raise Exception(f"Unknown action: {name}")
