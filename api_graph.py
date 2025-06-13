import re
import requests
from data_process import compare_meeting_ids, parse_event
from utils import log_and_print, log_and_print_err

import os
GRAPH_APP_URL = os.environ["GRAPH_APP_URL"]
GRAPH_APP_CLIENT_ID = os.environ["GRAPH_APP_CLIENT_ID"]
GRAPH_APP_CLIENT_SECRET = os.environ["GRAPH_APP_CLIENT_SECRET"]

def get_global_graphAPI_token():
    
    url = GRAPH_APP_URL

    payload = {
        "client_id": GRAPH_APP_CLIENT_ID,
        "client_secret": GRAPH_APP_CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        log_and_print_err(f"Error {response.status_code}: {response.text}")
        return None


def get_outlook_metadata(access_token, user, start_date, end_date):

    calendar_events = []
    events = []

    url = f"https://graph.microsoft.com/v1.0/users/{user}/calendarview?$top=1000&$count=true&startDateTime={start_date}&endDateTime={end_date}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Prefer": 'outlook.timezone="Asia/Singapore"',
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        events = data.get("value", [])
        for event in events:
            calendar_events.append(parse_event(event))
    else:
        log_and_print_err(f"Couldn't get Outlook calendar view metadata -  {response.status_code}: {response.text}")

    return calendar_events


def get_transcript_content_url(access_token, user_id, join_url, start_date, end_date):

    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings/getAllTranscripts(meetingOrganizerUserId='{user_id}',startDateTime={start_date},endDateTime={end_date})"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        log_and_print(f"Failed to retrieve transcript: {response.status_code}, {response.text}")
        return None

    data = response.json()
    # print (data)
    for meeting in data.get("value", []):
        meeting_id = meeting.get("meetingId")
        log_and_print(f"Checking meeting ID: {meeting_id}")
        match = compare_meeting_ids(join_url, meeting_id)
        
        if match:
            # log_and_print("Get Transcript: Match found!")
            return meeting.get("transcriptContentUrl")
    
    log_and_print("Unable to find meeting transcript..")
    return None


def get_filtered_vtt(access_token, vtt_url):

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'text/vtt'
    }
    response = requests.get(vtt_url, headers=headers)

    if response.status_code == 200:
        vtt_content = response.text
        vtt_no_timestamps = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', vtt_content)
        lines = [line.strip() for line in vtt_no_timestamps.splitlines() if line.strip().startswith('<v ')]
        log_and_print("VTT retreived and cleaned.")
        return '\n'.join(lines)
    else:
        log_and_print_err(f"Unable to access vtt url: {vtt_url}")
    return None


def get_user_id_by_email(email, access_token, get_value):

    url = f"https://graph.microsoft.com/v1.0/users?$filter=mail eq '{email}'"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        users = data.get("value", [])
        if users:
            return users[0].get(get_value)
        else:
            log_and_print("No user found with that email.")
            return None
    else:
        log_and_print_err(f"Error: {response.status_code} - {response.text}")
        return None
