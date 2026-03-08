import requests
import logging
import re
from src.core.config import Config
from src.parsers.event_parser import parse_event
from src.utils.meeting_utils import compare_meeting_ids

logger = logging.getLogger(__name__)

class GraphClient:

    def __init__(self):
        self.client_id = Config.GRAPH_APP_CLIENT_ID
        self.client_secret = Config.GRAPH_APP_CLIENT_SECRET
        self.token_url = Config.GRAPH_APP_URL
        self.token = self.get_access_token()

    def get_access_token(self):

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': "https://graph.microsoft.com/.default",
            'grant_type': 'client_credentials'
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(self.token_url, data=data, headers=headers)

        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"Failed to obtain access token: {response.status_code}, {response.text}")
            return None

    def get_outlook_metadata(self, user, start_date, end_date):

        calendar_events = []
        events = []

        url = f"https://graph.microsoft.com/v1.0/users/{user}/calendarview?$top=1000&$count=true&startDateTime={start_date}&endDateTime={end_date}"
        headers = {
            "Authorization": f"Bearer {self.token}",
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
            print(f"Couldn't get Outlook calendar view metadata -  {response.status_code}: {response.text}")

        return calendar_events
    

    def get_transcript_content_url(self, user_id, join_url, start_date, end_date):

        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings/getAllTranscripts(meetingOrganizerUserId='{user_id}',startDateTime={start_date},endDateTime={end_date})"

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve transcript: {response.status_code}, {response.text}")
            return None

        data = response.json()
        # print (data)
        for meeting in data.get("value", []):
            meeting_id = meeting.get("meetingId")
            logger.info(f"Checking meeting ID: {meeting_id}")
            match = compare_meeting_ids(join_url, meeting_id)
            
            if match:
                return meeting.get("transcriptContentUrl")
        
        logger.error("Unable to find meeting transcript..")
        return None


    def get_filtered_vtt(self, vtt_url):

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'text/vtt'
        }
        response = requests.get(vtt_url, headers=headers)

        if response.status_code == 200:
            vtt_content = response.text
            vtt_no_timestamps = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', vtt_content)
            lines = [line.strip() for line in vtt_no_timestamps.splitlines() if line.strip().startswith('<v ')]
            logger.info("VTT retreived and cleaned.")
            return '\n'.join(lines)
        else:
            logger.error(f"Unable to access vtt url: {vtt_url}")
        return None


    def get_user_id_by_email(self, email, get_value):

        url = f"https://graph.microsoft.com/v1.0/users?$filter=mail eq '{email}'"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            users = data.get("value", [])
            if users:
                return users[0].get(get_value)
            else:
                logger.info("No user found with that email.")
                return None
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")
            return None
