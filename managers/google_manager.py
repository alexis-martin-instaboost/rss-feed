import requests
from helpers.logger_setup import setup_logger

logger = setup_logger()

class GoogleManager:
    def __init__(self):
        # You might need to handle authentication and set other configurations here
        # For simplicity, we're not including authentication details in this example
        pass

    def _make_request(self, calling_function, method, google_key, url, data=None):
        headers = {
            "Authorization": f"Bearer {google_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(method, url, json=data, headers=headers)
            logger.info(response, response.json())
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Request successful: {method} {url}")
                return response_data
            else:
                logger.error(
                    f"Failed to process request called by: {calling_function}. Method: {method}. URL: {url}. Data: {data}"
                )
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {e}")
            return None
        
    def update_document(self, title, google_key, document_id, content_updates):
        # URL for updating a Google document
        update_document_url = f"https://docs.googleapis.com/v1/documents/{document_id}:batchUpdate"
        breaker = "-------------------------------------------------------------------------------------\n\n"

        # Request body for batch update
        batch_update_body = {
            "requests": [

                {
                    "insertText": {
                        "location": {
                            "index": 1,  # Modify the index based on your requirements
                        },
                        "text": content_updates,
                    }
                },
                {
                    "insertText": {
                        "location": {
                            "index": len(content_updates) + 1,  # Modify the index based on your requirements
                        },
                        "text": breaker,  # Insert the title at the specified index
                    }
                },
            ]
        }

        # Make a POST request to update the document using _make_request method
        response_data = self._make_request(
            "update_document", "POST", google_key, update_document_url, batch_update_body
        )

        if response_data:
            logger.info(f"Document updated successfully. Document ID: {document_id}")
        else:
            logger.error(f"Failed to update document with ID: {document_id}")

    def create_document(self, google_key, title):
        # URL for creating a new Google document
        create_document_url = "https://docs.googleapis.com/v1/documents"

        # Request body
        body = {
            "title": title,
        }

        # Make a POST request to create a new document using _make_request method
        response_data = self._make_request(
            "create_document", "POST", google_key, create_document_url, body
        )

        if response_data:
            document_id = response_data.get("documentId")
            if document_id:
                logger.info(f"Document created successfully. Document ID: {document_id}")
                return document_id
            else:
                logger.error("Failed to get document ID from the response.")

        return None
