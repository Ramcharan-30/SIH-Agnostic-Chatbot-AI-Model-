# bot_server.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil, json
import os
import asyncio
from typing import Dict, Any

# Import functions from your fun.py
from fun import load_documents, get_or_create_vector_store, ask_ai, ConversationMemory, create_qa_chain

app = FastAPI(title="Python Bot API")

# Optional: allow all origins (not necessary for server-to-server calls, but harmless)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Global state
vector_store = None
# Cache for user sessions: session_id -> qa_chain
# Note: In a production app, use Redis or a DB. For this prototype, in-memory is fine.
sessions: Dict[str, Any] = {}

def ensure_vector_store():
    global vector_store
    if vector_store is None:
        if any(DATA_DIR.iterdir()):
            docs = load_documents(str(DATA_DIR))
            vector_store = get_or_create_vector_store(docs, persist_directory=str(DATA_DIR / "chroma_db"))
        else:
            vector_store = None
    return vector_store

@app.on_event("startup")
async def startup_event():
    """Preload vector store on startup to avoid latency on the first request."""
    print("Preloading vector store and ML models...")
    # Run in a thread so it doesn't block the async event loop during startup
    await asyncio.to_thread(ensure_vector_store)
    print("Preloading complete.")

def process_ask(question: str, session_id: str):
    vs = ensure_vector_store()
    if vs is None:
        raise HTTPException(status_code=500, detail="No documents indexed. Upload FAQ files via /api/upload-faq first.")

    # Get or create session
    if session_id not in sessions:
        memory = ConversationMemory(max_history=5)
        qa_chain = create_qa_chain(vs, memory)
        sessions[session_id] = qa_chain
    
    qa_chain = sessions[session_id]
    
    # Run the chain
    response = qa_chain({"query": question})

    # Format sources cleanly
    sources = []
    for doc in response.get("source_documents", []):
        src = doc.metadata.get("source") if hasattr(doc, "metadata") else None
        page = doc.metadata.get("page") if hasattr(doc, "metadata") else None
        sources.append({"source": src, "page": page})

    # Prepare output dict
    intent_info = response.get("intent_info", {})
    output = {
        "answer": response.get("result"),
        "intent": intent_info.get("intent") if intent_info else None,
        "confidence": intent_info.get("confidence") if intent_info else None,
        "entities": intent_info.get("entities") if intent_info else {},
        "sources": sources,
    }
    
    return output

@app.post("/api/ask")
async def api_ask(payload: dict):
    """POST body: { "question": "...", "session_id": "...", "userId": "...", "language": "..." }"""
    question = payload.get("question") or payload.get("message")
    session_id = payload.get("session_id", "default_session")
    
    if not question:
        raise HTTPException(status_code=400, detail="question required")

    # Run blocking RAG operation in a separate thread so we don't freeze the FastAPI event loop
    result = await asyncio.to_thread(process_ask, question, session_id)
    return result

@app.post("/api/upload-faq")
async def api_upload_faq(file: UploadFile = File(...), meta: str = Form("{}")):
    """
    Multipart/form-data with 'file' and optional 'meta' JSON string.
    After saving file, rebuild vector store.
    """
    target = DATA_DIR / file.filename
    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # rebuild vector store with all files in data/
    docs = load_documents(str(DATA_DIR))
    global vector_store
    
    def rebuild_vs():
        return get_or_create_vector_store(docs, persist_directory=str(DATA_DIR / "chroma_db"))
        
    vector_store = await asyncio.to_thread(rebuild_vs)
    
    # Clear sessions since vector store changed
    sessions.clear()

    return {"ok": True, "filename": file.filename, "meta": json.loads(meta) if meta else {}}
