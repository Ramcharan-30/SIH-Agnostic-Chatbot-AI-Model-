# SIH-AI-BOT

SIH-AI-BOT is a 3-service campus assistant:

- `Frontend/`: React + TypeScript + Vite client
- `Backend/`: Node.js + Express API gateway
- `bot_before_integration/`: Python FastAPI RAG bot

The frontend sends chat requests to the Node backend. The backend normalizes the request, optionally logs the conversation to MongoDB, forwards the question to the Python bot, and returns the final answer to the UI.

## Architecture

```text
Browser
  -> Frontend (Vite/React, port 8080)
  -> Backend (Express, port 5000)
  -> Python Bot (FastAPI, port 8000)
  -> Optional MongoDB (chat log persistence)
```

## Repository Layout

```text
SIH-AI-BOT/
├─ Frontend/
│  ├─ src/
│  │  ├─ api/              # frontend HTTP helpers
│  │  ├─ components/       # UI components
│  │  ├─ hooks/            # chat-related hooks
│  │  └─ pages/            # route pages, including /chat
│  ├─ vite.config.ts       # Vite config, port 8080
│  └─ .env                 # VITE_BACKEND_URL
├─ Backend/
│  ├─ controller/          # request handlers
│  ├─ middleware/          # rate limit + error handling
│  ├─ models/              # mongoose schemas
│  ├─ routes/              # chat/admin routes
│  ├─ services/            # Python bot HTTP bridge
│  ├─ utils/               # session helpers
│  ├─ app.js               # Express app setup
│  ├─ server.js            # Node entrypoint
│  └─ .env                 # backend runtime variables
└─ bot_before_integration/
   ├─ bot_server.py        # FastAPI entrypoint
   ├─ fun.py               # RAG, embeddings, retrieval, LLM calls
   ├─ data/                # PDFs/DOCX + persisted Chroma DB
   └─ .env                 # Python bot secrets/config
```

## Frontend

Stack:

- React 18
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- React Router

Important files:

- `Frontend/src/pages/Chatbot.tsx`: chat screen
- `Frontend/src/api/chatService.ts`: sends `POST /api/chat`
- `Frontend/src/App.tsx`: route registration
- `Frontend/vite.config.ts`: dev server on port `8080`

Runtime behavior:

- Reads `VITE_BACKEND_URL` from `Frontend/.env`
- Sends `{ sessionId, message }` to the backend
- Expects the backend response body to contain `answer`

## Backend

Stack:

- Node.js
- Express
- Axios
- Mongoose
- Helmet
- CORS
- Morgan
- express-rate-limit

Important files:

- `Backend/server.js`: starts Express on `PORT` or `5000`
- `Backend/app.js`: middleware, routes, Mongo connection
- `Backend/controller/chatController.js`: main chat flow
- `Backend/services/botService.js`: calls the Python bot
- `Backend/routes/chat.js`: chat and FAQ upload routes
- `Backend/routes/admin.js`: log inspection route

Routes:

- `POST /api/chat`
  - body: `{ userId?, message, sessionId?, language? }`
  - response: `{ answer, sessionId, confidence, needsHuman, sources, humanContact? }`
- `POST /upload-faq`
  - multipart form-data with `file` and optional `meta`
- `GET /admin/logs`
  - returns recent stored chat logs

Notes:

- Rate limit is `30` requests per minute per IP.
- MongoDB is used for persistence only.
- If MongoDB is unreachable, the backend now stays up and skips log persistence instead of crashing.

## Python Bot

Stack inferred from the code:

- FastAPI
- LangChain
- Chroma
- sentence-transformers / Hugging Face embeddings
- OpenAI client against OpenRouter
- PyPDFLoader / Docx2txtLoader

Important files:

- `bot_before_integration/bot_server.py`: HTTP API
- `bot_before_integration/fun.py`: document loading, vector store creation, retrieval, answer generation
- `bot_before_integration/data/`: source documents and persisted Chroma files

Routes:

- `POST /api/ask`
  - body: `{ question }` or `{ message }`
  - returns answer metadata used by the backend
- `POST /api/upload-faq`
  - ingests a document and rebuilds the vector store

Behavior:

- Loads documents from `bot_before_integration/data/`
- Reuses `data/chroma_db` if it already exists
- Returns `answer`, `confidence`, `intent`, `entities`, and `sources`

## Environment Variables

### Frontend

`Frontend/.env`

```env
VITE_BACKEND_URL=http://localhost:5000
```

### Backend

`Backend/.env`

```env
PORT=5000
MONGODB_URI=...
PYTHON_BOT_URL=http://localhost:8000
BOT_API_KEY=...
ADMIN_CONTACT=helpdesk@college.edu
LOG_RETENTION_DAYS=90
REQUEST_TIMEOUT_MS=15000
CONFIDENCE_THRESHOLD=0.6
PY_API_BASE=http://localhost:8000
```

### Python Bot

`bot_before_integration/.env`

```env
OPENROUTER_API_KEY=...
```

Do not commit real credentials. Use local `.env` files or `.env.example` templates.

## Start Guide

Run the services in this order in separate terminals.

### 1. Python bot

If you want to use the existing local environment:

```powershell
cd D:\SIH-AI-BOT\bot_before_integration
..\environ\Scripts\activate
uvicorn bot_server:app --host 0.0.0.0 --port 8000 --reload
```

If you need to create a new environment, install the packages used by the code first:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn python-multipart langchain langchain-community langchain-text-splitters chromadb sentence-transformers docx2txt pypdf openai python-dotenv
uvicorn bot_server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Backend

```powershell
cd D:\SIH-AI-BOT\Backend
npm install
npm run dev
```

Expected port: `5000`

### 3. Frontend

```powershell
cd D:\SIH-AI-BOT\Frontend
npm install
npm run dev
```

Expected port: `8080`

Open:

- `http://localhost:8080/` for the landing page
- `http://localhost:8080/chat` for the chat UI

## End-to-End Request Flow

1. The user submits a message from `Frontend/src/pages/Chatbot.tsx`.
2. The frontend calls `Frontend/src/api/chatService.ts`.
3. The backend receives `POST /api/chat`.
4. The backend creates or reuses a `sessionId`.
5. The backend forwards the question to `http://localhost:8000/api/ask`.
6. The Python bot retrieves relevant chunks from Chroma and generates an answer.
7. The backend returns normalized JSON with `answer`, `confidence`, `needsHuman`, and `sources`.
8. The frontend renders the returned answer in the chat thread.

## Issues Found and Fixed

1. Frontend/backend response mismatch:
   - The backend returns `answer`.
   - The frontend chat page and API helper were reading `reply`.
   - Result: the frontend showed an empty/fallback response even when the backend answered correctly.

2. Broken backend npm scripts:
   - `Backend/package.json` pointed to `src/server.js`.
   - The actual entrypoint is `Backend/server.js`.
   - Result: `npm start` and `npm run dev` did not start the API.

3. Backend hard dependency on MongoDB startup:
   - The API exited when MongoDB Atlas was unreachable.
   - Result: the frontend could not reach the backend at all.
   - Current behavior: the backend continues running without persistence and still serves chat requests.

## Verification

Verified locally in this workspace:

- Frontend production build succeeded with `npm run build`
- Backend starts with `npm run start`
- Backend now remains available even when MongoDB DNS/Atlas is unreachable

Not fully verified here:

- Live chat answer generation from the Python bot
- MongoDB-backed log persistence against a reachable database

Both depend on local external services being available.

## Troubleshooting

- If the frontend cannot connect, confirm `VITE_BACKEND_URL` points to the backend port.
- If the backend returns bot errors, confirm the Python bot is running on port `8000`.
- If the Python bot says no documents are indexed, upload FAQ files or place PDF/DOCX files in `bot_before_integration/data/`.
- If MongoDB is unavailable, chat should still work, but `/admin/logs` will not show persisted data.
- If Vite fails to start on `8080`, check for a port conflict in `Frontend/vite.config.ts`.
