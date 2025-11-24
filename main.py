import os
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import UnstructuredURLLoader

load_dotenv()

# ------------------------
# Load keys
# ------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_INFERENCE_API_KEY")
if not GROQ_API_KEY or not HF_API_KEY:
    raise ValueError("Please add GROQ_API_KEY and HF_INFERENCE_API_KEY in .env")

# ------------------------
# Initialize
# ------------------------
app = FastAPI(title="RAG API with Ranking")
vector_store = None

embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = ChatGroq(model_name="qwen/qwen3-32b", groq_api_key=GROQ_API_KEY)

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="Use the context below to answer the question concisely.\n\nContext:\n{context}\n\nQuestion:\n{question}"
)
chain = LLMChain(llm=llm, prompt=prompt)

# ------------------------
# Helper
# ------------------------
def chunk_text(text, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

def add_to_vector_store(chunks):
    global vector_store
    if vector_store is None:
        # First time creation
        vector_store = Chroma.from_texts(chunks, embedding=embedder, persist_directory="chroma_db")
    else:
        # Add new chunks to existing store
        vector_store.add_texts(chunks)
    vector_store.persist()

# ------------------------
# Upload PDF
# ------------------------
@app.post("/upload-files/")
async def upload_files(files: List[UploadFile]):
    all_texts = []

    for file in files:
        path = f"temp_{file.filename}"
        with open(path, "wb") as f:
            f.write(await file.read())

        if file.filename.endswith(".pdf"):
            reader = PdfReader(path)
            text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            all_texts.append(text)
        else:
            raise HTTPException(status_code=400, detail="Only PDF files supported.")

    chunks = []
    for text in all_texts:
        chunks.extend(chunk_text(text))

    add_to_vector_store(chunks)
    return {"num_chunks": len(chunks), "message": "PDF processed and stored."}

# ------------------------
# Process URLs
# ------------------------
class URLInput(BaseModel):
    urls: List[str]

@app.post("/process-urls/")
async def process_urls(url_input: URLInput):
    loader = UnstructuredURLLoader(urls=url_input.urls)
    docs = loader.load()
    texts = [doc.page_content for doc in docs]

    chunks = []
    for text in texts:
        chunks.extend(chunk_text(text))

    add_to_vector_store(chunks)
    return {"num_chunks": len(chunks), "message": "URLs processed and stored."}

# ------------------------
# Query endpoint
# ------------------------
class QueryRequest(BaseModel):
    query: str
    rank_type: str = "adaptive"

@app.post("/generate-response/")
async def generate_response(req: QueryRequest):
    global vector_store
    if vector_store is None:
        raise HTTPException(status_code=400, detail="Please upload PDFs or URLs first.")

    # Choose retrieval type
    if req.rank_type.lower() == "adaptive":
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    elif req.rank_type.lower() == "corrective":
        retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 5, "lambda_mult": 0.5})
    else:
        raise HTTPException(status_code=400, detail="Invalid rank_type. Use 'adaptive' or 'corrective'.")

    try:
        docs = retriever.get_relevant_documents(req.query)
        if not docs:
            return {"answer": "No relevant context found."}

        context = "\n".join([doc.page_content for doc in docs])
        response = chain.run({"context": context, "question": req.query})

        return {
            "rank_type": req.rank_type,
            "answer": response.strip(),
            "sources": [doc.metadata.get("source", "N/A") for doc in docs]
        }

    except Exception as e:
        print("Error in generate-response:", e)
        raise HTTPException(status_code=500, detail=str(e))
