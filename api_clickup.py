from datetime import datetime
from utils import log_and_print, log_and_print_err
import requests
# from config import CLICKUP_USERS_LIST_ID, CLICKUP_API_TOKEN
import os
CLICKUP_API_TOKEN = os.environ["CLICKUP_API_TOKEN"]
CLICKUP_USERS_LIST_ID = os.environ["CLICKUP_USERS_LIST_ID"]

# ===============================================================================================================================
def get_users():

    url = f'https://api.clickup.com/api/v2/list/{CLICKUP_USERS_LIST_ID}/task'
    headers = {
        'Authorization': CLICKUP_API_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tasks = response.json().get('tasks', [])
        userID = [task['name'] for task in tasks]
        return userID
    else:
        log_and_print_err(f"Failed to retrieve user list. Status code: {response.status_code}")


# ===============================================================================================================================
def create_clickup_task (subject, user, is_organizer, is_cancelled, formatted_st, duration_str, categories_str, attendees_str, transcript_found, ai_api_done, summarized_transcript, clickup_api_done):
    
    log_and_print("Running create_clickup_task function...")
    LIST_ID = '901607923627'
    url = f'https://api.clickup.com/api/v2/list/{LIST_ID}/task'

    headers = {
        'Authorization': CLICKUP_API_TOKEN,
        'Content-Type': 'application/json'
    }
    
    # dt = datetime.strptime(formatted_st, "%Y-%m-%d %H:%M:%S.%f")
    # formatted_time = dt.strftime("%#I:%M %p").lower()
    payload = {
        'name': f"{subject}",
        'description': 'This task was created via the ClickUp API using Python.',
        'status': 'IN PROGRESS',
        'custom_fields': [
            {
                'id': '39b77645-3b5a-4bed-8ac4-a0d72a41da04', # Business Adviser
                'value': f"{user}"  
            },
            {
                'id': '7e636aa4-74ca-4513-98a9-548771bfe3e7', # Organizer
                'value': f"{is_organizer}"  
            },
            {
                'id': 'edfb7a5c-e3d7-4169-8320-2a6bfa5360d2', # Meeting Cancelled?
                'value': f"{is_cancelled}"  
            },
            {
                'id': '6c0f53b0-c6c9-4146-aee8-becedb4a269d', # Start Time
                'value': f"{formatted_st}"  
                # 'value': f"{formatted_time}"  
            },
            {
                'id': 'f3a17d4b-0a86-415d-947c-a10d226c7317', # Duration
                'value': f"{duration_str}"  
            },
            {
                'id': '7a36625a-1e0b-44af-9704-ea6283ee7899', # Categories
                'value': f"{categories_str}"  
            },
            {
                'id': 'ea7b8386-1c1a-4a4d-ae09-c0469ae619a8', # Attendees
                'value': f"{attendees_str}"  
            },
            {
                'id': '1c046a74-78e0-4e67-ad98-19166dc1944a', # transcript_found
                'value': f"{transcript_found}"  
            },
            {
                'id': 'eb3a3076-1dac-4828-9a21-32d517571f5b', # ai_api_done
                'value': f"{ai_api_done}"  
            },
            {
                'id': '50aac2ec-9a07-4f6b-85dd-abdc783275e2', # summarized_transcript
                'value': f"{summarized_transcript}"  
            },
            {
                'id': '6e2ce93b-c451-43d2-8337-1c9fcd0e0e3d', # clickup_api_done
                'value': f"{clickup_api_done}"  
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        log_and_print("Task created successfully!")
        task = response.json()
        task_id = task['id']
        return (task_id)
    else:
        log_and_print_err("Failed to create task.")
        log_and_print_err(f"Status code: {response.status_code}")
        log_and_print_err(f"Response: {response.text}")


# ===============================================================================================================================
def update_clickup_task(clickup_task_id, transcript_found, ai_api_done, summarized_transcript, clickup_api_done):

    task_id = clickup_task_id

    # print(f"Updating Task: {clickup_task_id}")

    custom_fields_to_update = {
        '1c046a74-78e0-4e67-ad98-19166dc1944a': f"{transcript_found}", # Transcript Found?
        'eb3a3076-1dac-4828-9a21-32d517571f5b': f"{ai_api_done}", # AI API Done? 
        '50aac2ec-9a07-4f6b-85dd-abdc783275e2': f"{summarized_transcript}",  # Summarized Transcript
        '6e2ce93b-c451-43d2-8337-1c9fcd0e0e3d': f"{clickup_api_done}",  # ClickUp API Done?
    }

    headers = {
        'Authorization': CLICKUP_API_TOKEN,
        'Content-Type': 'application/json'
    }

    for field_id, value in custom_fields_to_update.items():
        url = f'https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}'
        payload = {"value": value}

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            log_and_print(f"Custom field {field_id} updated to '{value}'")
        else:
            log_and_print_err(f"Failed to update field {field_id}")
            log_and_print_err(f"Status code: {response.status_code}")
            log_and_print_err(f"Response: {response.text}")



    if clickup_api_done == 'Yes':
        new_status = 'Complete'
    else: 
        new_status = 'In Progress'
        
    payload = {
        "description": summarized_transcript,
        "status": new_status
    }
    url = f'https://api.clickup.com/api/v2/task/{task_id}'
    response = requests.put(url, json=payload, headers=headers)

    if response.status_code == 200:
        log_and_print("Task has been updated!")
    else:
        log_and_print_err("Failed to mark task as complete.")
        log_and_print_err(f"Status code: {response.status_code}")
        log_and_print_err(f"Response: {response.text}")


# ===============================================================================================================================
def find_task_by_email(target_email, folder):

    log_and_print(f"Searching task in Caseload Overview - {folder}: {target_email}")


    url = f"https://api.clickup.com/api/v2/view/8cewk4m-13996/task?status={folder}"
    headers = {
        'Authorization': CLICKUP_API_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        log_and_print_err(f"Failed to retrieve tasks. Status Code: {response.status_code}")
        return None

    tasks = response.json().get('tasks', [])

    for task in tasks:
        for custom_field in task.get('custom_fields', []):
            if custom_field.get('name') == "Email" and custom_field.get('value') == target_email:
                log_and_print(f"Task found: {task['name']}")
                return task['name']
            email_value = custom_field.get('value')
            if custom_field.get('name') == "Email - Associates" and email_value:
                if email_value.find(target_email) != -1:
                    log_and_print(f"Task found: {task['name']}")
                    return task['name']
            
            
    # try again using pagination and maxed limit
    url = f"https://api.clickup.com/api/v2/view/8cewk4m-13996/task?status={folder}&page=1&limit=999"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        log_and_print_err(f"Failed to retrieve tasks. Status Code: {response.status_code}")
        return None

    tasks = response.json().get('tasks', [])

    for task in tasks:
        for custom_field in task.get('custom_fields', []):
            if custom_field.get('name') == "Email" and custom_field.get('value') == target_email:
                log_and_print(f"Task found: {task['name']}")
                return task['name']
            email_value = custom_field.get('value')
            if custom_field.get('name') == "Email - Associates" and email_value:
                if email_value.find(target_email) != -1:
                    log_and_print(f"Task found: {task['name']}")
                    return task['name']
    
    log_and_print("Not Found")
    return None


# 90160216966 or 90160216968
def find_folder_by_task_name (task_name,list_id):

    # log_and_print(f"Searching folder in Client Delivery: {list_id}")

    url = f"https://api.clickup.com/api/v2/folder/{list_id}/list"
    headers = {
        'Authorization': CLICKUP_API_TOKEN,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        log_and_print_err(f"Failed to retrieve lists. Status Code: {response.status_code}")
        return None

    lists = response.json().get('lists', [])
    for list_item in lists:
        if list_item['name'] == task_name:
            log_and_print(f"List found: {list_item['id']}")
            return list_item['id']  

    log_and_print("Not Found")
    return None



def add_task_to_list(list_id, task_name, task_description):

    log_and_print(f"Adding AI Meeting Notes task to client's folder.")
    
    task_url = f"https://api.clickup.com/api/v2/list/{list_id}/task" 
    headers = {
        "Authorization": CLICKUP_API_TOKEN
    }

    task_data = {
        "name": task_name,
        "description": task_description
    }

    response = requests.post(task_url, json=task_data, headers=headers)

    if response.status_code == 200:
        log_and_print(f"Task '{task_name}' successfully created in list ID {list_id}.")
    else:
        log_and_print_err(f"Func Name: add_task_to_list | Failed to create task. Status Code: {response.status_code}")
    
    return None


def add_task_to_temp_list(ba_name, task_name, task_description):

    log_and_print(f"Adding AI Meeting Notes task to AI Meeting Notes temporary folder.")

    ba_list = [
        {"name": "Andre Pech", "id": "901608412938"},
        {"name": "Brad Eisenhuth", "id": "901608412955"},
        {"name": "Chris Wightwick", "id": "901608412958"},
        {"name": "Simone Dunlop", "id": "901608412963"}
    ]

    ba_id = None
    for ba in ba_list:
        if ba["name"].lower() == ba_name.lower():
            ba_id = ba["id"]
            break  
    
    if ba_id is None:
        ba_id = '901608414834' #Others folder

    task_url = f"https://api.clickup.com/api/v2/list/{ba_id}/task"
    headers = {
        "Authorization": "REMOVED_SECRET"
    }

    task_data = {
        "name": task_name,
        "description": task_description
    }

    response = requests.post(task_url, json=task_data, headers=headers)

    if response.status_code == 200:
        log_and_print(f"Task '{task_name}' successfully created in list ID {ba_id}.")
    else:
        log_and_print_err(f"Func Name: add_task_to_temp_list | Failed to create task. Status Code: {response.status_code}")
    
    return None
