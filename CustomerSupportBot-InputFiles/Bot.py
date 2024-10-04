import streamlit as st
from krutrim_cloud import KrutrimCloud
from dotenv import load_dotenv
import os
import PyPDF2
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
logging.debug(f"API_KEY loaded: {API_KEY is not None}")

# Initialize Krutrim client and embedding model
client = KrutrimCloud(api_key=API_KEY)
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
logging.debug("Krutrim client and embedding model initialized.")

# Initialize FAISS index
dimension = 384  # The dimension of the embeddings
faiss_index = faiss.IndexFlatL2(dimension)
logging.debug("FAISS index initialized.")

# Streamlit app configuration
st.set_page_config(
    page_title="DocuBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

def extract_text_from_pdf(uploaded_file):
    """Extract text from the uploaded PDF file."""
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logging.debug(f"Extracted {len(text)} characters from PDF.")
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        logging.error(f"Error extracting text: {e}")
    return text

def get_response(messages):
    """Get a response from the Krutrim Cloud model."""
    logging.debug(f"Sending messages to the model: {messages}")
    try:
        response = client.chat.completions.create(model="Meta-Llama-3-8B-Instruct", messages=messages)
        logging.debug(f"Response received: {response.choices[0].message.content}")
        return response.choices[0].message.content
    except Exception as exc:
        st.error(f"Error getting response: {exc}")
        logging.error(f"Error getting response: {exc}")
        return "Sorry, I couldn't get a response."

def main():
    st.title("DocuBot")
    st.write("I am your friend who can answer your questions based on the documents you provide me.")
    
    # Initialize chat history and FAISS database
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        logging.debug("Initialized chat history.")
    if 'pdf_texts' not in st.session_state:
        st.session_state.pdf_texts = []
        logging.debug("Initialized PDF texts.")
    if 'faiss_index' not in st.session_state:
        st.session_state.faiss_index = faiss.IndexFlatL2(dimension)
        logging.debug("Initialized FAISS index in session state.")

    # File upload section (PDF only)
    uploaded_files = st.file_uploader("Upload a PDF file related to your query", type=["pdf"], accept_multiple_files=True)

    # Handle file processing and updating context
    if uploaded_files:
        for uploaded_file in uploaded_files:
            extracted_text = extract_text_from_pdf(uploaded_file)
            st.write(f"Uploaded file: {uploaded_file.name}")
            st.write(f"Extracted Text Snippet: {extracted_text[:100]}...")  # Show a snippet

            # Create embeddings and add to FAISS index
            if extracted_text:
                sentences = extracted_text.split(".")  # Split into sentences
                embeddings = embedding_model.encode(sentences)
                st.session_state.faiss_index.add(np.array(embeddings, dtype=np.float32))
                st.session_state.pdf_texts.extend(sentences)
                logging.debug(f"Added {len(sentences)} sentences to FAISS index.")

    # User input section
    if prompt := st.text_input("Ask your question here:"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        logging.debug(f"User prompt added to chat history: {prompt}")

        # Convert user question to embedding
        question_embedding = embedding_model.encode([prompt])
        logging.debug(f"Encoded user question to embedding.")

        # Search FAISS index for similar embeddings
        distances, indices = st.session_state.faiss_index.search(np.array(question_embedding, dtype=np.float32), k=3)
        logging.debug(f"FAISS search completed. Distances: {distances}, Indices: {indices}")

        # Retrieve most relevant texts
        retrieved_texts = [st.session_state.pdf_texts[idx] for idx in indices[0]]
        logging.debug(f"Retrieved texts: {retrieved_texts}")

        # Prepare messages for the model
        messages = [{"role": "system", "content": "You are a helpful customer support assistant."}]
        messages.extend(st.session_state.chat_history)
        
        if retrieved_texts:  # Ensure we have context to add
            context_message = " ".join(retrieved_texts)
            messages.append({"role": "assistant", "content": context_message})  # Add context
            logging.debug(f"Messages prepared for model: {messages}")

        # Get the response from the model
        bot_response = get_response(messages)

        # Add assistant message to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

    # Display chat history
    for chat in st.session_state.chat_history:
        avatar = "🤖" if chat["role"] == "assistant" else "😎"
        st.markdown(f"**{avatar}{chat['role'].capitalize()}**: {chat['content']}")
        if chat["role"]=="assistant":
            st.markdown("---")

if __name__ == "__main__":
    main()
