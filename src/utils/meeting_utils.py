from datetime import datetime
# from src.core.logger import setup_logger
import base64
import urllib.parse
import re
import logging

logger = logging.getLogger(__name__)

# This function calculates the duration of a meeting given the start and end time in ISO format. It converts the start and end times to datetime objects, computes the difference to get the duration, and then formats the duration as a string in "HH:MM:SS" format. If the input date format is invalid, it returns an error message.
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
        logger.error("Invalid Date Format")
        return "Invalid Date Format"
    
# This function extracts the meeting ID from the join URL by decoding it and using a regular expression to find the pattern that matches the meeting ID format. The meeting ID typically follows a specific format that includes a combination of numbers, letters, and special characters. By extracting this ID, we can later compare it with the meeting ID obtained from the Graph API response to ensure we are working with the correct meeting transcript.
def extract_meeting_id_from_join_url(join_url):
    decoded_url = urllib.parse.unquote(join_url)
    match = re.search(r'\d+:meeting_[\w-]+@[\w.-]+', decoded_url)
    return match.group(0) if match else None

# This function decodes the encoded meeting ID from the Graph API response and extracts the actual meeting ID using a regular expression. The encoded meeting ID is typically a base64 string that contains the meeting information, and we need to decode it to compare it with the meeting ID extracted from the join URL. If the decoded meeting ID matches the one from the join URL, we can confirm that we have found the correct transcript for the meeting.
def extract_meeting_id_from_encoded_id(meeting_id):
    try:
        padded_id = meeting_id + '=' * (-len(meeting_id) % 4)
        decoded = base64.b64decode(padded_id).decode('utf-8', errors='ignore')
        match = re.search(r'\d+:meeting_[\w-]+@[\w.-]+', decoded)
        return match.group(0) if match else None
    except Exception as e:
        logger.error(f"Decode error: {e}")
        return None

# This function compares the meeting ID extracted from the join URL with the meeting ID extracted from the encoded ID. If they match, it indicates that we have found the correct transcript for the meeting. The function also logs the results of the comparison for debugging purposes, which can help identify any issues in the ID extraction or comparison process.
def compare_meeting_ids(join_url, encoded_id):
    id_from_url = extract_meeting_id_from_join_url(join_url)
    id_from_encoded = extract_meeting_id_from_encoded_id(encoded_id)
    if id_from_url == id_from_encoded:
        logger.info("Get Transcript: Match found!")
        logger.info(f"From URL: {id_from_url}")
        logger.info(f"From Encoded: {id_from_encoded}")
    return id_from_url == id_from_encoded