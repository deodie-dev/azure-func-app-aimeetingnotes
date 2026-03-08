# AI Meeting Notes Automation

This project automates the extraction, summarization, and documentation of Microsoft Teams client advisory calls. Built using Azure services, Microsoft Graph API, and OpenAI, the solution captures Outlook meeting metadata, retrieves Teams transcripts, summarizes them using GPT-4, stores data in Azure SQL, and updates CRM (ClickUp) all on a scheduled basis.



## Tech Stack

- **Microsoft Graph API** – Fetches Outlook calendar and Teams transcript data.
- **Azure Function App** – Automates daily script execution.
- **Azure OpenAI (GPT-4)** – Summarizes meeting transcripts.
- **Azure SQL Database** – Stores meeting and summary data.
- **ClickUp API** – Updates CRM with summarized notes.
- **Python** – Primary programming language for all logic.

## Architecture
![Architecture](https://github.com/deodie-dev/azure-func-app-aimeetingnotes/blob/main/images/Architecture.png)

## List view of MS Teams Meetings in ClickUp
![ClickUp](https://github.com/deodie-dev/azure-func-app-aimeetingnotes/blob/main/images/ClickUp.png)

## AI Output in its respective ClickUp task 
![Output](https://github.com/deodie-dev/azure-func-app-aimeetingnotes/blob/main/images/Output.png)

## Project Structure

```plaintext
.
├── function_app.py                  # Main Azure Function entry point
├── host.json                        # Azure Function configuration
├── local.settings.json              # Local environment settings
├── requirements.txt                 # Python dependencies
├── src/
│   ├── clients/
│   │   ├── graph_client.py          # Microsoft Graph API client
│   │   ├── clickup_client.py        # ClickUp API client
│   │   └── openai_client.py         # Azure OpenAI (GPT-4) client
│   ├── core/
│   │   ├── config.py                # Configuration management
│   │   ├── logger.py                # Logger setup utility
│   │   ├── clickup_ids.py           # ClickUp folder/user IDs
│   │   └── folder_ids.json          # JSON data for folder mappings
│   ├── database/
│   │   └── azure_sql.py             # Azure SQL Database client
│   ├── models/
│   │   └── event.py                 # Event data model
│   ├── services/
│   │   └── meeting_service.py       # Core business logic orchestrator
│   └── utils/
│       └── meeting_utils.py         # Utility functions (parsing, cleaning)
├── README.md                        # Project documentation
└── images/                          # Architecture diagrams
```

### `function_app.py`
- Main Azure Function entry point
- Configures timer trigger (every 15 minutes during business hours)
- Delegates to `MeetingService` for orchestration

### `src/services/meeting_service.py`
- Orchestrates the complete pipeline:
  - Fetches Outlook calendar events
  - Retrieves Teams transcripts
  - Summarizes using GPT-4
  - Updates Azure SQL and ClickUp

### `src/clients/graph_client.py`
- Microsoft Graph API authentication and calls:
  - Fetch Outlook calendar events
  - Retrieve Teams meeting transcripts
  - Parse and clean VTT transcript format

### `src/clients/clickup_client.py`
- ClickUp API integration:
  - Create or update tasks
  - Attach meeting summaries and metadata

### `src/clients/openai_client.py`
- Azure OpenAI (GPT-4) integration:
  - Summarize meeting transcripts
  - Return structured summaries

### `src/database/azure_sql.py`
- Azure SQL Server client:
  - Insert/update meeting records in `tblOutlookEventsY`
  - Query existing meetings

### `src/core/config.py`
- Configuration management for API keys and database settings

### `src/core/logger.py`
- Centralized logging setup for tracking workflow and errors

### `src/models/event.py`
- Data model for meeting/event objects

### `src/utils/meeting_utils.py`
- Helper utilities for data parsing, formatting, and text cleaning



## Workflow Overview

1. **Trigger**  
   Azure Function App timer trigger invokes `function_app.py` on a schedule (every 15 minutes during business hours: 10 PM - 8 AM SGT, weekdays only).

2. **Service Orchestration**  
   `MeetingService.main()` initializes all clients (GraphClient, ClickUpClient, OpenAIClient, AzureSQLClient) and orchestrates the pipeline.

3. **Fetch Calendar Events**  
   `GraphClient.get_outlook_metadata()` retrieves Outlook meeting metadata for the past 24 hours to upcoming 24 hours.

4. **Process Event Metadata**  
   `MeetingUtils` functions parse and format event data, extracting relevant fields and computing meeting duration.

5. **Get Meeting Transcript**  
   `GraphClient.get_transcript_content_url()` fetches the Teams transcript URL.
   `GraphClient.get_filtered_vtt()` retrieves and cleans the transcript (converts VTT to plain text).

6. **Summarize Using OpenAI GPT-4**  
   `OpenAIClient.summarize_transcript()` sends cleaned transcript to Azure OpenAI and returns a structured summary.

7. **Update Azure SQL Database**  
   `AzureSQLClient.insert_record()` or `update_record()` stores meeting metadata and summaries in `tblOutlookEventsY`.

8. **Update CRM (ClickUp)**  
   `ClickUpClient.update_task()` pushes the summary to the relevant ClickUp task for CRM integration.



## Key Features

- **Modular Architecture**  
  Organized into distinct layers: clients (external APIs), services (business logic), database (data persistence), utils (helpers), and models (data structures).

- **Scalable Design**  
  Each client (Graph, ClickUp, OpenAI, SQL) is independently instantiable and testable.

- **Centralized Logger**  
  All operations logged through `core/logger.py` for consistent debugging and monitoring.

- **Resilient Error Handling**  
  Try-catch blocks and logging at each pipeline stage ensure graceful failure and troubleshooting.

- **Transcript Matching**  
  Precise meeting ID correlation between Outlook and Teams for accurate transcript retrieval.

- **Extensible Configuration**  
  Environment variables managed in `core/config.py` for easy deployment across environments.

- **CRM Integration**  
  Automated task creation and updates in ClickUp for seamless workflow automation.



## Recent Refactoring & Architecture Improvements

The codebase has been refactored for improved maintainability, testability, and scalability:

- **Modular Client Layer**: API interactions (Microsoft Graph, ClickUp, OpenAI, SQL) now live in separate, independently testable client classes.
- **Service-Oriented Architecture**: Business logic centralized in `MeetingService`, making the main trigger function clean and lightweight.
- **Configuration Management**: Centralized in `src/core/config.py` for consistent settings across modules.
- **Better Code Organization**: Separated concerns into `clients/`, `services/`, `database/`, `models/`, and `utils/` directories.
- **Enhanced Logging**: Unified logging setup in `src/core/logger.py` replaces scattered logging utilities.
- **Data Models**: Introduced `Event` model in `src/models/` for type safety and clarity.


## Deployment

All Python files are deployed inside an **Azure Function App**, which runs automatically on a timer trigger. Environment variables (e.g., client credentials, SQL settings) are stored securely in the Azure Function configuration settings.



## Environment Variables (for local testing)

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



## Requirements

```bash
pip install -r requirements.txt
```

> Make sure to include `pyodbc`, `requests` and `pytz`


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


## Testing Locally

You can test the main script by running:

```bash
python function_app.py
```

Ensure your environment variables are loaded or defined before running.



## Potential Extensions

**Scalable Diagnostic Intelligence**  - As it is designed with scalability in mind, we can generate diagnostics based on previous meeting summaries. The system can be enhanced to automatically assess whether a client advisory session requires further action or indicates resolution/no action needed.
**Sentiment & Intent Analysis**  - Layer in sentiment analysis and intent classification using Azure Cognitive Services to flag urgent or sensitive client conversations.
**CRM Integration Flexibility**  - Expand support for additional CRMs beyond ClickUp via modular API adapters.
**Smart Filtering & Alerts**  - Auto-prioritize meetings for follow-up based on keyword triggers or customer profile metadata.
**Smart Filtering & Alerts**  - Auto-prioritize meetings for follow-up based on keyword triggers or customer profile metadata.
**UI Dashboard (Ongoing Enhancement)** - Create a frontend dashboard for manual review, editing, and audit trail of summaries and automation status.



## License

This project is internal-use. Please customize depending on your organization’s policies.



## Author

Built by Deodie Picson as part of a productivity and efficiency automation initiative. For inquiries or support, please contact deodie.dev@gmail.com.
