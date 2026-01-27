import chromadb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_chroma_client():
    """
    Connect to local ChromaDB instance.

    Returns:
        chromadb.Client: ChromaDB client instance.
    """
    # Use local persistent client
    client = chromadb.PersistentClient(path="./chroma_db")
    return client

def get_or_create_collection(client, collection_name="rag_documents"):
    """
    Get or create a ChromaDB collection.

    Args:
        client (chromadb.Client): ChromaDB client instance.
        collection_name (str): Name of the collection.

    Returns:
        chromadb.Collection: The collection instance.
    """
    try:
        collection = client.get_collection(name=collection_name)
    except:
        collection = client.create_collection(name=collection_name)
    return collection

def store_chunks_and_embeddings(collection, text_chunks, embeddings):
    """
    Store text chunks and their embeddings in the ChromaDB collection.

    Args:
        collection (chromadb.Collection): The ChromaDB collection.
        text_chunks (list): List of text chunks.
        embeddings (list): List of embedding vectors corresponding to the chunks.
    """
    if len(text_chunks) != len(embeddings):
        raise ValueError("Number of text chunks must match number of embeddings")

    # Generate IDs for the chunks
    ids = [f"chunk_{i}" for i in range(len(text_chunks))]

    # Add to collection
    collection.add(
        documents=text_chunks,
        embeddings=embeddings,
        ids=ids
    )