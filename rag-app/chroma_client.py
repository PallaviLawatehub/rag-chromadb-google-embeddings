import chromadb
from chromadb.config import Settings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_chroma_client():
    """
    Connect to ChromaDB Cloud using API credentials.

    Returns:
        chromadb.Client: ChromaDB client instance.
    """
    chroma_url = os.getenv("CHROMA_URL")
    chroma_api_key = os.getenv("CHROMA_API_KEY")
    chroma_tenant = os.getenv("CHROMA_TENANT")
    chroma_database = os.getenv("CHROMA_DATABASE")

    if not all([chroma_url, chroma_api_key, chroma_tenant, chroma_database]):
        raise ValueError("CHROMA_URL, CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE must be set in .env")

    # Extract host from URL (remove https://)
    host = chroma_url.replace("https://", "").replace("http://", "")

    client = chromadb.HttpClient(
        host=host,
        port=443,
        ssl=True,
        headers={
            "Authorization": f"Bearer {chroma_api_key}",
            "tenant": chroma_tenant,
            "database": chroma_database
        }
    )
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