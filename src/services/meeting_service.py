import logging
from datetime import datetime, timedelta
import pytz

from src.clients.graph_client import GraphClient
from src.clients.clickup_client import ClickUpClient
from src.clients.openai_client import OpenAIClient
from src.database.azure_sql import AzureSQLClient
from src.core.config import Config

logger = logging.getLogger(__name__)

class MeetingService:

    # Initialize the MeetingService with instances of GraphClient, ClickUpClient, OpenAIClient, and AzureSQLClient to handle interactions with Microsoft Graph API, ClickUp API, Azure OpenAI, and Azure SQL Database respectively.
    def __init__(self):

        self.graph = GraphClient()
        self.clickup = ClickUpClient()
        self.openai = OpenAIClient()
        self.azuredb = AzureSQLClient()


    def main(self):

        utc_now = datetime.now(pytz.utc)
        one_day_ago = utc_now - timedelta(days=1)
        start_date = one_day_ago.strftime('%Y-%m-%dT00:00:00Z')
        end_date_utc = utc_now + timedelta(days=1)
        end_date = end_date_utc.strftime('%Y-%m-%dT23:59:59Z')
        logger.info (f"Script started at: {utc_now}")

        if not self.azuredb.connection or not self.azuredb.cursor:
            logger.error("Unable to connect to Azure SQL Database. Exiting the script.")
            return
        
        logger.info(f"Processing meetings from {start_date} to {end_date}...")

        # users_list = self.clickup.get_users()
        users_list = ['tech@theoutperformer.co']
        logger.info(f"Retrieved list of users: {users_list}")

        for user in users_list:

            logger.info (f"\n\n\n[ ===============================     Processing meetings for {user}     =============================== ]\n")

            business_advisor_name = self.graph.get_user_id_by_email(user, "displayName")
            calendar_events = self.graph.get_outlook_metadata(user, start_date, end_date)

            for event in calendar_events:

                logger.info("-------------------------------------------------------------------------------------------------- \n")
                get_transcript = 0

                # exclude all meetings that don't fall under the category of [client - retainer] and [client - diagnostic]
                if not ('client - retainer' in event.categories_str.lower() or 'client - diagnostic' in event.categories_str.lower()):
                    logger.info (f"NOT INCLUDED | Subject: {event.subject} | Start Date/Time: {event.start_time} | Category: xxxxx \n")
                    continue
                else:
                    logger.info (f"Subject: {event.subject} | Category: {event.categories_str}")
                    logger.info (f"Start Date/Time: {event.start_time} ")

                # retrieve record from sql database based on event ID
                check_sql = """ SELECT get_transcript_done, summarize_transcript_done, clickup_task_id FROM tblOutlookEventsY WHERE event_id = ? """
                self.azuredb.cursor.execute(check_sql, (event.event_id,))
                result = self.azuredb.cursor.fetchone()

                # logger.info(f"Database check result for event {event.event_id}: {result}")

                endtime_str = event.end_time[:26]
                endtime = datetime.fromisoformat(endtime_str).replace(tzinfo=pytz.UTC)
                now = utc_now + timedelta(hours=8) 

                if endtime < now: get_transcript = 1

                # add new clickup task in Calendar Events v.001
                if not result:
                    clickup_task_id = self.clickup.create_clickup_task (event.subject, business_advisor_name, event.is_cancelled, event.is_cancelled, event.formatted_start, event.duration_str, event.categories_str, event.attendees_str, 0, 0, 'Pending', 0)
                    if clickup_task_id:
                        logger.info(f"Created ClickUp task with ID: {clickup_task_id} for event: {event.event_id}")
                        self.azuredb.sql_insert_new_record(event, get_transcript, clickup_task_id)
                    else:
                        logger.error(f"Unable to create ClickUp task and add new record in SQL database.")
                    
                    continue

                # process existing events stored in database
                get_transcript_done, summarize_transcript_done, clickup_task_id = result # SQL query results
                logger.info(f"Existing record found in database for event: {event.event_id} | get_transcript_done: {get_transcript_done} | summarize_transcript_done: {summarize_transcript_done} | clickup_task_id: {clickup_task_id}")    

                # skip processed events
                if get_transcript_done != False and summarize_transcript_done != False:
                    continue

                # update event metadata in database
                self.azuredb.sql_update_outlook_metadata(event, get_transcript)

                # skip events that have not yet finished
                if not get_transcript == 1:
                    continue

                # try to retrieve transcript from MS Teams and send it to Azure OpenAI for summarization
                logger.info("Getting Transcript...")
                filtered_vtt = None
                summarized_transcript = None
                user_microsoft_id = self.graph.get_user_id_by_email(user, "id")
                logger.info(f"Microsoft ID for {user}: {user_microsoft_id}")

                if not user_microsoft_id: 
                    logger.error(f"Unable to get Microsoft id for {user}")
                    continue

        self.azuredb.cursor.close()
        self.azuredb.connection.close()







        #         yesterday = utc_now - timedelta(days=1)
        #         start_date_Tminus1 = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT00:00:00Z')
        #         transcript_found_and_ready = False

        #         # get transcript URL by decoding teams meeting id and match it with outlook's join URL
        #         transcript_URL = get_transcript_content_url(access_token,user_microsoft_id,event.get("joinURL"),start_date_Tminus1,end_date)
        #         if transcript_URL:
        #             log_and_print ("Retrieving vtt...")
        #             filtered_vtt = get_filtered_vtt(access_token, transcript_URL)
                    
        #         # get transcript contents (vtt)
        #         if filtered_vtt:
        #             summarized_transcript = summarize_func(filtered_vtt)
        #             transcript_found_and_ready = True

        #         # transcript not found
        #         if not transcript_found_and_ready and not summarized_transcript:
        #             update_clickup_task(clickup_task_id, 'No', 'No', 'Transcript Not Found', 'No')
        #             sql_update_record(cursor, conn, summarized_transcript, event.get("event_id"), 0)
        #             continue

        #         # update both Clickup and SQL database if VVT is found and transcript is summarized

        #         # client email as clickup reference ID
        #         client_email = event.get("attendees_str")
        #         email_list = []

        #         if isinstance(client_email, str):
        #             email_list = [email.strip() for email in client_email.split(",")]

        #             if user in email_list: # exclude organizer
        #                 email_list.remove(user) 

        #         task_name = None

        #         # find company name as task in case overload by email address
        #         for email in email_list:
        #             task_name_diagnostic = find_task_by_email(email, 'DIAGNOSTIC')
        #             if task_name_diagnostic:
        #                 task_name = task_name_diagnostic
        #                 break
        #             task_name_retainer = find_task_by_email(email, 'RETAINER')
        #             if task_name_retainer:
        #                 task_name = task_name_retainer
        #                 break

        #         date_str = event.get('start_time')
        #         dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f0")
        #         formatted_date = f"{dt.month}/{dt.day}"

        #         ai_task_name = f"AI Notes {formatted_date}: {event.get('subject')}"
        #         task_description = summarized_transcript

        #         # if company name is found, add task to temp folder
        #         if task_name:
        #             # find clients folder then create a new task for the summarization
        #             log_and_print(f"Searching Diagnostic folder in Client Delivery...")
        #             client_folder_diagnostic_id = find_folder_by_task_name (task_name, DIAGNOSTIC_ID)
        #             if client_folder_diagnostic_id:
        #                 add_task_to_list(client_folder_diagnostic_id, ai_task_name, task_description) # SUCCESS
        #                 update_clickup_task(clickup_task_id, 'Yes', 'Yes', summarized_transcript, 'Yes')
        #             else:
        #                 log_and_print(f"Searching Retainer folder in Client Delivery...")
        #                 client_folder_retainer_id = find_folder_by_task_name (task_name, RETAINER_ID)
        #                 if client_folder_retainer_id:
        #                     add_task_to_list(client_folder_retainer_id, ai_task_name, task_description) # SUCCESS
        #                     update_clickup_task(clickup_task_id, 'Yes', 'Yes', summarized_transcript, 'Yes')

        #                 # if client folder cannot be found in either Retainer or Diagnostic, add to user's temp folder
        #                 else: 
        #                     log_and_print("Task Found: Add to temp")
        #                     add_task_to_temp_list(business_advisor_name, ai_task_name, task_description)
        #                     update_clickup_task(clickup_task_id, 'Yes', 'Yes', summarized_transcript, 'No')

        #         else:
        #             log_and_print("Task NOT Found: Add to temp")
        #             add_task_to_temp_list(business_advisor_name, ai_task_name, task_description)
        #             update_clickup_task(clickup_task_id, 'Yes', 'Yes', summarized_transcript, 'No')

        #         # AI summarization is complete
        #         sql_update_record(cursor, conn, summarized_transcript, event.get("event_id"), 1)
                        
        # cursor.close()
        # conn.close()

        

