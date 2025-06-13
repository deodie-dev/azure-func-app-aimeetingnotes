import requests
import json
from utils import log_and_print_err, log_and_print

import os
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_URL = os.environ["OPENAI_URL"]

def summarize_func(transcript):

    headers = {
        "Content-Type": "application/json",
        "api-key": OPENAI_API_KEY
    }

    # promt = """
    # You are the business advisor that specializes in business and sales. Given the transcript from the recent client call, perform the following tasks:
    # Key discussion points: Extract and bullet point the key insights or takeaways.
    # Decisions made: Any final decisions or conclusion reached during the meeting.
    # Action Items: A list of specific task or follwo ups that were assigned to team members, including deadlines or responsible individuals.
    # Summarize the transcript after listing the key points.
    # Conduct a thorough sentiment analysis of the overall conversation.

    # Do not place the summary at the beginning. Make sure to be detailed as much as possible. Avoid special characters except for bullet points.
    # """


    promt = """
    You are a business advisor specializing in business strategy and sales. Based on the transcript of a recent client call, perform the following tasks:
    Key Discussion Points: Extract and bullet point the key insights or takeaways from the conversation.
    Decisions Made: Identify any final decisions or conclusions reached during the meeting.
    Action Items: List specific tasks or follow-ups assigned to team members, including deadlines or individuals responsible.
    Summary: Summarize the transcript after listing the key points.
    Sentiment Analysis: Conduct a thorough sentiment analysis of the overall conversation.

    Guidelines:
    Do not place the summary at the beginning.
    Provide as much detail as possible for each section.

    Use this format:

    KEY DISCUSSION POINTS:
    • [value]
    • [value]

    DECISIONS MADE:
    • [value]
    • [value]

    ACTION ITEMS:
    • [value]
    • [value]

    SUMMARY:
    [value]

    SENTIMENT ANALYSIS:
    [value]

    """

    data = {
        "messages": [
            {"role": "system", "content": f"{promt}"},
            {"role": "user", "content": f"{transcript}"}
        ],
    }

    response = requests.post(OPENAI_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        result = response.json()
        summary = result['choices'][0]['message']['content']
        log_and_print("OpenAI successfully processed the summary.")
        # log_and_print(summary)
        return summary
    else:
        log_and_print_err(f"OpenAI request failed: {response.status_code}")
        log_and_print_err(response.text)
        return None