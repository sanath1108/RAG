import requests
import streamlit as st
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Streamlit app configuration
st.set_page_config(
    page_title="Personalized Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_response(user_prompt, chat_history):
    """
    Calls the LLM API to get a response for the user's prompt.
    
    :param user_prompt: The user's input prompt.
    :param chat_history: The history of chat messages.
    
    :return: The response from the LLM.
    """
    url = "https://cloud.olakrutrim.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    recent_messages = chat_history[-6:]  # Up to 6 recent messages
    messages.extend(recent_messages)
    messages.append({"role": "user", "content": user_prompt})

    data = {
        "model": "Meta-Llama-3-8B-Instruct",
        "messages": messages,
        "max_tokens": 256,
        "temperature": 0.5,
    }

    # Use a spinner while waiting for the API response
    with st.spinner("Getting response..."):
        
        response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(response.json())
        return response.json()['choices'][0]['message']['content']
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return "Sorry, I couldn't get a response."

def main():
    """
    The main function that runs the application.
    """
    st.title("Personalized Chatbot")

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Message container
    message_container = st.container()

    # Display chat history
    for chat in st.session_state.chat_history:
        avatar = "🤖" if chat["role"] == "assistant" else "😎"
        with message_container.chat_message(chat["role"], avatar=avatar):
            st.markdown(chat["content"])

    # User input
    if prompt := st.chat_input("Ask a question:"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        message_container.chat_message("user", avatar="😎").markdown(prompt)

        # Get the response from the API
        bot_response = get_response(prompt, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

        with message_container.chat_message("assistant", avatar="🤖"):
            st.markdown(bot_response)

if __name__ == "__main__":
    main()
