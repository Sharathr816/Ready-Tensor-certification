import chromadb
import torch
import os
from datetime import datetime
from dotenv import load_dotenv # to load .env file
from langchain_huggingface import HuggingFaceEmbeddings


device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available() else "cpu"
    )

# embeddings will be used as keys in vector database
embed_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": device},
)

#Chroma only sees strings + dicts, not fancy objects.
client = chromadb.PersistentClient(path="psycheMoney_db") # storing db in local file not on a seperate server or as a separate process
collection = client.get_or_create_collection(# only creates if db dosen't exists
    name="money_publication",
    metadata={"hnsw:space": "cosine", "created": str(datetime.now())} # uses cosine similarity to cal distance(alt: l2(euclidean))
)

# for llm response
load_dotenv()  # loads .env fileX
api_key = os.getenv("GROQ_API_KEY") # fetch api key from .env