import streamlit as st
import os
from document_loader import extract_text_from_files, chunk_text
from embeddings import get_embeddings, generate_response
from chroma_client import get_chroma_client, get_or_create_collection, store_chunks_and_embeddings

# Set up the Streamlit app
st.title('RAG Document Search App')

# Initialize client at the beginning so it's always available
@st.cache_resource
def load_chroma_client():
    return get_chroma_client()

client = load_chroma_client()

# File uploader for PDF, TXT, and DOCX files
uploaded_files = st.file_uploader('Upload files', type=['pdf', 'txt', 'docx'], accept_multiple_files=True)

if uploaded_files:
    st.write('Uploaded files:')
    for uploaded_file in uploaded_files:
        st.write(uploaded_file.name)
    
    # Process button
    if st.button('Process Documents'):
        with st.spinner('Processing documents...'):
            # Extract text
            combined_text = extract_text_from_files(uploaded_files)
            st.write(f"Extracted text length: {len(combined_text)} characters")
            
            # Chunk text
            chunks = chunk_text(combined_text)
            st.write(f"Created {len(chunks)} chunks")
            
            # Generate embeddings
            embeddings = get_embeddings(chunks)
            st.write(f"Generated {len(embeddings)} embeddings")
            
            # Store in ChromaDB
            try:
                collection = get_or_create_collection(client)
                store_chunks_and_embeddings(collection, chunks, embeddings)
                
                # Verify storage
                collection_count = collection.count()
                st.success(f'Documents processed and stored successfully! Total documents in DB: {collection_count}')
                
            except Exception as e:
                st.error(f'Error storing documents: {e}')

# Query section
st.header('Ask Questions')

# Display stored documents info
try:
    collection = get_or_create_collection(client)
    doc_count = collection.count()
    if doc_count > 0:
        st.info(f'📚 Database contains {doc_count} document(s)')
except Exception as e:
    st.warning(f'Could not check database: {e}')

# Text input for user questions
query = st.text_input('Enter your question:')

if query and st.button('Search'):
    with st.spinner('Searching and generating response...'):
        try:
            collection = get_or_create_collection(client)
            
            # Check if collection has documents
            if collection.count() == 0:
                st.error('❌ No documents found in database. Please process documents first.')
            else:
                # Generate embedding for query
                query_embedding = get_embeddings([query])[0]
                
                # Search ChromaDB for top 3 similar chunks
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3
                )
                
                # Combine retrieved chunks for context
                context = "\n\n".join(results['documents'][0])
                
                # Generate response using LLM
                answer = generate_response(query, context)
                
                # Display answer
                st.subheader('Answer:')
                st.write(answer)
                
                # Display source chunks
                st.subheader('Source Chunks:')
                for i, doc in enumerate(results['documents'][0]):
                    with st.expander(f"Source Chunk {i+1}"):
                        st.write(doc)
                    
        except Exception as e:
            st.error(f'Error during search: {e}')
