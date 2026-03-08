import os
from src.core.clickup_ids import *

class Config:

    # ClickUp API credentials
    CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN")
    CLICKUP_USERS_LIST_ID = os.getenv("CLICKUP_USERS_LIST_ID")

    # Microsoft Graph API credentials
    GRAPH_APP_CLIENT_ID = os.getenv("GRAPH_APP_CLIENT_ID")
    GRAPH_APP_CLIENT_SECRET = os.getenv("GRAPH_APP_CLIENT_SECRET")
    GRAPH_APP_URL = os.getenv("GRAPH_APP_URL")

    # OpenAI API credentials
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_URL = os.getenv("OPENAI_URL")

    # Azure SQL Database credentials
    SQL_DATABASE = os.getenv("SQL_DATABASE")
    SQL_DRIVER = os.getenv("SQL_DRIVER")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_USERNAME = os.getenv("SQL_USERNAME")

    # ClickUp folder and list IDs
    DIAGNOSTIC_ID = os.getenv("DIAGNOSTIC_ID")
    RETAINER_ID = os.getenv("RETAINER_ID")
    CALENDAR_EVENTS_LIST_ID = os.getenv("CALENDAR_EVENTS_LIST_ID")
    OTHERS_LIST_ID = os.getenv("OTHERS_LIST_ID")
    BA_LIST = BA_FOLDER_LIST

    # ClickUp custom field IDs
    CUSTOM_FIELD_ID_BusinessAdviser = CUSTOM_FIELD_ID_BusinessAdviser
    CUSTOM_FIELD_ID_Organizer = CUSTOM_FIELD_ID_Organizer
    CUSTOM_FIELD_ID_MeetingCancelled = CUSTOM_FIELD_ID_MeetingCancelled
    CUSTOM_FIELD_ID_StartTime = CUSTOM_FIELD_ID_StartTime
    CUSTOM_FIELD_ID_Duration = CUSTOM_FIELD_ID_Duration
    CUSTOM_FIELD_ID_Categories = CUSTOM_FIELD_ID_Categories
    CUSTOM_FIELD_ID_Attendees = CUSTOM_FIELD_ID_Attendees
    CUSTOM_FIELD_ID_TranscriptFound = CUSTOM_FIELD_ID_TranscriptFound
    CUSTOM_FIELD_ID_AIAPIDone = CUSTOM_FIELD_ID_AIAPIDone
    CUSTOM_FIELD_ID_SummarizedTranscript = CUSTOM_FIELD_ID_SummarizedTranscript
    CUSTOM_FIELD_ID_ClickUpAPIDone = CUSTOM_FIELD_ID_ClickUpAPIDone

