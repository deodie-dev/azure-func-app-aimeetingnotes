from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EventDetails:
    event_id: str
    subject: str
    organizer: str

    start_time: Optional[str]
    end_time: Optional[str]

    formatted_start: Optional[str]
    formatted_end: Optional[str]

    join_url: Optional[str]

    is_cancelled: Optional[bool]
    is_organizer: Optional[bool]
    event_type: Optional[str]

    is_online_meeting: Optional[bool]
    online_meeting_provider: Optional[str]

    response_status: Optional[str]

    duration_str: Optional[str]

    location: str

    categories: List[str]
    categories_str: str

    attendees: List[str]
    attendees_str: str