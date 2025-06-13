import logging
import azure.functions as func
import logging
from datetime import datetime, timedelta
import pytz

from api_graph import *
from api_gpt import *
from api_clickup import *
from utils import *
from sql_azure_db import *

app = func.FunctionApp()

@app.timer_trigger(schedule="15-59/15,0,15,30,45 21-23,0-7 * * 0-4", arg_name="myTimer", run_on_startup=True, use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    main()
    logging.info('Python timer trigger function executed.')


def main():

    utc_now = datetime.now(pytz.utc) 
    logging.info (f"Scripts started at: {utc_now}")

    one_day_ago = utc_now - timedelta(days=1)
    start_date = one_day_ago.strftime('%Y-%m-%dT00:00:00Z')
    end_date_utc = utc_now + timedelta(days=2)
    end_date = end_date_utc.strftime('%Y-%m-%dT23:59:59Z')

    conn, cursor = sql_connection()
    if not conn and cursor:
        return
    
    access_token = get_global_graphAPI_token ()
    users_list = get_users()

    for user in users_list:

        log_and_print (f"\n\n\n[ ===============================     Processing meetings for {user}     =============================== ]\n")
        business_advisor_name = get_user_id_by_email(user, access_token, "displayName")
        calendar_events = get_outlook_metadata(access_token, user, start_date, end_date)

        for event in calendar_events:

            log_and_print("-------------------------------------------------------------------------------------------------- \n")
            get_transcript = 0

            # exclude all meetings that don't fall under the category of [client - retainer] and [client - diagnostic]
            if not ('client - retainer' in event.get("categories_str").lower() or 'client - diagnostic' in event.get("categories_str").lower()):
                log_and_print (f"NOT INCLUDED | Subject: {event.get('subject')} | Start Date/Time: {event.get('start_time')} | Category: xxxxx \n")
                continue
            else:
                log_and_print (f"Subject: {event.get('subject')} | Category: {event.get('categories_str')}")
                log_and_print (f"Start Date/Time: {event.get('start_time')} ")

            # retrieve record from sql database based on event ID
            check_sql = """ SELECT get_transcript_done, summarize_transcript_done, clickup_task_id FROM tblOutlookEventsY WHERE event_id = ? """
            cursor.execute(check_sql, (event.get("event_id"),))
            result = cursor.fetchone()

            endtime_str = event.get("end_time")[:26]
            endtime = datetime.fromisoformat(endtime_str).replace(tzinfo=pytz.UTC)
            now = utc_now + timedelta(hours=8) 

            if endtime < now: get_transcript = 1

            # add new clickup task in Calendar Events v.001
            if not result:

                clickup_task_id = create_clickup_task (event.get("subject"), business_advisor_name, event.get("is_cancelled"), event.get("is_cancelled"), event.get("formatted_st"), event.get("duration_str"), event.get("categories_str"), event.get("attendees_str"), 0, 0, 'Pending', 0)
                if create_clickup_task:
                    sql_insert_new_record(cursor, conn, event, get_transcript, clickup_task_id)
                else:
                    log_and_print_err(f"Unable to create ClickUp task and add new record in SQL database.")

                continue

            # process existing events stored in database
            get_transcript_done, summarize_transcript_done, clickup_task_id = result # SQL query results

            # skip processed events
            if get_transcript_done != False and summarize_transcript_done != False:
                continue

            # update event metadata in database
            sql_update_outlook_metadata(cursor, conn, event, get_transcript)

            # skip events that have not yet finished
            if not get_transcript == 1:
                continue

            # try to retrieve transcript from MS Teams and send it to Azure OpenAI for summarization
            log_and_print ("Getting Transcript...")
            filtered_vtt = None
            summarized_transcript = None
            user_microsoft_id = get_user_id_by_email(user, access_token, "id")

            if not user_microsoft_id: 
                log_and_print_err(f"Unable to get microsft id for {user}")
                continue

            yesterday = utc_now - timedelta(days=1)
            start_date_Tminus1 = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT00:00:00Z')
            transcript_found_and_ready = False

            # get transcript URL by decoding teams meeting id and match it with outlook's join URL
            transcript_URL = get_transcript_content_url(access_token,user_microsoft_id,event.get("joinURL"),start_date_Tminus1,end_date)
            if transcript_URL:
                log_and_print ("Retrieving vtt...")
                filtered_vtt = get_filtered_vtt(access_token, transcript_URL)
                
            # get transcript contents (vtt)
            if filtered_vtt:
                summarized_transcript = summarize_func(filtered_vtt)
                transcript_found_and_ready = True

            # transcript not found
            if not transcript_found_and_ready and not summarized_transcript:
                update_clickup_task(clickup_task_id, 'No', 'No', 'Transcript Not Found', 'No')
                sql_update_record(cursor, conn, summarized_transcript, event.get("event_id"), 0)
                continue

            # update both Clickup and SQL database if VVT is found and transcript is summarized

            # client email as clickup reference ID
            client_email = event.get("attendees_str")
            email_list = []

            if isinstance(client_email, str):
                email_list = [email.strip() for email in client_email.split(",")]

                if user in email_list: # exclude organizer
                    email_list.remove(user) 

            task_name = None

            # find company name as task in case overload by email address
            for email in email_list:
                task_name_diagnostic = find_task_by_email(email, 'DIAGNOSTIC')
                if task_name_diagnostic:
                    task_name = task_name_diagnostic
                    break
                task_name_retainer = find_task_by_email(email, 'RETAINER')
                if task_name_retainer:
                    task_name = task_name_retainer
                    break

            ai_task_name = f"AI Notes: {event.get('subject')}"
            task_description = summarized_transcript

            # if company name is found, add task to temp folder
            if task_name:
                # find clients folder then create a new task for the summarization
                client_folder_diagnostic_id = find_folder_by_task_name (task_name,'90160216966')
                if client_folder_diagnostic_id:
                    log_and_print(f"Searching Diagnostic folder in Client Delivery...")
                    add_task_to_list(client_folder_diagnostic_id, ai_task_name, task_description) # SUCCESS
                else:
                    log_and_print(f"Searching Diagnostic folder in Client Delivery...")
                    client_folder_retainer_id = find_folder_by_task_name (task_name,'90160216968')
                    if client_folder_retainer_id:
                        add_task_to_list(client_folder_retainer_id, ai_task_name, task_description) # SUCCESS

                    # if client folder cannot be found in either Retainer or Diagnostic, add to user's temp folder
                    else: 
                        log_and_print("Task Found: Add to temp")
                        add_task_to_temp_list(business_advisor_name, ai_task_name, task_description)

            else:
                log_and_print("Task NOT Found: Add to temp")
                add_task_to_temp_list(business_advisor_name, ai_task_name, task_description)


            # AI summarization is complete
            update_clickup_task(clickup_task_id, 'Yes', 'Yes', summarized_transcript, 'Yes')
            sql_update_record(cursor, conn, summarized_transcript, event.get("event_id"), 1)

                    
    cursor.close()
    conn.close()

       

