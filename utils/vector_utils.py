from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import os

def get_vector_db():
    # Example: Load or create a Chroma vector DB for semantic retrieval
    persist_dir = "vector_db"
    embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding)
    return vectordb
