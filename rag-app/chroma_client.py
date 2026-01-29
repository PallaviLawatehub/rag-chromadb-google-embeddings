import os
from dotenv import load_dotenv
# Load environment variables
#load_dotenv()
load_dotenv()
import chromadb
from chromadb.config import Settings
import uuid
from datetime import datetime


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
    #host = chroma_url.replace("https://", "").replace("http://", "")

    #client = chromadb.HttpClient(
     ##  host="api.trychroma.com",
       # api_key=chroma_api_key,
        #tenant=chroma_tenant,
        #database=chroma_database
        #port=443,
        #ssl=True,
        #headers={
         #   "Authorization": f"Bearer {chroma_api_key}",
          #  "tenant": chroma_tenant,
           # "database": chroma_database
        #}
    #)
    client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE"),
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
        # Try to get existing collection
        collection = client.get_collection(name=collection_name)
        return collection
    except Exception as e:
        # If collection doesn't exist, create it
        try:
            collection = client.create_collection(name=collection_name)
            return collection
        except Exception as create_error:
            # If creation fails, try deleting and recreating
            try:
                client.delete_collection(name=collection_name)
            except:
                pass
            collection = client.create_collection(name=collection_name)
            return collection

def store_chunks_and_embeddings(collection, text_chunks, embeddings, file_name=""):
    """
    Store text chunks and their embeddings in the ChromaDB collection.

    Args:
        collection (chromadb.Collection): The ChromaDB collection.
        text_chunks (list): List of text chunks.
        embeddings (list): List of embedding vectors corresponding to the chunks.
        file_name (str): Optional file name for metadata.
    """
    if len(text_chunks) != len(embeddings):
        raise ValueError("Number of text chunks must match number of embeddings")

    # Validate embedding dimensions are consistent
    if embeddings:
        first_dim = len(embeddings[0])
        for i, emb in enumerate(embeddings):
            if len(emb) != first_dim:
                raise ValueError(f"Inconsistent embedding dimensions: embedding {i} has {len(emb)} dimensions, expected {first_dim}")
    
    # Generate unique IDs for the chunks using UUID
    timestamp = datetime.now().isoformat()
    ids = [f"{file_name}_{i}_{uuid.uuid4().hex[:8]}" if file_name else f"chunk_{i}_{uuid.uuid4().hex[:8]}" 
           for i in range(len(text_chunks))]
    
    # Metadata for each chunk
    metadatas = [
        {
            "file_name": file_name,
            "chunk_index": i,
            "timestamp": timestamp
        }
        for i in range(len(text_chunks))
    ]

    # Add to collection
    collection.add(
        documents=text_chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    
    print(f"Stored {len(text_chunks)} chunks in collection")

def reset_collection(client, collection_name="rag_documents"):
    """
    Delete and recreate a collection (useful for resolving dimension mismatches).

    Args:
        client (chromadb.Client): ChromaDB client instance.
        collection_name (str): Name of the collection to reset.
    """
    try:
        client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' deleted successfully")
    except Exception as e:
        print(f"Could not delete collection: {e}")
    
    # Recreate the collection
    collection = client.create_collection(name=collection_name)
    print(f"Collection '{collection_name}' recreated successfully")
    return collection