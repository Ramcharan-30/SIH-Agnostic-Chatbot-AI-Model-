# SIH-Agnostic-Chatbot-AI-Model

## Overview
This project is a Retrieval-Augmented Generation (RAG) based chatbot specifically tailored for students. It serves as an interactive LLM-based assistant that answers student queries regarding course schedules, mess timings, exams, hostel issues, fees, and more by drawing context directly from institution-provided documents (PDFs, DOCX).

## Architecture
1. **Document Ingestion & Chunking**: Institutional documents stored in the `data/` directory are loaded using `PyPDFLoader` and `Docx2txtLoader`. The text is split into manageable context chunks using LangChain's `RecursiveCharacterTextSplitter`.
2. **Vector Store & Embeddings**: Chunked text is transformed into dense vector representations using multilingual Hugging Face embeddings and stored locally in a **Chroma** vector database, facilitating fast semantic similarity searches.
3. **Intent & Entity Recognition (NLP)**: A custom rule-based `IntentEntityRecognizer` parses inbound queries. It matches inputs against pre-defined regex patterns to categorize the student's intent (e.g., `course_schedule`, `mess_timings`) and extracts specific entities.
4. **LLM Answer Generation**: 
   - Relevant document context is retrieved from the Chroma DB.
   - A custom prompt combines the conversational history (managed via `ConversationMemory`), the retrieved context, and the recognized entity/intent data.
   - The query is then sent to **DeepSeek V3.1** (via the OpenRouter API) to generate an accurate, conversational answer based purely on the provided institutional context.
5. **Backend API API Serving**: A FastAPI server wraps the conversational pipeline into HTTP endpoints, enabling chat interactions (`/ask` or `/api/ask`) as well as RESTful interfaces for uploading supplementary context guidelines (`/api/upload-faq`).

## Tech Stack
- **Core Language**: Python 3.13
- **Backend Framework**: FastAPI
- **LLM Setup & Chaining**: LangChain
- **Embeddings**: HuggingFace (`langchain_community.embeddings.HuggingFaceEmbeddings`)
- **Vector Database**: Chroma (sqlite3-based local persist database)
- **Large Language Model**: DeepSeek V3.1 (accessed via OpenRouter API)
- **Document Loading**: PyPDFLoader, Docx2txtLoader

## Usage Guide
### 1. Prerequisites
- Create a `.env` file at the root level of the repository.
- Provide your OpenRouter API key:
  ```env
  OPENROUTER_API_KEY=your_openrouter_api_key
  ```

### 2. Prepare Context Documents
- Place any required FAQs, rulebooks, or curriculum documents (PDF, DOCX) inside the `data/` directory. (If missing, the script will create the directory, but you'll have to provide resources).

### 3. Running the Backend Server
- Activate Python environment:
  ```shell
  .\environ\Scripts\Activate.ps1
  ```
- Start the FastApi application:
  ```shell
  uvicorn bot_server:app --host 0.0.0.0 --port 8000
  ```
  *(You can also use this server's endpoint to interactively upload FAQ documents).*

- **Alternatively (Interactive Console Mode):**
  If you want to run and test queries in your CLI without spinning up a server, run the core toolkit directly:
  ```shell
  python fun.py
  ```


