import requests
import time
import logging
from src.core.config import Config

logger = logging.getLogger(__name__)

class ClickUpClient:

    # This class provides methods to interact with the ClickUp API, including creating and updating tasks, retrieving user lists, and handling rate limits.
    def __init__(self):
        self.api_token = Config.CLICKUP_API_TOKEN
        self.users_list_id = Config.CLICKUP_USERS_LIST_ID
        self.base_url = "https://api.clickup.com/api/v2"

        self.BusinessAdviser = Config.CUSTOM_FIELD_ID_BusinessAdviser
        self.Organizer = Config.CUSTOM_FIELD_ID_Organizer
        self.MeetingCancelled = Config.CUSTOM_FIELD_ID_MeetingCancelled
        self.StartTime = Config.CUSTOM_FIELD_ID_StartTime
        self.Duration = Config.CUSTOM_FIELD_ID_Duration
        self.Categories = Config.CUSTOM_FIELD_ID_Categories
        self.Attendees = Config.CUSTOM_FIELD_ID_Attendees
        self.TranscriptFound = Config.CUSTOM_FIELD_ID_TranscriptFound
        self.AIAPIDone = Config.CUSTOM_FIELD_ID_AIAPIDone
        self.SummarizedTranscript = Config.CUSTOM_FIELD_ID_SummarizedTranscript
        self.ClickUpAPIDone = Config.CUSTOM_FIELD_ID_ClickUpAPIDone

        self.BA_LIST = Config.BA_LIST
        self.OTHERS_LIST_ID = Config.OTHERS_LIST_ID


    # This function handles all ClickUp API requests and implements rate limit handling
    def request_clickup(action,url,headers,json=False):

        if action == 'Get':
            response = requests.get(url, headers=headers)
        elif action == 'Post':
            response = requests.post(url, headers=headers, json=json)
        elif action == 'Put':
            response = requests.put(url, headers=headers, json=json)

        while True:
            limit = response.headers.get("X-RateLimit-Limit")
            remaining = response.headers.get("X-RateLimit-Remaining")
            int_remaining = int(remaining)
            logger.info(f"ClickUp Rate Limit: {remaining}/{limit} remaining")
            
            if response.status_code == 429 or int_remaining < 20:
                time.sleep(30)
                continue

            return response


    # This function retrieves the list of users from ClickUp and returns their names as a list
    def get_users(self):

        url = f'{self.base_url}/list/{self.users_list_id}/task'
        headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }

        response = self.request_clickup('Get', url, headers)
        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            userID = [task['name'] for task in tasks]
            return userID
        else:
            logger.error(f"Failed to retrieve user list. Status code: {response.status_code}")


    # This function creates a new task in ClickUp with the provided details and returns the task ID
    def create_clickup_task (self, subject, user, is_organizer, is_cancelled, formatted_st, duration_str, categories_str, attendees_str, transcript_found, ai_api_done, summarized_transcript, clickup_api_done):
        
        logger.info("Running create_clickup_task function...")
        
        url = f'{self.base_url}/list/{self.calendar_events_list_id}/task'
        headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'name': f"{subject}",
            'description': 'This task was created via the ClickUp API using Python.',
            'status': 'IN PROGRESS',
            'custom_fields': [
                {
                    'id': self.BusinessAdviser, # Business Adviser
                    'value': f"{user}"  
                },
                {
                    'id': self.Organizer, # Organizer
                    'value': f"{is_organizer}"  
                },
                {
                    'id': self.MeetingCancelled, # Meeting Cancelled?
                    'value': f"{is_cancelled}"  
                },
                {
                    'id': self.StartTime, # Start Time
                    'value': f"{formatted_st}"  
                },
                {
                    'id': self.Duration, # Duration
                    'value': f"{duration_str}"  
                },
                {
                    'id': self.Categories, # Categories
                    'value': f"{categories_str}"  
                },
                {
                    'id': self.Attendees, # Attendees
                    'value': f"{attendees_str}"  
                },
                {
                    'id': self.TranscriptFound, # transcript_found
                    'value': f"{transcript_found}"  
                },
                {
                    'id': self.AIAPIDone, # ai_api_done
                    'value': f"{ai_api_done}"  
                },
                {
                    'id': self.SummarizedTranscript, # summarized_transcript
                    'value': f"{summarized_transcript}"  
                },
                {
                    'id': self.ClickUpAPIDone, # clickup_api_done
                    'value': f"{clickup_api_done}"  
                }
            ]
        }

        response = self.request_clickup('Post', url, headers, payload)
        if response.status_code == 200:
            logger.info("Task created successfully!")
            task = response.json()
            task_id = task['id']
            return (task_id)
        else:
            logger.error("Failed to create task.")
            logger.error(f"Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")


    # This function updates the specified ClickUp task with the provided details and marks it as complete if the clickup_api_done field is set to 'Yes'
    def update_clickup_task(self, clickup_task_id, transcript_found, ai_api_done, summarized_transcript, clickup_api_done):

        task_id = clickup_task_id

        custom_fields_to_update = {
            self.TranscriptFound: f"{transcript_found}", # Transcript Found?
            self.AIAPIDone: f"{ai_api_done}", # AI API Done? 
            self.SummarizedTranscript: f"{summarized_transcript}",  # Summarized Transcript
            self.ClickUpAPIDone: f"{clickup_api_done}",  # ClickUp API Done?
        }

        headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }

        for field_id, value in custom_fields_to_update.items():
            url = f'{self.base_url}/task/{task_id}/field/{field_id}'
            payload = {"value": value}

            response = self.request_clickup('Post', url, headers, payload)
            if response.status_code == 200:
                logger.info(f"Custom field {field_id} updated to '{value}'")
            else:
                logger.error(f"Failed to update field {field_id}")
                logger.error(f"Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")

        if clickup_api_done == 'Yes':
            new_status = 'Complete'
        else: 
            new_status = 'In Progress'
            
        payload = {
            "description": summarized_transcript,
            "status": new_status
        }
        url = f'{self.base_url}/task/{task_id}'
        response = self.request_clickup('Put', url, headers, payload)
        if response.status_code == 200:
            logger.info("Task has been updated!")
        else:
            logger.error("Failed to mark task as complete.")
            logger.error(f"Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")


    # This function searches for a task in the specified ClickUp folder that has a custom field matching the target email and returns the task name if found, otherwise returns None
    def find_task_by_email(self, target_email, folder):

        logger.info(f"Searching task in Caseload Overview - {folder}: {target_email}")

        url = f"{self.base_url}/view/8cewk4m-13996/task?status={folder}"
        headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }

        response = self.request_clickup('Get', url, headers)

        if response.status_code != 200:
            logger.error(f"Failed to retrieve tasks. Status Code: {response.status_code}")
            return None

        tasks = response.json().get('tasks', [])

        for task in tasks:
            for custom_field in task.get('custom_fields', []):
                if custom_field.get('name') == "Email" and custom_field.get('value') == target_email:
                    logger.info(f"Task found: {task['name']}")
                    return task['name']
                email_value = custom_field.get('value')
                if custom_field.get('name') == "Email - Associates" and email_value:
                    if email_value.find(target_email) != -1:
                        logger.info(f"Task found: {task['name']}")
                        return task['name']
                
                
        # try again using pagination maxed limit
        page = 0
        while page != 11:
            print(page)
            url = f"{self.base_url}/view/8cewk4m-13996/task?status={folder}&page={page}&limit=100"

            response = self.request_clickup('Get', url, headers)
            if response.status_code != 200:
                logger.error(f"Failed to retrieve tasks. Status Code: {response.status_code}")
                return None

            tasks = response.json().get('tasks', [])

            for task in tasks:
                for custom_field in task.get('custom_fields', []):
                    if custom_field.get('name') == "Email" and custom_field.get('value') == target_email:
                        logger.info(f"Task found: {task['name']}")
                        return task['name']
                    email_value = custom_field.get('value')
                    if custom_field.get('name') == "Email - Associates" and email_value:
                        if email_value.find(target_email) != -1:
                            logger.info(f"Task found: {task['name']}")
                            return task['name']

            page +=1 
        
        logger.info("Not Found")
        return None


    # This function searches for a folder in the specified ClickUp list that matches the target task name and returns the folder ID if found, otherwise returns None
    def find_folder_by_task_name (self, task_name, list_id):

        url = f"{self.base_url}/folder/{list_id}/list"
        headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }

        response = self.request_clickup('Get', url, headers)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve lists. Status Code: {response.status_code}")
            return None

        lists = response.json().get('lists', [])
        for list_item in lists:
            if list_item['name'] == task_name:
                logger.info(f"List found: {list_item['id']}")
                return list_item['id']  

        logger.info("Not Found")
        return None


    # This function creates a new task in the specified ClickUp list with the provided task name and description
    def add_task_to_list(self, list_id, task_name, task_description):

        logger.info(f"Adding AI Meeting Notes task to client's folder.")
        
        task_url = f"{self.base_url}/list/{list_id}/task" 
        headers = {
            "Authorization": self.api_token
        }

        task_data = {
            "name": task_name,
            "description": task_description
        }

        response = self.request_clickup('Post', task_url, headers, task_data)
        if response.status_code == 200:
            logger.info(f"Task '{task_name}' successfully created in list ID {list_id}.")
        else:
            logger.error(f"Func Name: add_task_to_list | Failed to create task. Status Code: {response.status_code}")
        
        return None


    # This function creates a new task in the AI Meeting Notes temporary folder with the provided task name and description, assigning it to the appropriate business advisor based on the provided name
    def add_task_to_temp_list(self, ba_name, task_name, task_description):

        logger.info(f"Adding AI Meeting Notes task to AI Meeting Notes temporary folder.")

        ba_id = None
        for ba in self.BA_LIST:
            if ba["name"].lower() == ba_name.lower():
                ba_id = ba["id"]
                break  
        
        if ba_id is None:
            ba_id = self.OTHERS_LIST_ID #Others folder

        task_url = f"{self.base_url}/list/{ba_id}/task"
        headers = {
            "Authorization": self.api_token
        }

        task_data = {
            "name": task_name,
            "description": task_description
        }

        response = self.request_clickup('Post', task_url, headers, task_data)
        if response.status_code == 200:
            logger.info(f"Task '{task_name}' successfully created in list ID {ba_id}.")
        else:
            logger.error(f"Func Name: add_task_to_temp_list | Failed to create task. Status Code: {response.status_code}")
        
        return None