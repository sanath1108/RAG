import os
from fastapi import FastAPI, Form, UploadFile, File, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from Speak import Speak
from DocumentProcessor import DocumentProcessor
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import requests  # For calling Ollama's API
import io
import traceback
from OllamaEmbeddings import OllamaEmbeddings
from pydantic import BaseModel

class ConversationRequest(BaseModel):
    user_id: str

app = FastAPI()

# Enable CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your React frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = DocumentProcessor()
speak_instance = Speak()

VECTOR_STORE_DIR = "./vectorstores"

# Helper function to call Ollama for embeddings
def generate_ollama_embeddings(text):
    """
    Generate embeddings using Ollama's Nomic embed endpoint.
    """
    url = "http://localhost:11434/v1/embeddings"  # Correct URL
    payload = {"model": "nomic-embed-text:latest", "input": text}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        # Extract the embeddings from the response
        data = response.json()
        print(f"Response from Ollama: {data}")  # For debugging purposes
        embedding = data.get("data", [])[0].get("embedding", None)
        
        if embedding is None:
            raise ValueError("No embedding returned from Ollama API.")
        
        ollama_embedding=OllamaEmbeddings(embedding)
        
        return ollama_embedding
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        raise RuntimeError(f"Failed to generate embeddings using Ollama: {e}")
    except ValueError as ve:
        print(ve)
        raise RuntimeError(f"Embedding generation failed: {ve}")


@app.post("/start-conversation")
async def start_conversation(user_id: str = Form(...)):
    """
    Endpoint to start the conversation and start listening.
    """
    print(f"Received user_id: {user_id}")
    try:
        # Start listening indefinitely and process
        speak_instance.listen_and_process(user_id)
        return JSONResponse(content={"message": "Conversation started successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)




@app.post("/end-conversation")
async def end_conversation(request: ConversationRequest):
    """
    Endpoint to end the conversation and stop listening.
    """
    try:
        user_id = request.user_id  # Access the user_id from the request
        # Stop the listening process (e.g., by stopping the thread or breaking the loop)
        speak_instance.stop_listening(user_id)
        return JSONResponse(content={"message": "Conversation ended successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/process-file")
async def process_file(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Endpoint to process a file, embed its content, and save it to the vector store.
    """
    try:
        # Log the user_id and file name
        print(f"Received file from user_id: {user_id}, file: {file.filename}")
        
        # Read file content
        file_content = await file.read()

        # Use the file content in the processor (assuming it's a valid file format)
        extracted_text = processor.extract_text(file)  # Pass raw content, no need for UploadFile

        print(f"Extracted text: {extracted_text[:100]}...")  # Print part of the extracted text for debugging

        # Generate embeddings for the text using Ollama
        ollama_embedding = generate_ollama_embeddings(extracted_text)

        # Create or update the vector store
        user_store_path = os.path.join(VECTOR_STORE_DIR, user_id)
        os.makedirs(user_store_path, exist_ok=True)

        faiss_store = None
        if os.path.exists(os.path.join(user_store_path, "index")):
            faiss_store = FAISS.load_local(user_store_path, ollama_embedding)
        else:
            faiss_store = FAISS.from_texts([extracted_text], ollama_embedding)

        # Save the updated FAISS store
        faiss_store.save_local(user_store_path)
        return JSONResponse(content={"message": "File processed successfully"}, status_code=200)

    except Exception as e:
        print(f"Error in processing file: {e}")
        print("Traceback:", traceback.format_exc())  # Print full traceback for debugging
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
