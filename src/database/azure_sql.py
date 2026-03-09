import pyodbc
import logging
from src.core.config import Config

logger = logging.getLogger(__name__)

class AzureSQLClient:

    def __init__(self):
        self.database = Config.SQL_DATABASE
        self.driver = Config.SQL_DRIVER
        self.password = Config.SQL_PASSWORD
        self.server = Config.SQL_SERVER
        self.username = Config.SQL_USERNAME
        self.connection = self.connect()
        self.cursor = self.connection.cursor() if self.connection else None


    # Establishes a connection to the Azure SQL Database using the provided configuration
    def connect(self):
        logger.info(
            "Attempting SQL connection server=%s database=%s",
            self.server,
            self.database
        )

        connection_string = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
        try:
            connection = pyodbc.connect(connection_string)
            return connection
        
        except Exception as e:
            logger.error(f"Error connecting to Azure SQL Database: {e}")
            return None

    # This function inserts a new record into the tblOutlookEventsY table with the provided event details, transcript status, and ClickUp task ID
    def sql_insert_new_record (self, event, get_transcript, clickup_task_id):

        insert_sql = """
            INSERT INTO tblOutlookEventsY (event_id, joinURL_id, is_cancelled, is_organizer, event_type, is_online_meeting, online_meeting_provider, 
                                        response_status, subject, organizer, start_time, end_time, location, categories, duration, attendees,
                                        is_recording_exist, is_transcript_exist, get_transcript, get_transcript_done, summarize_transcript_done, clickup_task_id, update_clickup_done)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
        
        try:
            self.cursor.execute(insert_sql, (event.event_id, event.join_url, event.is_cancelled, event.is_organizer, event.event_type, event.is_online_meeting, event.online_meeting_provider, 
                                        event.response_status, event.subject, event.organizer, event.formatted_start, event.formatted_end, event.location, 
                                        event.categories_str, event.duration_str, event.attendees_str, 'False', False, get_transcript, False, False, clickup_task_id, False))
            self.connection.commit()
            logger.info(f"Added event {event.event_id} into the database.")
            return True
        
        except Exception as sql_execution_error:
            logger.error(f"Error while adding event {event.event_id} in the database: {sql_execution_error}")
            return False


    # This function updates an existing record in the tblOutlookEventsY table with the latest event details, transcript status, and ClickUp task ID based on the event_id
    def sql_update_outlook_metadata(self, event, get_transcript):
        update_sql = """
            UPDATE tblOutlookEventsY
            SET is_cancelled = ?, is_organizer = ?, event_type = ?, is_online_meeting = ?, online_meeting_provider = ?, 
                response_status = ?, subject = ?, organizer = ?, start_time = ?, end_time = ?, location = ?, 
                categories = ?, duration = ?, attendees = ?, get_transcript = ?
            WHERE event_id = ? """
        try:
            self.cursor.execute(update_sql, (event.is_cancelled, event.is_organizer, event.event_type, event.is_online_meeting, event.online_meeting_provider, 
                                        event.response_status, event.subject, event.organizer, event.formatted_start, event.formatted_end, event.location, 
                                        event.categories_str, event.duration_str, event.attendees_str, get_transcript, event.event_id))
            self.connection.commit()
            logger.info(f"Updated event {event.event_id} in the database.")
            return True

        except Exception as sql_execution_error:
            logger.error(f"Error while updating event {event.event_id} in the database: {sql_execution_error}")
            return False


    # This function updates the summarized transcript and the status of transcript retrieval and summarization in the tblOutlookEventsY table based on the event_id
    def sql_update_record (self, summarized_transcript, event_id, transcript_done):
        try:
            update_sql = """
                UPDATE tblOutlookEventsY
                SET get_transcript_done = ?, summarize_transcript_done = ?, summarized_transcript = ?
                WHERE event_id = ? """
            self.cursor.execute(update_sql, (transcript_done, transcript_done, summarized_transcript, event_id))
            self.connection.commit()
            return True
        
        except Exception as sql_execution_error:
            logger.error(f"Error while updating event {event_id} in the database: {sql_execution_error}")
            return False