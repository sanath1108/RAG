import threading
import time
import pyttsx3
import requests

class Speak:
    def __init__(self):
        """Initialize the Speak class."""
        self.tts_engine = pyttsx3.init()  # Text-to-speech engine
        self.listening = False  # Flag to control the listening state
        self.listening_thread = None  # Store the listening thread

    def listen_and_process(self, user_id):
        """Start listening indefinitely in a separate thread."""
        if self.listening:
            print(f"Already listening for user {user_id}...")  # Debugging line
            return  # Prevent starting a new thread if already listening
    
        self.listening = True
        print(f"Started listening for user {user_id}...")
    
        # Create and start the listening thread
        self.listening_thread = threading.Thread(target=self._listen_for_voice, args=(user_id,))
        self.listening_thread.start()


    def _listen_for_voice(self, user_id):
        """Internal method to simulate the listening process."""
        while self.listening:
            # Your listening logic here (e.g., use microphone to listen)
            print("Listening for user's voice...")
            time.sleep(1)  # Simulate listening with a delay

    def stop_listening(self, user_id):
        """Stop the listening process."""
        self.listening = False  # Set the listening flag to False
        if self.listening_thread and self.listening_thread.is_alive():
            print(f"Joining thread for user {user_id}...")  # Debugging line
            self.listening_thread.join()  # Wait for the thread to finish
        print(f"Stopped listening for user {user_id}")

    def get_llm_response(self, input_text, context=""):
        """
        Send the extracted text to the LLM and return its response.

        Args:
            input_text (str): The extracted text to be processed by the LLM.

        Returns:
            str: The LLM's response.
        """
        print("Sending text to the LLM...")

        # Example with Mistral model (replace with your actual implementation)
        # This should interact with the Mistral API running locally via Ollama
        response = requests.post(
            'http://localhost:11434/api/v1/ask',
            json={"model": "mistral", "context": context, "input": input_text}
        )

        if response.status_code == 200:
            return response.json().get('response', 'No response from LLM.')
        else:
            raise RuntimeError("Failed to get response from Mistral.")

    def speak_response(self, response_text):
        """
        Convert the LLM's response to speech and speak it aloud.

        Args:
            response_text (str): The text to convert to speech.
        """
        print(f"Speaking response: {response_text}")
        self.tts_engine.say(response_text)
        self.tts_engine.runAndWait()
