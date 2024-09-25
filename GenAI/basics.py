import requests

texts = ["Hi, my name is Sanath", "This hot chick is Riru"]
url = "http://localhost:11434/run/nomic-embed-text" 

# Prepare the request payload
data = {
    "inputs": texts
}

# Send the request to the Ollama model
response = requests.post(url, json=data)
embeddings = response.json()

# Print the embeddings
print(embeddings)
for text, embedding in zip(texts, embeddings):
    print(f"Text: {text}\nEmbedding: {embedding}\n")
