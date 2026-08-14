# SIH Agnostic Chatbot AI Model - Project Documentation

**Created:** August 14, 2026  
**Repository:** Ramcharan-30/SIH-Agnostic-Chatbot-AI-Model-  
**Purpose:** Interview-ready comprehensive documentation for code analysis and explanation

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Repository Structure](#repository-structure)
4. [Architecture Overview](#architecture-overview)
5. [Backend Architecture](#backend-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [Bot Integration](#bot-integration)
8. [Key Features](#key-features)
9. [API Endpoints](#api-endpoints)
10. [Development Workflow](#development-workflow)
11. [Interview Talking Points](#interview-talking-points)

---

## Project Overview

**Project Name:** SIH Agnostic Chatbot AI Model  
**Description:** An AI Model built for the Smart India Hackathon (SIH) that provides an agnostic chatbot interface capable of processing user queries, maintaining conversation context, and integrating with multiple AI backends.

**Primary Goal:** Build a flexible, scalable chatbot system that can work with different AI models and backends while providing a unified user interface.

**Key Characteristics:**
- Full-stack application with separate frontend and backend
- Multi-language support (primarily TypeScript/JavaScript with Python components)
- RAG (Retrieval-Augmented Generation) implementation for knowledge-based queries
- Session management with conversation memory
- Intent recognition and entity extraction capabilities

---

## Technology Stack

### Languages
| Language | Percentage | Primary Use |
|----------|-----------|-------------|
| TypeScript | 80.3% | Frontend & Backend logic |
| Python | 12.9% | AI/ML operations, Bot server |
| JavaScript | 4.2% | Configuration & Build files |
| CSS | 2% | Styling |
| Other | 0.6% | Miscellaneous |

### Backend Stack
**Runtime & Framework:**
- **Node.js** (v18.0.0+)
- **Express.js** (v5.1.0) - HTTP server framework
- **MongoDB** (v7.3.0) - Database
- **Mongoose** (v8.18.1) - MongoDB ODM

**Key Dependencies:**
- `axios` (v1.11.0) - HTTP client for API calls
- `cors` (v2.8.5) - Cross-Origin Resource Sharing
- `helmet` (v8.1.0) - Security middleware
- `express-rate-limit` (v8.1.0) - Rate limiting
- `morgan` (v1.10.1) - HTTP request logging
- `multer` (v2.0.2) - File upload handling
- `uuid` (v13.0.0) - Unique identifier generation

### Frontend Stack
**Framework & Build:**
- **React** (v18.3.1)
- **TypeScript** (v5.8.3)
- **Vite** (v5.4.19) - Build tool
- **Tailwind CSS** (v3.4.17) - Utility-first CSS

**UI Components & Libraries:**
- **Shadcn/UI** - Component library built on Radix UI
- **React Router** (v6.30.1) - Client-side routing
- **React Hook Form** (v7.61.1) - Form management
- **React Query** (@tanstack/react-query v5.83.0) - Server state management
- **Zod** (v3.25.76) - TypeScript-first schema validation
- **Recharts** (v2.15.4) - Charting library
- **Lucide React** (v0.462.0) - Icon library

### Python AI/ML Stack
**Framework:**
- **FastAPI** - Modern async Python web framework
- **LangChain** - Framework for building LLM applications
- **Chroma** - Vector database for embeddings
- **LLM Integration** - Support for multiple language models

---

## Repository Structure

```
SIH-Agnostic-Chatbot-AI-Model-/
│
├── Backend/                    # Node.js Express API server
│   ├── api/                    # API endpoint definitions
│   ├── controller/             # Request handlers (MVC pattern)
│   ├── middleware/             # Express middleware
│   │   ├── rateLimiter.js     # Request rate limiting
│   │   └── errorHandler.js    # Global error handling
│   ├── models/                 # Database models (Mongoose schemas)
│   ├── routes/                 # API route definitions
│   │   ├── chat.js            # Chat endpoints
│   │   └── admin.js           # Admin endpoints
│   ├── services/              # Business logic layer
│   ├── utils/                 # Utility functions
│   ├── app.js                 # Express app configuration
│   ├── server.js              # Server entry point
│   ├── package.json           # Dependencies
│   ├── .env.example           # Environment variables template
│   └── vercel.json            # Vercel deployment config
│
├── Frontend/                   # React + TypeScript UI
│   ├── src/
│   │   ├── api/               # API client functions
│   │   ├── components/        # Reusable React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utility libraries
│   │   ├── assets/            # Static assets (images, icons)
│   │   ├── App.tsx            # Root app component
│   │   ├── main.tsx           # React entry point
│   │   └── index.css          # Global styles
│   ├── public/                # Static files
│   ├── package.json           # Dependencies
│   ├── vite.config.ts         # Vite configuration
│   ├── tailwind.config.ts     # Tailwind CSS configuration
│   ├── tsconfig.json          # TypeScript configuration
│   └── vercel.json            # Vercel deployment config
│
├── bot_before_integration/    # Python AI bot (pre-integration version)
│   ├── bot_server.py          # FastAPI server for bot
│   ├── fun.py                 # Core bot logic & RAG implementation
│   ├── requirements.txt       # Python dependencies
│   ├── Procfile               # Heroku/process deployment config
│   ├── render.yaml            # Render deployment config
│   └── data/                  # Document/FAQ storage
│
├── README.md                  # Project overview
└── PROJECT_DOCUMENTATION.md   # This file
```

---

## Architecture Overview

### High-Level Flow

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└─���────┬──────┘
       │ HTTP/JSON
       ▼
┌──────────────────────┐
│  Express API Server  │
│    (Backend)         │
│  - Chat routes       │
│  - Admin routes      │
│  - Rate limiting     │
└──────┬───────────────┘
       │
       ├──→ MongoDB (Conversation logs)
       │
       └──→ FastAPI Python Bot
             (AI/ML Processing)
                │
                ├──→ Vector Store (Chroma)
                ├──→ LLM Integration
                └──→ RAG Pipeline
```

### Data Flow for Chat Request

1. **User Input** → Frontend React app
2. **API Call** → Express Backend (`/api/ask` or similar)
3. **Processing** → Backend middleware (rate limiting, validation)
4. **Query Forwarding** → Python FastAPI Bot server
5. **Vector Search** → Chroma vector database (document retrieval)
6. **LLM Processing** → Generate response with context
7. **Response** → Back through backend to frontend
8. **Logging** → Store in MongoDB for history/analytics
9. **UI Update** → Display response to user

---

## Backend Architecture

### Express.js Setup (`Backend/app.js`)

**Key Configuration:**
```javascript
- Helmet: Security headers middleware
- CORS: Accepts requests from any origin (GET, POST)
- JSON Parser: 500KB limit for request bodies
- Morgan: HTTP request logging
- Rate Limiting: Applied globally
- Error Handler: Centralized error management
```

**Middleware Stack (in order):**
1. Helmet - Security
2. CORS - Cross-origin requests
3. Express.json - Parse JSON bodies
4. Morgan - Logging
5. Rate Limiter - Request throttling
6. Routes (Chat & Admin)
7. Error Handler - Exception catching

### Database Connection

**Technology:** MongoDB with Mongoose ODM  
**Connection:** Optional (graceful degradation if not available)  
**Purpose:** 
- Store chat conversation logs
- User sessions and history
- Analytics and audit trails

**Environment Variable:** `MONGODB_URI`  
**Behavior:** Application continues without DB if connection fails

### API Routes

#### Chat Routes (`Backend/routes/chat.js`)
Primary endpoints for chatbot interaction:
- `POST /api/ask` - Submit a question to the bot
- `POST /api/message` - Send a chat message
- `GET /api/history` - Retrieve conversation history
- Other chat-related endpoints

#### Admin Routes (`Backend/routes/admin.js`)
Administrative operations:
- Analytics/metrics endpoints
- Configuration management
- Session management
- Logging/debugging endpoints

### Middleware Components

#### Rate Limiter (`middleware/rateLimiter.js`)
- Prevents abuse through request throttling
- Protects API from DDoS attacks
- Limits requests per IP address

#### Error Handler (`middleware/errorHandler.js`)
- Catches all errors from routes
- Standardizes error responses
- Logs errors for debugging

---

## Frontend Architecture

### React App Setup

**Framework:** React 18 with TypeScript  
**Build Tool:** Vite (modern, fast bundler)  
**Styling:** Tailwind CSS + Shadcn/UI components

### Project Structure

**Pages/Routes** (`src/pages/`)
- Different view components for chat, admin, settings, etc.

**Components** (`src/components/`)
- Reusable UI building blocks
- Chat interface components
- Message display components
- Input/form components

**API Client** (`src/api/`)
- Centralized HTTP client using axios
- Type-safe API endpoints
- Request/response interceptors
- Error handling

**Custom Hooks** (`src/hooks/`)
- `useChat()` - Chat state management
- `useMessage()` - Message handling
- Custom lifecycle hooks for specific features

**Utilities** (`src/lib/`)
- Helper functions
- Constants
- Formatting utilities

### State Management

**React Query** - Server state (API responses)
- Automatic caching
- Background refetching
- Request deduplication
- Automatic retry logic

**React Hooks** - Local state
- `useState` for component state
- `useEffect` for side effects
- `useContext` for shared state (via React Hook Form)

**React Router** - Navigation
- Client-side routing
- Nested routes
- Dynamic route handling

### Form Handling

**React Hook Form** with **Zod** validation:
- Declarative form management
- Type-safe validation schemas
- Minimal re-renders
- Excellent performance

---

## Bot Integration

### Python Bot Server (`bot_before_integration/bot_server.py`)

**Framework:** FastAPI  
**Purpose:** AI/ML processing and RAG (Retrieval-Augmented Generation)

**Key Endpoints:**

```python
POST /api/ask
- Input: { "question": str, "session_id": str, "userId": str, "language": str }
- Processing: Query vector store, generate response
- Output: { "answer": str, "intent": str, "confidence": float, "entities": dict, "sources": list }

POST /api/upload-faq
- Input: Multipart file upload + metadata
- Processing: Process document, update vector store
- Output: { "ok": bool, "filename": str, "meta": dict }
```

**Session Management:**
- In-memory session cache (user_id → QA chain)
- Conversation memory per session (max 5 history items)
- Production use: Would migrate to Redis

### RAG Implementation (`bot_before_integration/fun.py`)

**Key Components:**

1. **Document Loading** (`load_documents()`)
   - Reads FAQ files from `data/` directory
   - Supports multiple formats (PDF, TXT, etc.)

2. **Vector Store** (`get_or_create_vector_store()`)
   - Uses Chroma for vector embeddings
   - Persists to disk for durability
   - Enables semantic search

3. **Conversation Memory** (`ConversationMemory` class)
   - Maintains chat history
   - Limits history to prevent context overflow
   - Provides context for follow-up questions

4. **QA Chain** (`create_qa_chain()`)
   - Combines vector store + LLM
   - Retrieves relevant documents
   - Generates answers with sources
   - Performs intent recognition and entity extraction

### Async/Performance Optimization

**Threading Model:**
```python
# Long-running operations moved to thread pool
result = await asyncio.to_thread(process_ask, question, session_id)

# Prevents blocking the FastAPI event loop
```

**Startup Preloading:**
```python
@app.on_event("startup")
async def startup_event():
    # Preload vector store on app startup
    # Reduces latency on first request
    await asyncio.to_thread(ensure_vector_store)
```

---

## Key Features

### 1. Chatbot Interface
- Real-time message display
- Conversation history
- Session persistence
- Multi-user support

### 2. Intent Recognition
- Automatically identifies user intent
- Returns confidence scores
- Enables intent-specific responses

### 3. Entity Extraction
- Recognizes entities in user queries
- Supports multiple entity types
- Used for context-aware responses

### 4. Document Management
- FAQ/document upload capability
- Automatic vector indexing
- Semantic search over documents

### 5. Conversation Memory
- Maintains context across messages
- Previous message awareness
- Configurable history length

### 6. Rate Limiting
- Prevents API abuse
- Per-IP request throttling
- Configurable limits

### 7. Error Handling
- Graceful error responses
- Detailed error messages
- Centralized error management

### 8. Security Features
- Helmet.js security headers
- CORS configuration
- Input validation
- Rate limiting

---

## API Endpoints

### Base URLs
- **Backend:** `http://localhost:3000` (development)
- **Python Bot:** `http://localhost:8000` (development)
- **Frontend:** `http://localhost:5173` (Vite dev server)

### Chat Endpoints

**POST /api/ask**
```json
Request:
{
  "question": "What is the refund policy?",
  "session_id": "user_123",
  "userId": "user_123",
  "language": "en"
}

Response:
{
  "answer": "Our refund policy allows...",
  "intent": "policy_inquiry",
  "confidence": 0.95,
  "entities": {
    "topic": "refund",
    "action": "inquire"
  },
  "sources": [
    { "source": "faq.pdf", "page": 1 },
    { "source": "policies.txt", "page": null }
  ]
}
```

**POST /api/upload-faq**
```
Content-Type: multipart/form-data
- file: [binary file data]
- meta: {"category": "FAQ", "version": "1.0"}

Response:
{
  "ok": true,
  "filename": "faq.pdf",
  "meta": {"category": "FAQ", "version": "1.0"}
}
```

### Admin Endpoints

**POST /admin/analytics**
- Retrieve usage analytics
- Chat volume statistics
- Intent distribution

**GET /admin/sessions**
- List active sessions
- Session details and metadata

---

## Development Workflow

### Backend Setup

```bash
# Navigate to backend
cd Backend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env with MongoDB URI and other configs

# Development mode (with auto-reload)
npm run dev

# Production mode
npm start
```

### Frontend Setup

```bash
# Navigate to frontend
cd Frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env with API base URL

# Development mode (Vite dev server)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Python Bot Setup

```bash
# Navigate to bot
cd bot_before_integration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python bot_server.py

# Or use Uvicorn directly
uvicorn bot_server:app --reload
```

### Environment Variables

**Backend (.env):**
```
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/chatbot
NODE_ENV=development
PORT=3000
```

**Frontend (.env):**
```
VITE_API_URL=http://localhost:3000
VITE_BOT_URL=http://localhost:8000
```

**Python Bot (.env):**
```
OPENAI_API_KEY=your_key_here
LLM_MODEL=gpt-3.5-turbo
```

---

## Interview Talking Points

### 1. Architecture & Design Decisions

**Questions You Might Receive:**
- "Why did you choose Express for the backend?"
  - Lightweight, high-performance Node.js framework
  - Large ecosystem and community support
  - Easy to build RESTful APIs
  - Supports middleware pattern for clean separation of concerns

- "Why separate the Python bot into its own service?"
  - Allows independent scaling of AI/ML components
  - Python has better ML libraries (LangChain, Chroma, etc.)
  - Can upgrade/restart bot without affecting API
  - Future-proof for swapping different AI engines

- "How does your RAG (Retrieval-Augmented Generation) work?"
  - Documents are chunked and converted to embeddings
  - Embeddings stored in Chroma vector database
  - User query converted to embedding and searched
  - Retrieved documents provided as context to LLM
  - LLM generates answer based on context + knowledge

### 2. Technology Choices

**Why TypeScript?**
- Type safety catches errors at development time
- Better IDE support and autocomplete
- Self-documenting code through types
- Easier refactoring and maintenance
- Industry standard for modern web development

**Why React + Tailwind?**
- Component-based architecture for reusability
- Virtual DOM for performance
- Tailwind for rapid UI development without custom CSS
- Shadcn/UI provides production-ready components

**Why FastAPI for Python bot?**
- Async support for non-blocking operations
- Automatic API documentation (Swagger/OpenAPI)
- Built-in data validation
- Fast performance comparable to Node.js

### 3. Key Technical Implementations

**Session Management:**
- Tracked via session_id
- Conversation memory maintains last 5 messages
- Allows follow-up questions with context
- Prevents token overflow in LLM calls

**Rate Limiting Strategy:**
- Per-IP limiting to prevent abuse
- Protects free tier usage
- Prevents DDoS attacks
- Configurable thresholds

**Error Handling:**
- Middleware pattern for centralized handling
- Graceful degradation (works without DB)
- Detailed error logs for debugging
- User-friendly error messages

**Async Operations:**
- Uses asyncio for thread pooling
- Prevents blocking the event loop
- FastAPI handles multiple concurrent requests
- Preloading on startup reduces latency

### 4. Scalability Considerations

**What Would You Change for Production?**
- Redis for session caching instead of in-memory
- Load balancing for multiple backend instances
- Document versioning in vector store
- Proper authentication/authorization
- Request logging and monitoring
- Database indices for performance
- CDN for static frontend assets

**Performance Optimizations:**
- Vector store preloading on startup
- Request deduplication with React Query
- Lazy loading of components
- Database query optimization
- Caching strategies

### 5. Challenges & Solutions

**Challenge: Context Window Limits**
- Solution: Conversation memory with fixed history size
- Solution: Summarization of long conversations
- Solution: Hierarchical context management

**Challenge: Vector Search Latency**
- Solution: Pre-compute and cache embeddings
- Solution: Use approximate nearest neighbor search
- Solution: Parallel processing with threading

**Challenge: Cross-Origin Requests**
- Solution: CORS middleware with proper configuration
- Solution: Same-origin deployment strategy
- Solution: Proxy server in production

### 6. Code Quality & Best Practices

**Points to Highlight:**
- Error handling at every layer
- Environment-based configuration
- Separation of concerns (controllers, services, models)
- Type safety with TypeScript
- Input validation with Zod
- Logging with Morgan
- Security with Helmet
- Rate limiting for API protection

---

## Deployment Information

### Backend Deployment (Vercel)
- Configuration in `Backend/vercel.json`
- Auto-deploys from main branch
- Environment variables configured in Vercel dashboard

### Frontend Deployment (Vercel)
- Configuration in `Frontend/vercel.json`
- Static site hosting
- Automatic builds on push

### Python Bot Deployment
- **Options:** Render.com, Heroku, AWS Lambda
- Config files: `Procfile`, `render.yaml`
- Requires Python runtime and dependencies

---

## Additional Resources

### Key Files for Interview
- `Backend/app.js` - Core Express setup
- `Backend/routes/chat.js` - API endpoint logic
- `Backend/middleware/` - Middleware implementation
- `bot_before_integration/bot_server.py` - FastAPI setup
- `bot_before_integration/fun.py` - RAG implementation
- `Frontend/src/App.tsx` - React app structure
- `Frontend/src/api/` - API client implementation

### Concepts to Review
- RESTful API design
- Middleware pattern
- Vector embeddings and similarity search
- Conversation context management
- Async/await and event loops
- React hooks and state management
- Type safety with TypeScript
- Security best practices
- Rate limiting and throttling

---

## Quick Start for Interviewers

To explain this project to an interviewer:

1. **Start with the big picture:** "This is a full-stack chatbot application built during Smart India Hackathon with a React frontend, Express backend, and Python AI engine."

2. **Explain the architecture:** "We separated concerns - the Express backend handles HTTP/API layer, connects to MongoDB for persistence, and forwards AI queries to a Python FastAPI service."

3. **Highlight the AI component:** "The Python bot implements Retrieval-Augmented Generation using Chroma for vector search and LangChain for LLM integration."

4. **Discuss technical decisions:** "We chose TypeScript for type safety, React for the UI, and FastAPI+Python because that ecosystem has better ML libraries."

5. **Walk through a request:** "When a user sends a question, it goes through rate limiting, the Express backend receives it, calls the Python bot which searches the vector store, gets context, queries an LLM, and returns a response with sources and confidence scores."

6. **Mention scalability:** "For production, we'd use Redis instead of in-memory sessions, implement proper auth, add monitoring, and use a load balancer for horizontal scaling."

---

**Last Updated:** August 14, 2026  
**Documentation Version:** 1.0  

Use this documentation as your reference guide for technical interviews. Customize examples and talking points based on specific questions asked.
