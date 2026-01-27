import google.genai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_embeddings(text_chunks):
    """
    Generate embeddings for text chunks using Google Generative AI text-embedding-004.

    Args:
        text_chunks (list): List of text strings to embed.

    Returns:
        list: List of embedding vectors (lists of floats).
    """
    if not text_chunks:
        return []

    embeddings = []
    for chunk in text_chunks:
        try:
            response = client.models.embed_content(
                model="text-embedding-004",
                contents=[chunk]
            )
            embeddings.append(response.embeddings[0].values)
        except Exception as e:
            print(f"Error generating embedding for chunk: {e}")
            # Return zero vector or skip
            embeddings.append([0.0] * 768)  # Assuming 768 dimensions for text-embedding-004

    return embeddings

def generate_response(query, context):
    """
    Generate a response using Google Generative AI based on the query and context.

    Args:
        query (str): The user's question.
        context (str): The retrieved context chunks combined.

    Returns:
        str: The generated response.
    """
    try:
        prompt = f"""Based on the following context, answer the question. If the context doesn't contain enough information to answer the question, say so.

Context:
{context}

Question: {query}

Answer:"""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"