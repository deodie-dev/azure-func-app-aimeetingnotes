# 📞 AI Meeting Notes Automation

This project automates the extraction, summarization, and documentation of Microsoft Teams client advisory calls. Built using Azure services, Microsoft Graph API, and OpenAI, the solution captures Outlook meeting metadata, retrieves Teams transcripts, summarizes them using GPT-4, stores data in Azure SQL, and updates CRM (ClickUp) — all on a scheduled basis.

---

## ⚙️ Tech Stack

- **Microsoft Graph API** – Fetches Outlook calendar and Teams transcript data.
- **Azure Function App** – Automates daily script execution.
- **Azure OpenAI (GPT-4)** – Summarizes meeting transcripts.
- **Azure SQL Database** – Stores meeting and summary data.
- **ClickUp API** – Updates CRM with summarized notes.
- **Python** – Primary programming language for all logic.

---

## 📂 Project Structure

```plaintext
.
├── function_app.py          # Main script triggered by Azure Function
├── api_graph.py             # Microsoft Graph API interaction logic
├── api_clickup.py           # ClickUp API integration (create/update tasks)
├── api_gpt.py               # Azure OpenAI (GPT-4) integration for summarization
├── data_process.py          # Meeting ID comparison and event data parsing
├── sql_azure_db.py          # Azure SQL DB interaction (insert/update records)
├── utils.py                 # Logging utilities
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

### `function_app.py`
- Main Azure Function trigger
- Orchestrates the full pipeline from data fetch → summarization → ClickUp update

### `api_graph.py`
- Handles Microsoft Graph authentication and API calls:
  - Get calendar events
  - Retrieve Teams meeting transcripts
  - Clean and extract VTT text
  - Look up user ID by email

### `api_clickup.py`
- Handles communication with ClickUp API:
  - Create or update ClickUp tasks
  - Attach summaries and metadata
  - Automate task status updates

### `api_gpt.py`
- Connects to Azure OpenAI (GPT-4) for:
  - Summarizing raw transcript text
  - Ensuring concise and accurate summaries for documentation

### `data_process.py`
- Extracts meeting IDs and compares them
- Formats event metadata
- Computes durations and attendee lists

### `sql_azure_db.py`
- Connects to Azure SQL Server
- Inserts and updates records in the `tblOutlookEventsY` table

### `utils.py`
- Logging utilities for tracking process flow and errors

---

## 🚀 Workflow Overview

1. **Trigger**  
   Azure Function App triggers `function_app.py` on a schedule (e.g. daily at 7 PM SGT).

2. **Fetch Calendar Events**  
   `api_graph.get_outlook_metadata()` pulls relevant meetings from Outlook Calendar within the defined date range.

3. **Process Event Metadata**  
   `data_process.parse_event()` extracts and cleans relevant data fields.

4. **Get Meeting Transcript**  
   `api_graph.get_transcript_content_url()` fetches the transcript URL for Teams calls.
   Then, `api_graph.get_filtered_vtt()` cleans the transcript (from VTT format).

5. **Summarize Using OpenAI GPT-4**  
   Transcript text is sent to Azure OpenAI, which returns a structured summary.

6. **Update Azure SQL Database**  
   `sql_azure_db.sql_insert_new_record()` or `sql_update_record()` inserts or updates meeting info and summaries.

7. **Update CRM (ClickUp)**  
   The summary is pushed to the relevant ClickUp task using the ClickUp API.

---

## 🧠 Key Features

- **Transcript Matching**  
  Uses encoded vs. raw meeting ID comparison for precise transcript mapping.

- **Resilient Logging**  
  All critical steps are logged using Python's logging module via `utils.py`.

- **Extensible Database**  
  SQL table `tblOutlookEventsY` tracks each meeting’s metadata, processing status, and summary content.

- **CRM Integration**  
  (Optional) Each meeting can be linked to a ClickUp task for automated note updates.

---

## ⚙️ Deployment

All Python files are deployed inside an **Azure Function App**, which runs automatically on a timer trigger. Environment variables (e.g., client credentials, SQL settings) are stored securely in the Azure Function configuration settings.

---

## 🛠️ Environment Variables (for local testing)

Create an `.env` file or set these as App Settings in your Azure Function App:

```env
GRAPH_APP_URL=
GRAPH_APP_CLIENT_ID=
GRAPH_APP_CLIENT_SECRET=

SQL_SERVER=
SQL_USERNAME=
SQL_PASSWORD=
SQL_DATABASE=
SQL_DRIVER={ODBC Driver 18 for SQL Server}

CLICKUP_API_TOKEN= 
CLICKUP_USERS_LIST_ID= 

OPENAI_API_KEY= 
OPENAI_URL= 
```

---

## 📦 Requirements

```bash
pip install -r requirements.txt
```

> Make sure to include `pyodbc`, `requests` and `pytz`
---

## 🔍 Sample SQL Table Structure (`tblOutlookEventsY`)

```sql
CREATE TABLE tblOutlookEventsY (
    event_id NVARCHAR(255) PRIMARY KEY,
    joinURL_id NVARCHAR(MAX),
    is_cancelled BIT,
    is_organizer BIT,
    event_type NVARCHAR(100),
    is_online_meeting BIT,
    online_meeting_provider NVARCHAR(100),
    response_status NVARCHAR(100),
    subject NVARCHAR(500),
    organizer NVARCHAR(255),
    start_time DATETIME,
    end_time DATETIME,
    location NVARCHAR(255),
    categories NVARCHAR(MAX),
    duration NVARCHAR(20),
    attendees NVARCHAR(MAX),
    is_recording_exist BIT,
    is_transcript_exist BIT,
    get_transcript BIT,
    get_transcript_done BIT,
    summarize_transcript_done BIT,
    summarized_transcript NVARCHAR(MAX),
    clickup_task_id NVARCHAR(100),
    update_clickup_done BIT
);
```

---

## 🧪 Testing Locally

You can test the main script by running:

```bash
python function_app.py
```

Ensure your environment variables are loaded or defined before running.

---

## 📈 Potential Extensions

- Email summary notifications to attendees.
- Auto-detect client names and topics from transcript.
- Multi-user or multi-team support.
- Transcription language detection and translation.

---

## 📄 License

This project is internal-use. Please customize depending on your organization’s policies.

---

## 👨‍💻 Author

Built by Deodie Picson as part of a productivity and efficiency automation initiative. For inquiries or support, please contact deodie.dev@gmail.com.