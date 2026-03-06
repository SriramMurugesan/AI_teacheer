# AI PDF Tutor 🎓

A production-grade **RAG (Retrieval Augmented Generation)** application that transforms your PDFs into an intelligent AI tutor. Upload any document and get interactive lessons, quiz questions, and a ChatGPT-like Q&A experience — all powered by your own documents.

## Architecture

```
User → Frontend (React) → FastAPI → RAG Pipeline
                                       │
                              ┌────────┼────────┐
                              ▼        ▼        ▼
                         PDF Parser  FAISS   LLM Service
                         Chunker   VectorDB  (OpenAI/Ollama)
                         Embeddings
```

## Features

- 📄 **PDF Upload & Processing** — Upload PDFs, auto-extract and chunk text
- 💬 **RAG Chat** — Ask questions answered from your document context
- 🔄 **Streaming Responses** — Real-time Server-Sent Events streaming
- 📚 **AI Lesson Generator** — Create structured lessons from documents
- 📝 **Quiz Generator** — Auto-generate quizzes with difficulty levels
- 🔀 **Dual LLM Support** — OpenAI or Ollama (free, local, private)
- ⚡ **Async Throughout** — Non-blocking I/O for maximum throughput

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- [Ollama](https://ollama.com) (for free local LLM) or OpenAI API key

### 1. Install Ollama & Pull Model

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

### 2. Backend Setup

```bash
# Create virtual env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure env
cp .env.example .env

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** and start uploading PDFs!

### 4. Using OpenAI Instead

Edit `.env`:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/upload` | Upload PDF |
| `GET` | `/api/documents` | List documents |
| `DELETE` | `/api/documents/{id}` | Delete document |
| `POST` | `/api/chat` | Ask question (RAG) |
| `POST` | `/api/chat/stream` | Streaming chat (SSE) |
| `POST` | `/api/lesson` | Generate lesson |
| `POST` | `/api/quiz` | Generate quiz |

## Docker

```bash
docker build -t ai-tutor .
docker run -p 8000:8000 ai-tutor
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.11 |
| Frontend | React, Vite |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | FAISS |
| LLM | OpenAI / Ollama (Llama3) |
| PDF Parsing | pypdf |

## Project Structure

```
ai-pdf-tutor/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config/settings.py   # Environment-based configuration
│   ├── routers/             # API endpoint definitions
│   ├── services/            # Business logic (RAG pipeline)
│   ├── models/              # Pydantic request/response schemas
│   └── utils/prompts.py     # LLM prompt templates
├── frontend/                # React + Vite UI
├── Dockerfile               # Multi-stage production build
├── requirements.txt
└── .env.example
```

## License

MIT