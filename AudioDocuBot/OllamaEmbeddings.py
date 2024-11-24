# OllamaEmbeddings.py
from langchain.embeddings.base import Embeddings

class OllamaEmbeddings(Embeddings):
    def __init__(self, embedding):
        self.embedding = embedding  # The embedding vector returned by Ollama

    def embed_documents(self, texts):
        # Return the same embedding for each text (assuming same embedding for all texts)
        return [self.embedding for _ in texts]

    def embed_query(self, query):
        # Return the embedding for a single query (same logic as above)
        return self.embedding
