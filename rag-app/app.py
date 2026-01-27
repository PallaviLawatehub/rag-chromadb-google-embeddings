import streamlit as st
import os
from document_loader import extract_text_from_files, chunk_text
from embeddings import get_embeddings, generate_response
from chroma_client import get_chroma_client, get_or_create_collection, store_chunks_and_embeddings

# Set up the Streamlit app
st.title('RAG Document Search App')

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
                client = get_chroma_client()
                collection = get_or_create_collection(client)
                store_chunks_and_embeddings(collection, chunks, embeddings)
                st.success('Documents processed and stored successfully!')
                st.session_state['collection'] = collection
                st.session_state['chunks'] = chunks  # Store chunks for reference
            except Exception as e:
                st.error(f'Error storing documents: {e}')

# Query section
st.header('Ask Questions')

# Text input for user questions
query = st.text_input('Enter your question:')

if query and st.button('Search'):
    if 'collection' not in st.session_state:
        st.error('Please process documents first.')
    else:
        with st.spinner('Searching and generating response...'):
            try:
                # Generate embedding for query
                query_embedding = get_embeddings([query])[0]
                
                # Search ChromaDB for top 3 similar chunks
                results = st.session_state['collection'].query(
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
