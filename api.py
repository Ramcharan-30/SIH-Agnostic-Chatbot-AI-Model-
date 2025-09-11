from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import sys
import os
from contextlib import asynccontextmanager

# Add the current directory to Python path to import your chatbot module
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# Import your chatbot functions
try:
    from fun import load_documents, get_or_create_vector_store, create_qa_chain, ConversationMemory, IntentEntityRecognizer
    print("Successfully imported chatbot functions")
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure your chatbot code is in 'fun.py' in the same directory")

# Global variables
vector_store = None
qa_chain_func = None

# Modern lifespan handler (replaces @app.on_event)
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
    
    yield  # This is where the app runs
    
    # Shutdown code (optional)
    print("API shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# --- Request models ---
class Query(BaseModel):
    question: str

class Response(BaseModel):
    question: str
    answer: str
    success: bool = True

# --- API endpoints ---
@app.post("/ask", response_model=Response)
async def ask_question(query: Query):
    """Ask a question using the full chatbot pipeline"""
    try:
        if qa_chain_func is None:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        
        # Use your full QA chain
        result = qa_chain_func({"query": query.question})
        
        return Response(
            question=query.question,
            answer=result["result"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/ask_simple")
async def ask_simple(query: Query):
    """Simple similarity search (fallback)"""
    try:
        if vector_store is None:
            raise HTTPException(status_code=503, detail="Vector store not initialized")
        
        results = vector_store.similarity_search(query.question, k=3)
        answer = "\n\n".join([doc.page_content for doc in results])
        
        return {
            "question": query.question, 
            "answer": answer,
            "sources": [{
                "source": doc.metadata.get("source", "unknown"), 
                "page": doc.metadata.get("page", "N/A"),
                "content_preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            } for doc in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "vector_store_ready": vector_store is not None,
        "qa_chain_ready": qa_chain_func is not None
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Chatbot API is running",
        "endpoints": {
            "POST /ask": "Full chatbot with intent recognition and memory",
            "POST /ask_simple": "Simple similarity search",
            "GET /health": "System health check",
            "GET /": "This information page"
        }
    }

# --- Run the API ---
if __name__ == "__main__":
    # For production, use this instead to avoid the reload warning:
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)