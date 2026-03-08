import requests
import json
import logging
from src.core.logger import setup_logger
from src.core.config import Config

logger = logging.getLogger(__name__)

class OpenAIClient:

    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.api_url = Config.OPENAI_URL

    def summarize_func(self,transcript):

        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

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

        response = requests.post(self.api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content']
            logger.info("OpenAI successfully processed the summary.")
            return summary
        else:
            logger.error(f"OpenAI request failed: {response.status_code}")
            logger.error(response.text)
            return None