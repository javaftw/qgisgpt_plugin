import requests
import json
import threading
from PyQt5.QtCore import QObject, pyqtSignal

class QGISGPT(QObject):
    responseReceived = pyqtSignal(str)

    def __init__(self):
        super().__init__() 
        #self.model = "gpt-3.5-turbo-16k"
        #self.model="gpt-4"
        #self.model="gpt-4-32k-0613"
        self.model="gpt-4-1106-preview" 
        self.conversation_history = []
        self.conversation_history.append({"role": "system", "content": self.constructSystemMessage()})
        self.api_key = None
        self.project_snapshot = ""

    def set_api_key(self, api_key):
        self.api_key = api_key

    def set_project_snapshot(self, project_snapshot):
        self.project_snapshot = json.dumps(project_snapshot, indent=4)

    def sanitize_response(self, response):
        cleaned_response = response.replace("``` python", "").replace("python\n", "").replace("```", "").strip()
        return cleaned_response
    
    def send_message(self, message, project_snapshot=""):
        # Append the user's message to the conversation history
        # Ensure thread safety while modifying shared data
        with threading.Lock():
            self.conversation_history.append({"role": "user", "content": message})

        # Create a thread for the API call
        thread = threading.Thread(target=self._send_message_thread)
        thread.start()

    def _send_message_thread(self):
        # Prepare the API request payload
        payload = {
            "model": self.model,
            "messages": self.conversation_history
        }
        
        # Make the API call
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            
            # Check for errors
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")

            assistant_message = self._process_response(response)
            
            # Emit the signal and invoke the callback after processing the response
            self.responseReceived.emit(assistant_message)

        except Exception as e:
            error_message = f"Error during API call: {e}"
            self.responseReceived.emit(error_message)


    def _process_response(self, response):
        # Process the response (similar to the existing code)
        response_data = response.json()
        assistant_message = response_data['choices'][0]['message']['content']
        #assistant_message = self.sanitize_response(assistant_message)
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        return assistant_message
    
    def constructSystemMessage(self):
        system_message = (
            ""
        )
        return system_message
