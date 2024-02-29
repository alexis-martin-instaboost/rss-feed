from dotenv import load_dotenv
import os
from helpers.logger_setup import setup_logger
import requests  # Use requests instead of aiohttp
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = setup_logger()


class GPTManager:
    _instance = None

    def __new__(cls):
        # Singleton pattern: create a single instance of GPTManager
        if not cls._instance:
            cls._instance = super(GPTManager, cls).__new__(cls)
        return cls._instance

    def rewrite_article(self, raw_article):
        prompt = f"Rewrite this article"

        api_key = os.getenv("OPENAI_API_KEY")
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-3.5-turbo-1106",
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": raw_article},
                    ],
                },
            )

            response_data = response.json()
            if "choices" in response_data and response_data["choices"]:
                extracted_text = response_data["choices"][0]["message"][
                    "content"
                ].strip()
                return extracted_text
            else:
                return None
        except Exception as e:
            # Log the error or handle it as per your application's requirements
            logger.error(f"Error during OpenAI API call: {e}")
            return None


if __name__ == "__main__":
    # Specify the file path
    file_path = "output.html"

    # Open and read the content of the file
    with open(file_path, 'r') as file:
        html_content = file.read()

    # Pass the content to the function
    gpt_manager = GPTManager()
    result = gpt_manager.extract_article(html_content)
    print(result)
