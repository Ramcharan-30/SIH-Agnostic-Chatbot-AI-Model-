# bot_server.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil, json
import os

# Import functions from your fun.py
# fun.py must be in the same directory (it defines load_documents, get_or_create_vector_store, ask_ai)
from fun import load_documents, get_or_create_vector_store, ask_ai

app = FastAPI(title="Python Bot API")

# Optional: allow all origins (not necessary for server-to-server calls, but harmless)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# keep a module-global vector_store so we don't rebuild for every request
vector_store = None

def ensure_vector_store():
    global vector_store
    if vector_store is None:
        if any(DATA_DIR.iterdir()):
            docs = load_documents(str(DATA_DIR))
            vector_store = get_or_create_vector_store(docs, persist_directory=str(DATA_DIR / "chroma_db"))
        else:
            vector_store = None
    return vector_store


@app.post("/api/ask")
async def api_ask(payload: dict):
    """POST body: { "question": "...", "session_id": "...", "userId": "...", "language": "..." }"""
    question = payload.get("question") or payload.get("message")
    if not question:
        raise HTTPException(status_code=400, detail="question required")

    vs = ensure_vector_store()
    if vs is None:
        # no docs indexed yet; instruct user to upload docs
        raise HTTPException(status_code=500, detail="No documents indexed. Upload FAQ files via /api/upload-faq first.")

    result = ask_ai(vs, question)
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
    vector_store = get_or_create_vector_store(docs, persist_directory=str(DATA_DIR / "chroma_db"))

    return {"ok": True, "filename": file.filename, "meta": json.loads(meta) if meta else {}}
