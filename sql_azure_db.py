import pyodbc
from utils import log_and_print, log_and_print_err

import os
SQL_SERVER = os.environ["SQL_SERVER"]
SQL_PASSWORD = os.environ["SQL_PASSWORD"]
SQL_DATABASE = os.environ["SQL_DATABASE"]
SQL_DRIVER = os.environ["SQL_DRIVER"]
SQL_USERNAME = os.environ["SQL_USERNAME"]

def sql_connection ():

    try:
        conn = pyodbc.connect(f'DRIVER={SQL_DRIVER};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USERNAME};PWD={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30')
        cursor = conn.cursor()
    except pyodbc.Error as e:
        log_and_print_err(f"Database connection error: {e}")
        return None
    
    return conn, cursor


def sql_insert_new_record (cursor, conn, event, get_transcript, clickup_task_id):

    insert_sql = """
        INSERT INTO tblOutlookEventsY (event_id, joinURL_id, is_cancelled, is_organizer, event_type, is_online_meeting, online_meeting_provider, 
                                    response_status, subject, organizer, start_time, end_time, location, categories, duration, attendees,
                                    is_recording_exist, is_transcript_exist, get_transcript, get_transcript_done, summarize_transcript_done, clickup_task_id, update_clickup_done)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
    
    try:
        cursor.execute(insert_sql, (event.get("event_id"), event.get("joinURL"), event.get("is_cancelled"), event.get("is_cancelled"), event.get("event_type"), event.get("is_online_meeting"), event.get("online_meeting_provider"), 
                                    event.get("response_status"), event.get("subject"), event.get("organizer"), event.get("formatted_st"), event.get("formatted_et"), event.get("location"), 
                                    event.get("categories_str"), event.get("duration_str"), event.get("attendees_str"), 'False', False, get_transcript, False, False, clickup_task_id, False))
        conn.commit()
        log_and_print(f"Added event {event.get('event_id')} into the database.")
        return True
    
    except Exception as sql_execution_error:
        log_and_print_err(f"Error while adding event {event.get('event_id')} in the database: {sql_execution_error}")
        return False


def sql_update_outlook_metadata(cursor, conn, event, get_transcript):
    update_sql = """
        UPDATE tblOutlookEventsY
        SET is_cancelled = ?, is_organizer = ?, event_type = ?, is_online_meeting = ?, online_meeting_provider = ?, 
            response_status = ?, subject = ?, organizer = ?, start_time = ?, end_time = ?, location = ?, 
            categories = ?, duration = ?, attendees = ?, get_transcript = ?
        WHERE event_id = ? """
    try:
        cursor.execute(update_sql, (event.get("is_cancelled"), event.get("is_cancelled"), event.get("event_type"), event.get("is_online_meeting"), event.get("online_meeting_provider"), 
                                    event.get("response_status"), event.get("subject"), event.get("organizer"), event.get("formatted_st"), event.get("formatted_et"), event.get("location"), 
                                    event.get("categories_str"), event.get("duration_str"), event.get("attendees_str"), get_transcript, event.get("event_id")))
        conn.commit()
        log_and_print(f"Updated event {event.get('event_id')} in the database.")
        return True

    except Exception as sql_execution_error:
        log_and_print_err(f"Error while updating event {event.get('event_id')} in the database: {sql_execution_error}")
        return False


def sql_update_record (cursor, conn, summarized_transcript, event_id, transcript_done):
    try:
        update_sql = """
            UPDATE tblOutlookEventsY
            SET get_transcript_done = ?, summarize_transcript_done = ?, summarized_transcript = ?
            WHERE event_id = ? """
        cursor.execute(update_sql, (transcript_done, transcript_done, summarized_transcript, event_id))
        conn.commit()
        return True
    
    except Exception as sql_execution_error:
        log_and_print_err(f"Error while updating event {event_id} in the database: {sql_execution_error}")
        return False



