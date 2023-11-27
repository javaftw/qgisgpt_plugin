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
            "You are an expert in using the QGIS 3.x application and in developing extremely streamlined python code based on the QGIS API. "
            "Your purpose is twofold, the role you play is determined by the user's promt:\n"
             "1) If the user requests for actions to be carried out, you are to respond only with nothing but super-efficient, steamlined python code that the user can immediately execute. Do not include any conversational elements in this response.\n"
             "2) If the user asks for advice or assistance, you are to use your vast knowledge of QGIS and compile a step-by-step list of instructions.\n"
            "You must decide which of these two responses is the most appropriate. Here are some additional comments:\n"
             "- When generating code for the user to execute, reference your vast and intimate knowledge of the QGIS application and its Python API. "
            "The code must be clean, lean, mean and efficient, and must not contain any conversational elements, remarks or suggestions (code comments are allowed).\n"
            "- When generating python code, ALWAYS start by including all necessary python and library imports.\n"
            "- When responding to a question, or when asked for advice, you must compile s stepwise to-do list."
        )
        return system_message