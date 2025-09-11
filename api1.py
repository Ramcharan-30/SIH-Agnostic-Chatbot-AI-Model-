from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import sys
import os
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

# Add the current directory to Python path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# Import your chatbot functions
try:
    from fun import load_documents, get_or_create_vector_store, create_qa_chain, ConversationMemory
    print("Successfully imported chatbot functions")
except ImportError as e:
    print(f"Import error: {e}")

# Global variables
vector_store = None
qa_chain_func = None

# Modern lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    global vector_store, qa_chain_func
    
    try:
        script_dir = Path(__file__).resolve().parent
        data_dir = script_dir / "data"
        
        print("Loading documents...")
        documents = load_documents(str(data_dir))
        print(f"Loaded {len(documents)} documents")
        
        print("Creating vector store...")
        vector_store = get_or_create_vector_store(documents, persist_directory=str(data_dir / "chroma_db"))
        
        print("Initializing QA chain...")
        memory = ConversationMemory(max_history=5)
        qa_chain_func = create_qa_chain(vector_store, memory)
        
        print("API startup complete!")
        
    except Exception as e:
        print(f"Startup error: {e}")
        raise
    
    yield
    
    print("API shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Add CORS middleware for MERN frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# --- Request models ---
class QueryRequest(BaseModel):
    question: str
    session_id: str = "default"

class SourceDocument(BaseModel):
    source: str
    page: str
    content_preview: str

class ChatbotResponse(BaseModel):
    success: bool
    question: str
    answer: str
    intent: str
    confidence: float
    entities: Dict[str, Any]
    sources: List[SourceDocument] = []
    error: str = None

class SimpleResponse(BaseModel):
    success: bool
    question: str
    answer: str
    sources: List[SourceDocument]
    error: str = None

# --- API endpoints ---
@app.post("/api/ask", response_model=ChatbotResponse)
async def ask_question(request: QueryRequest):
    """Main chatbot endpoint with full capabilities"""
    try:
        if qa_chain_func is None:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        
        # Use your full QA chain
        result = qa_chain_func({"query": request.question})
        
        # Format source documents for response
        sources = []
        for doc in result.get("source_documents", []):
            sources.append(SourceDocument(
                source=doc.metadata.get("source", "unknown"),
                page=str(doc.metadata.get("page", "N/A")),
                content_preview=doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
            ))
        
        return ChatbotResponse(
            success=True,
            question=request.question,
            answer=result["result"],
            intent=result["intent_info"]["intent"],
            confidence=result["intent_info"]["confidence"],
            entities=result["intent_info"]["entities"],
            sources=sources
        )
        
    except Exception as e:
        return ChatbotResponse(
            success=False,
            question=request.question,
            answer="",
            intent="error",
            confidence=0.0,
            entities={},
            error=f"Error processing question: {str(e)}"
        )

@app.post("/api/ask-simple", response_model=SimpleResponse)
async def ask_simple(request: QueryRequest):
    """Simple similarity search endpoint"""
    try:
        if vector_store is None:
            raise HTTPException(status_code=503, detail="Vector store not initialized")
        
        results = vector_store.similarity_search(request.question, k=3)
        answer = "\n\n".join([doc.page_content for doc in results])
        
        # Format sources
        sources = []
        for doc in results:
            sources.append(SourceDocument(
                source=doc.metadata.get("source", "unknown"),
                page=str(doc.metadata.get("page", "N/A")),
                content_preview=doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
            ))
        
        return SimpleResponse(
            success=True,
            question=request.question,
            answer=answer,
            sources=sources
        )
    except Exception as e:
        return SimpleResponse(
            success=False,
            question=request.question,
            answer="",
            sources=[],
            error=f"Error: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "chatbot-api",
        "vector_store_ready": vector_store is not None,
        "qa_chain_ready": qa_chain_func is not None
    }

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/ask": "Full chatbot with intent recognition",
            "POST /api/ask-simple": "Simple similarity search",
            "GET /api/health": "System health check",
            "GET /api/info": "This information"
        }
    }

# --- Run the API ---
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)  