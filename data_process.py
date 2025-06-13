from datetime import datetime
from utils import log_and_print
import base64
import urllib.parse
import re


def get_duration(start_time_str, end_time_str):    
    try:
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        
        duration = end_time - start_time
        total_minutes = int(duration.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        return f"{hours:02}:{minutes:02}:00"
    
    except ValueError:
        return "Invalid Date Format"
    

def extract_meeting_id_from_join_url(join_url):
    decoded_url = urllib.parse.unquote(join_url)
    match = re.search(r'\d+:meeting_[\w-]+@[\w.-]+', decoded_url)
    return match.group(0) if match else None


def extract_meeting_id_from_encoded_id(meeting_id):
    try:
        padded_id = meeting_id + '=' * (-len(meeting_id) % 4)
        decoded = base64.b64decode(padded_id).decode('utf-8', errors='ignore')
        match = re.search(r'\d+:meeting_[\w-]+@[\w.-]+', decoded)
        return match.group(0) if match else None
    except Exception as e:
        log_and_print(f"Decode error: {e}")
        return None


def compare_meeting_ids(join_url, encoded_id):
    id_from_url = extract_meeting_id_from_join_url(join_url)
    id_from_encoded = extract_meeting_id_from_encoded_id(encoded_id)
    if id_from_url == id_from_encoded:
        log_and_print("Get Transcript: Match found!")
        log_and_print(f"From URL: {id_from_url}")
        log_and_print(f"From Encoded: {id_from_encoded}")
    return id_from_url == id_from_encoded


def parse_event(event):
    event_details = {
        "event_id": event.get("id"),
        "online_meeting": event.get("onlineMeeting"),
        "joinURL": event.get("onlineMeeting").get("joinUrl", "None") if event.get("onlineMeeting") else "None",
        "is_cancelled": event.get("isCancelled"),
        "is_organizer": event.get("isOrganizer"),
        "event_type": event.get("type"),
        "is_online_meeting": event.get("isOnlineMeeting"),
        "online_meeting_provider": event.get("onlineMeetingProvider"),
        "response_status": event.get("responseStatus", {}).get("response"),
        "subject": event.get("subject", "No Subject"),
        "organizer": event.get("organizer", {}).get("emailAddress", {}).get("name", "Unknown Organizer"),

        "start_time": event.get("start", {}).get("dateTime", "No Start Time"),
        "trimmed_st": event.get("start", {}).get("dateTime", "No Start Time")[:23],
        "formatted_st": event.get("start", {}).get("dateTime", "No Start Time")[:23].replace("T", " "),
        
        "end_time": event.get("end", {}).get("dateTime", "No End Time"),
        "trimmed_et": event.get("end", {}).get("dateTime", "No End Time")[:23],
        "formatted_et": event.get("end", {}).get("dateTime", "No End Time")[:23].replace("T", " "),

        "duration_str": get_duration(event.get("start", {}).get("dateTime", "No Start Time"), event.get("end", {}).get("dateTime", "No End Time")),
        "location": event.get("location", {}).get("displayName", "No Location"),
        "categories": event.get("categories", []),
        "attendees": event.get("attendees", []),
        "categories_str": ', '.join(event.get("categories", [])) if event.get("categories", []) else 'No Categories',
        "attendees_str": ', '.join([attendee["emailAddress"]["address"] for attendee in event.get("attendees", [])]) if event.get("attendees", []) else 'No Attendees'
    }
    return event_details
