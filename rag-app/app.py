import streamlit as st
import os
from document_loader import extract_text_from_files, chunk_text
from embeddings import get_embeddings, generate_response
from chroma_client import get_chroma_client, get_or_create_collection, store_chunks_and_embeddings, reset_collection

# Configure page
st.set_page_config(
    page_title="RAG Document Search",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        /* Main styling */
        .main {
            padding: 2rem;
        }
        
        /* Header styling */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header-container h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .header-container p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* Section styling */
        .section-container {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 1rem;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            width: 100%;
        }
        
        .stButton > button:hover {
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
        }
        
        /* File uploader styling */
        .stFileUploader {
            border: 2px dashed #667eea;
            border-radius: 12px;
            padding: 1rem;
        }
        
        /* Info boxes */
        .info-box {
            background: #f0f7ff;
            border-left: 4px solid #667eea;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        /* Stats display */
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        /* Results styling */
        .result-container {
            background: #f9f9f9;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin-top: 1rem;
        }
        
        .result-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 1rem;
        }
        
        .result-text {
            line-height: 1.6;
            color: #555;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize client
@st.cache_resource
def load_chroma_client():
    return get_chroma_client()

client = load_chroma_client()

# Header
st.markdown("""
    <div class="header-container">
        <h1>📚 RAG Document Search Engine</h1>
        <p>Upload documents and search across them using AI-powered semantic search</p>
    </div>
""", unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📤 Upload Documents</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        'Select files (PDF, TXT, DOCX)',
        type=['pdf', 'txt', 'docx'],
        accept_multiple_files=True,
        help="Upload one or multiple documents to search across"
    )
    
    if uploaded_files:
        st.markdown(f'<div class="info-box"><strong>Selected Files:</strong> {len(uploaded_files)} file(s)</div>', unsafe_allow_html=True)
        for uploaded_file in uploaded_files:
            st.caption(f"✓ {uploaded_file.name}")
        
        if st.button('🚀 Process Documents', key='process'):
            with st.spinner('⏳ Processing documents...'):
                # Extract text
                combined_text = extract_text_from_files(uploaded_files)
                st.success(f"✓ Extracted {len(combined_text):,} characters")
                
                # Chunk text
                chunks = chunk_text(combined_text)
                st.success(f"✓ Created {len(chunks)} text chunks")
                
                # Generate embeddings
                with st.spinner('🔄 Generating embeddings...'):
                    embeddings = get_embeddings(chunks)
                st.success(f"✓ Generated {len(embeddings)} embeddings")
                
                # Store in ChromaDB
                try:
                    collection = get_or_create_collection(client)
                    file_names = ", ".join([f.name for f in uploaded_files])
                    store_chunks_and_embeddings(collection, chunks, embeddings, file_names)
                    
                    import time
                    time.sleep(1)
                    
                    collection_count = collection.count()
                    st.success(f'✅ Documents stored successfully! Total documents: {collection_count}')
                    st.balloons()
                    
                except Exception as e:
                    error_msg = str(e)
                    if "dimension" in error_msg.lower():
                        st.warning(f'⚠️ Resetting collection...')
                        try:
                            reset_collection(client)
                            collection = get_or_create_collection(client)
                            file_names = ", ".join([f.name for f in uploaded_files])
                            store_chunks_and_embeddings(collection, chunks, embeddings, file_names)
                            
                            import time
                            time.sleep(1)
                            
                            collection_count = collection.count()
                            st.success(f'✅ Documents stored after reset! Total: {collection_count}')
                        except Exception as retry_error:
                            st.error(f'❌ Error: {retry_error}')
                    else:
                        st.error(f'❌ Error: {e}')
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Database Status</div>', unsafe_allow_html=True)
    
    try:
        collection = get_or_create_collection(client)
        doc_count = collection.count()
        
        # Display stats
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Documents</div>
                    <div class="stat-value">{doc_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">Status</div>
                    <div class="stat-value">{'✓' if doc_count > 0 else '○'}</div>
                </div>
            """, unsafe_allow_html=True)
        
        if doc_count > 0:
            st.markdown('<div class="info-box">✓ Database is ready for search</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">ℹ️ Upload documents to get started</div>', unsafe_allow_html=True)
        
        # Clear database button
        if st.button('🗑️ Clear Database', key='clear_db', help="Delete all documents from the database"):
            try:
                reset_collection(client)
                st.success("✅ Database cleared successfully")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error clearing database: {e}")
    
    except Exception as e:
        st.warning(f'⚠️ Could not check database: {e}')
    
    st.markdown('</div>', unsafe_allow_html=True)

# Search section
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 Search & Ask Questions</div>', unsafe_allow_html=True)

col_search1, col_search2 = st.columns([4, 1])

with col_search1:
    query = st.text_input(
        'Enter your question:',
        placeholder='What would you like to know about your documents?',
        help='Ask any question related to your uploaded documents'
    )

with col_search2:
    search_button = st.button('🔎 Search', key='search', use_container_width=True)

if search_button and query:
    with st.spinner('⏳ Searching and generating response...'):
        try:
            collection = get_or_create_collection(client)
            
            if collection.count() == 0:
                st.error('❌ No documents in database. Please upload documents first.')
            else:
                # Generate embedding for query
                query_embedding = get_embeddings([query])[0]
                
                # Search ChromaDB for more results to get better context
                num_results = min(10, collection.count())  # Get up to 10 results or all available
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=num_results
                )
                
                # Combine retrieved chunks with better formatting
                context = "\n\n---\n\n".join(results['documents'][0])
                
                # Show how many results were retrieved
                st.info(f"📚 Retrieved {len(results['documents'][0])} relevant document sections")
                
                # Generate response with better prompt
                answer = generate_response(query, context)
                
                # Display results
                st.markdown("""
                    <div class="result-container">
                        <div class="result-title">💡 Answer</div>
                        <div class="result-text">
                """, unsafe_allow_html=True)
                
                st.markdown(answer)
                
                st.markdown("""
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show sources with relevance
                with st.expander(f"📖 View Source Documents ({len(results['documents'][0])} matches)"):
                    for i, doc in enumerate(results['documents'][0], 1):
                        st.markdown(f"**Source {i}:**")
                        st.text_area(f"Content {i}", doc, height=100, disabled=True, key=f"source_{i}")
                        st.divider()
        
        except Exception as e:
            st.error(f'❌ Error: {e}')

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #eee; color: #999;">
        <p>Powered by Google Generative AI • ChromaDB • Streamlit</p>
        <p style="font-size: 0.85rem;">Using Gemini Embedding & Gemini 2.5 Flash Models</p>
    </div>
""", unsafe_allow_html=True)
