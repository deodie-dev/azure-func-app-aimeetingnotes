from src.models.event import EventDetails
from src.utils.meeting_utils import get_duration


def parse_event(event: dict) -> EventDetails:

    online_meeting = event.get("onlineMeeting") or {}
    start = event.get("start") or {}
    end = event.get("end") or {}
    organizer = event.get("organizer", {}).get("emailAddress", {})
    location = event.get("location") or {}

    categories = event.get("categories") or []
    attendees_raw = event.get("attendees") or []

    start_time = start.get("dateTime")
    end_time = end.get("dateTime")

    formatted_start = start_time[:23].replace("T", " ") if start_time else None
    formatted_end = end_time[:23].replace("T", " ") if end_time else None

    attendees = [
        attendee.get("emailAddress", {}).get("address")
        for attendee in attendees_raw
        if attendee.get("emailAddress")
    ]

    return EventDetails(
        event_id=event.get("id"),

        subject=event.get("subject", "No Subject"),
        organizer=organizer.get("name", "Unknown Organizer"),

        start_time=start_time,
        end_time=end_time,

        formatted_start=formatted_start,
        formatted_end=formatted_end,

        join_url=online_meeting.get("joinUrl"),

        is_cancelled=event.get("isCancelled"),
        is_organizer=event.get("isOrganizer"),
        event_type=event.get("type"),

        is_online_meeting=event.get("isOnlineMeeting"),
        online_meeting_provider=event.get("onlineMeetingProvider"),

        response_status=event.get("responseStatus", {}).get("response"),

        duration_str=get_duration(start_time, end_time),

        location=location.get("displayName", "No Location"),

        categories=categories,
        categories_str=", ".join(categories) if categories else "No Categories",

        attendees=attendees,
        attendees_str=", ".join(attendees) if attendees else "No Attendees",
    )