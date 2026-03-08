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

        # self.connection, self.cursor = self.connect()

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
        
    def sql_insert_new_record (self, event, get_transcript, clickup_task_id):

        insert_sql = """
            INSERT INTO tblOutlookEventsY (event_id, joinURL_id, is_cancelled, is_organizer, event_type, is_online_meeting, online_meeting_provider, 
                                        response_status, subject, organizer, start_time, end_time, location, categories, duration, attendees,
                                        is_recording_exist, is_transcript_exist, get_transcript, get_transcript_done, summarize_transcript_done, clickup_task_id, update_clickup_done)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
        
        try:
            self.cursor.execute(insert_sql, (event.get("event_id"), event.get("joinURL"), event.get("is_cancelled"), event.get("is_cancelled"), event.get("event_type"), event.get("is_online_meeting"), event.get("online_meeting_provider"), 
                                        event.get("response_status"), event.get("subject"), event.get("organizer"), event.get("formatted_st"), event.get("formatted_et"), event.get("location"), 
                                        event.get("categories_str"), event.get("duration_str"), event.get("attendees_str"), 'False', False, get_transcript, False, False, clickup_task_id, False))
            self.connection.commit()
            logger.info(f"Added event {event.get('event_id')} into the database.")
            return True
        
        except Exception as sql_execution_error:
            logger.error(f"Error while adding event {event.get('event_id')} in the database: {sql_execution_error}")
            return False


    def sql_update_outlook_metadata(self, event, get_transcript):
        update_sql = """
            UPDATE tblOutlookEventsY
            SET is_cancelled = ?, is_organizer = ?, event_type = ?, is_online_meeting = ?, online_meeting_provider = ?, 
                response_status = ?, subject = ?, organizer = ?, start_time = ?, end_time = ?, location = ?, 
                categories = ?, duration = ?, attendees = ?, get_transcript = ?
            WHERE event_id = ? """
        try:
            self.cursor.execute(update_sql, (event.get("is_cancelled"), event.get("is_cancelled"), event.get("event_type"), event.get("is_online_meeting"), event.get("online_meeting_provider"), 
                                        event.get("response_status"), event.get("subject"), event.get("organizer"), event.get("formatted_st"), event.get("formatted_et"), event.get("location"), 
                                        event.get("categories_str"), event.get("duration_str"), event.get("attendees_str"), get_transcript, event.get("event_id")))
            self.connection.commit()
            logger.info(f"Updated event {event.get('event_id')} in the database.")
            return True

        except Exception as sql_execution_error:
            logger.error(f"Error while updating event {event.get('event_id')} in the database: {sql_execution_error}")
            return False


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