🧠 DocuMind AI — RAG-based Document & URL Chat System (FastAPI + Streamlit + Groq + ChromaDB)

DocuMind AI is an intelligent Retrieval-Augmented Generation (RAG) system that allows users to upload PDFs, process URLs, and ask questions based on the extracted content.

The system uses:

✅ FastAPI as backend
✅ Streamlit as frontend UI
✅ ChromaDB for vector storage
✅ HuggingFace Embeddings for encoding
✅ Groq LLM (Qwen3-32B) for generating fast, accurate answers
✅ MMR (Corrective) & Adaptive ranking for better retrieval
✅ Unstructured URL loader to extract text from websites

🚀 Features
📄 Upload and Process PDFs

Upload multiple PDFs at once.
PDF content is extracted, chunked, embedded, and stored in ChromaDB.

🌐 Process URLs

Fetch webpage content directly from URLs and store them for RAG querying.

🧠 Ask Questions

Query your knowledge base using two smart retrieval approaches:

Mode	Behavior
Adaptive Ranking	Retrieves best matches using similarity search
Corrective Ranking (MMR)	Reduces redundancy, improves diversity of retrieved documents
💬 Beautiful Streamlit UI

Drag & drop PDFs

Enter multiple URLs

Chatbox-style Q&A

Chat history

Smart backend connection check

🏗️ Tech Stack

Backend (FastAPI)

FastAPI

PyPDF2

LangChain

Groq API

ChromaDB

HuggingFace Embeddings

RecursiveCharacterTextSplitter

Frontend (Streamlit)

Streamlit UI

REST API communication

Chat history

File uploader

URL processor

📂 Project Structure
.
├── backend/
│   ├── main.py                  # FastAPI backend
│   ├── chroma_db/               # Vector store
│   ├── .env                     # API keys
│
├── frontend/
│   ├── app.py                   # Streamlit interface
│
├── README.md

🔑 Environment Setup

Create a .env file in your /backend folder:

GROQ_API_KEY=your_groq_api_key
HF_INFERENCE_API_KEY=your_huggingface_api_key

▶️ How to Run the Project
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Start FastAPI Backend
cd backend
uvicorn main:app --reload


Backend URL →
http://127.0.0.1:8000

3️⃣ Start Streamlit Frontend
cd frontend
streamlit run app.py


Frontend URL →
http://localhost:8501

🧠 RAG Workflow
PDF/URL → Extract Text → Chunk →
Embed using MiniLM → Store in ChromaDB →
Retrieve (Adaptive/MMR) → Groq LLM → Answer

🧪 Ranking Modes
1. Adaptive (Similarity Search)

Best for normal Q&A

Retrieves top-k chunks based on cosine similarity

2. Corrective (MMR Ranking)

Balances relevance + diversity

Avoids retrieving repeated or redundant chunks.

