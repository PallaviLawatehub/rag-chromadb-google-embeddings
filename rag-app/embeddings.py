"""
Embeddings & Response Generation Module

Handles AI interactions using Google Generative AI:

EMBEDDINGS:
- Model: gemini-embedding-001
- Output: 768-dimensional vectors
- Converts text to numerical representation
- Validates dimension consistency across all embeddings

RESPONSE GENERATION:
- Model: gemini-2.5-flash
- Input: User query + retrieved context chunks
- Output: Natural language answer
- Features: Caching, quota handling, retry logic

KEY FEATURES:
- Response caching (saves API quota)
- Exponential backoff for API overload
- Quota limit detection (429 errors)
- Dimension consistency validation
"""

import google.genai as genai
import os
import time
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# Create client for API interaction
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Response cache: MD5(query + context) -> response
response_cache = {}

def get_embeddings(text_chunks):
    """
    Generate embeddings for text chunks using Google Generative AI gemini-embedding-001.

    Args:
        text_chunks (list): List of text strings to embed.

    Returns:
        list: List of embedding vectors (lists of floats).
    """
    if not text_chunks:
        return []

    embeddings = []
    embedding_dimension = None
    
    for i, chunk in enumerate(text_chunks):
        try:
            response = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=[chunk]
            )
            embedding = response.embeddings[0].values
            
            # Store the first embedding dimension as reference
            if embedding_dimension is None:
                embedding_dimension = len(embedding)
            
            embeddings.append(list(embedding))
        except Exception as e:
            print(f"Error generating embedding for chunk {i}: {e}")
            # If we have a reference dimension, use it. Otherwise, skip this chunk
            if embedding_dimension is not None:
                embeddings.append([0.0] * embedding_dimension)
            else:
                # Try one more time with fallback
                embeddings.append([0.0] * 768)
    
    # If we still don't have a dimension, standardize to 768
    if embedding_dimension is None:
        embedding_dimension = 768
        embeddings = [[0.0] * 768 for _ in embeddings]
    
    # Ensure all embeddings have the same dimension
    standardized_embeddings = []
    for emb in embeddings:
        if len(emb) != embedding_dimension:
            # Pad or trim to match the standard dimension
            if len(emb) < embedding_dimension:
                emb = list(emb) + [0.0] * (embedding_dimension - len(emb))
            else:
                emb = emb[:embedding_dimension]
        standardized_embeddings.append(emb)
    
    print(f"Generated {len(standardized_embeddings)} embeddings with dimension {embedding_dimension}")
    return standardized_embeddings

def generate_response(query, context, max_retries=3):
    """
    Generate a response using Google Generative AI based on the query and context.
    Includes retry logic, caching, and quota handling.

    Args:
        query (str): The user's question.
        context (str): The retrieved context chunks combined.
        max_retries (int): Maximum number of retry attempts.

    Returns:
        str: The generated response.
    """
    # Create cache key from query and context
    cache_key = hashlib.md5(f"{query}_{context[:500]}".encode()).hexdigest()
    
    # Check if response is cached
    if cache_key in response_cache:
        print("Using cached response")
        return response_cache[cache_key]
    
    prompt = f"""You are a helpful AI assistant. Based on the following context from documents, provide a comprehensive and detailed answer to the question.

IMPORTANT INSTRUCTIONS:
- Provide a complete and detailed answer based on the context provided
- Include specific details, facts, and information from the context
- If the context doesn't contain information to fully answer the question, say what information is missing
- Format your answer clearly with proper paragraphs and structure
- Be thorough and informative in your response

CONTEXT FROM DOCUMENTS:
{context}

QUESTION: {query}

DETAILED ANSWER:"""

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            result = response.text
            # Cache the successful response
            response_cache[cache_key] = result
            return result
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a quota/rate limit error (429 or 503)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                return """⚠️ **API Quota Limit Reached**

You've exceeded the free tier quota for the Gemini API (20 requests per day).

**Options:**
1. **Wait 24 hours** for the quota to reset
2. **Upgrade your API plan** at https://ai.google.dev
3. **Check your usage** at https://ai.dev/rate-limit

The free tier is limited to 20 generation requests per day. For production use, please consider upgrading to a paid plan for higher limits."""
            
            elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"API overloaded (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "⚠️ The AI service is currently overloaded. Please try again in a moment."
            else:
                return f"❌ Error generating response: {e}"
    
    return "❌ Error generating response: Maximum retries exceeded."