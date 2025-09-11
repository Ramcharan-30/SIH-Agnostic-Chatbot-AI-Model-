from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from pathlib import Path

from fun import load_documents, get_or_create_vector_store, ask_ai

app = FastAPI()

# --- Setup ---
script_dir = Path(__file__).resolve().parent
data_dir = script_dir / "data"

documents = load_documents(str(data_dir))
vector_store = get_or_create_vector_store(
    documents, persist_directory=str(data_dir / "chroma_db")
)

# --- Input model ---
class Query(BaseModel):
    question: str

# --- Endpoint ---
@app.post("/ask")
async def ask(query: Query):
    result = ask_ai(vector_store, query.question)

    answer = result.get("answer", "").strip()
    confidence = result.get("confidence", 0)

    # --- Clean answer formatting ---
    if confidence == 0:
        # Remove disclaimers like "Based on the context..."
        if "The answer to your question is" in answer:
            clean_answer = answer.split("The answer to your question is")[-1].strip()
            clean_answer = "The answer is " + clean_answer
        else:
            # Fallback → just return last sentence
            clean_answer = answer.split("\n")[-1].strip()

        return {
            "question": query.question,
            "answer": clean_answer
        }

    # --- Normal high-confidence response ---
    return {
        "question": query.question,
        "answer": answer,
        "intent": result.get("intent"),
        "confidence": confidence,
        "entities": result.get("entities", {}),
        "sources": result.get("sources", [])
    }


# --- Run ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
@app.post("/ask")
async def ask(query: Query):
    result = ask_ai(vector_store, query.question)

    # Extract answer + confidence
    answer = result.get("answer", "")
    confidence = result.get("confidence", 0)

    # If confidence is low, return only the direct answer (no context junk)
    if confidence == 0:
        clean_answer = answer.split("\n\n")[-1]  # take only last sentence (the real answer)
        return {
            "question": query.question,
            "answer": clean_answer.strip()
        }

    # Otherwise return full result
    return {
        "question": query.question,
        "answer": answer,
        "intent": result.get("intent"),
        "confidence": confidence,
        "entities": result.get("entities", {}),
        "sources": result.get("sources", [])
    }
