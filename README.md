# RAG Document Search Application

A Retrieval-Augmented Generation (RAG) application built with Streamlit, ChromaDB, and Google Gemini that enables intelligent document search and question-answering.

## 🎯 Core Features Implemented

### 1. Document Upload Interface ✅

- **Drag-and-drop functionality**: Intuitive file upload with drag-and-drop support
- **Format support**: PDF, TXT, and DOCX files
- **File display**: Shows uploaded file names for user confirmation
- **Multiple files**: Support for batch uploading multiple documents

### 2. Vector Storage & Processing ✅

- **Text extraction**: Extracts text from all supported document formats
  - PDF: Via `pypdf` library
  - TXT: Via UTF-8 decoding
  - DOCX: Via `python-docx` library

- **Text chunking**: Splits documents into manageable chunks
  - Chunk size: 500 characters
  - Overlap: 50 characters (context preservation)

- **Embedding generation**: Converts text to vectors
  - Model: `gemini-embedding-001`
  - Dimension: 3072-D vectors
  - Powered by Google Generative AI

- **Vector storage**: Stores in ChromaDB
  - Local persistent storage: `./chroma_data`
  - Automatic collection management
  - Fast similarity search

### 3. Query Interface ✅

- **Text input**: Simple question field
- **Semantic search**: Retrieves top-3 most relevant chunks
- **AI response**: Generates contextual answers via Google Gemini
- **Source attribution**: Displays relevant document chunks
- **Error handling**: Graceful error messages

## 📁 Project Structure

```
rag-app/
├── app.py                    # Main Streamlit UI
├── document_loader.py        # Text extraction & chunking
├── embeddings.py             # Embedding generation
├── chroma_client.py          # Vector database client
├── requirements.txt          # Dependencies
├── .env                      # API keys (git-ignored)
├── .env.example              # Template
└── chroma_data/              # Local vector DB
```

## 🚀 Quick Start

1. **Setup**

   ```bash
   cd rag-app
   pip install -r requirements.txt
   cp .env.example .env
   # Add your Google API key to .env
   ```

2. **Run**

   ```bash
   streamlit run app.py
   ```

3. **Use**
   - Upload documents (PDF/TXT/DOCX)
   - Click "Process Documents"
   - Ask questions in the "Ask Questions" section

## 🔑 Configuration

Create `.env` with:

```
GOOGLE_API_KEY=your_api_key_here
```

Get API key: https://aistudio.google.com/apikey

## 🔐 Security

- API keys stored in `.env` (git-ignored)
- Never commit `.env` file
- See [SECURITY.md](SECURITY.md) for guidelines

## 📦 Dependencies

- streamlit: Web UI
- chromadb: Vector database
- google-genai: Gemini API
- pypdf: PDF processing
- python-docx: DOCX processing
- python-dotenv: Environment variables

## 📝 How It Works

```
Upload Document
     ↓
Extract Text
     ↓
Split into Chunks (500 chars, 50 char overlap)
     ↓
Generate Embeddings (3072-D vectors)
     ↓
Store in ChromaDB
     ↓
User Query → Generate Query Embedding → Search → Retrieve Top 3 Chunks
     ↓
Generate AI Response using Retrieved Context
     ↓
Display Answer + Source Chunks
```

## ✅ All Core Features Complete

- [x] Drag-and-drop file upload (PDF, TXT, DOCX)
- [x] Text extraction from all formats
- [x] Document chunking (500 chars, 50 overlap)
- [x] Embedding generation (gemini-embedding-001)
- [x] Vector storage in ChromaDB
- [x] Semantic search (top-3 retrieval)
- [x] AI response generation
- [x] Source chunk display
- [x] Error handling
- [x] Security best practices
