import os
from src.core.folder_IDs import BA_FOLDER_LIST

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

    #Azure SQL Database credentials
    SQL_DATABASE = os.getenv("SQL_DATABASE")
    SQL_DRIVER = os.getenv("SQL_DRIVER")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_USERNAME = os.getenv("SQL_USERNAME")

    #Clickup folder IDs
    DIAGNOSTIC_ID = os.getenv("DIAGNOSTIC_ID")
    RETAINER_ID = os.getenv("RETAINER_ID")
    CALENDAR_EVENTS_LIST_ID = os.getenv("CALENDAR_EVENTS_LIST_ID")
    OTHERS_LIST_ID = os.getenv("OTHERS_LIST_ID")
    BA_LIST = BA_FOLDER_LIST


