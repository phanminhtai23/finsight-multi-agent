# FinSight — Multi-Agent Financial Research Assistant

> Submission for **Ready Tensor — Agentic AI Developer Certification (AAIDC), Module 2: Build Your Multi-Agent System**.

FinSight is a production-style, multi-agent system that answers financial questions about **any company** — either from documents you upload (PDF, Word, scanned images) or from live web/financial sources — and **always answers with inline citations** back to the exact source page.

It is built around a LangGraph supervisor orchestrating a team of specialized agents, a retrieval-augmented-generation (RAG) layer with advanced chunking and hybrid search, tools exposed through a dedicated **MCP server**, and an async task engine that lets you keep chatting while long jobs (document ingestion, deep research) run in the background.

---

## ✨ Key Features

- **Multi-agent orchestration (LangGraph supervisor)** — six focused agents (Supervisor, Retrieval, Market Research, Analyst, Writer, Critic) coordinating to solve a task.
- **RAG over your own documents** — upload PDF / DOCX / scanned images; FinSight parses, OCRs, chunks and indexes them into a **Qdrant** vector store.
- **Advanced chunking** — layout-aware + semantic + parent–child + Anthropic-style *contextual retrieval*, with table-aware handling for financial statements.
- **Hybrid retrieval + reranking** — vector search fused with full-text (BM25-like) search, then cross-encoder reranking.
- **Citations everywhere** — every claim is traceable to a document, page and region (deep-link to the file on Cloudinary).
- **Live financial research** — web search + financial APIs via MCP tools for companies not in your documents.
- **Async & concurrent** — long-running ingestion / research runs in background workers; you can keep chatting in the same conversation. Progress streams live over WebSocket.
- **Durable memory** — conversation state and long-term user memory persisted in **Postgres** via LangGraph's built-in checkpointer/store.
- **Observability** — full tracing and evaluation with LangSmith.

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design, agent roles, communication flows, RAG pipeline and data model.

```
React (Vite+TS)  ──REST/WS──►  FastAPI  ──►  LangGraph supervisor + agents
                                  │                    │ tools
                  Postgres (relational + memory)   MCP server (web/RAG/calc)
                  Qdrant (vectors) · Redis (cache/pubsub/queue)
                          ARQ workers (async ingestion & research)
                          Cloudinary (raw file storage)   LangSmith (tracing)
```

## 🧰 Tech Stack

| Layer | Tech |
|-------|------|
| Orchestration | LangGraph, LangChain |
| LLM / Embeddings | Google Gemini — chat (e.g. `gemini-2.0-flash`) + `gemini-embedding-2` (3072-d) |
| Vector store | Qdrant |
| Relational store | PostgreSQL |
| Tools protocol | Model Context Protocol (MCP) server |
| Cache / bus / queue | Redis, ARQ |
| Conversation memory | Postgres (LangGraph `PostgresSaver` + `PostgresStore`) |
| File storage | Cloudinary |
| API | FastAPI (RESTful) |
| Frontend | React + Vite + TypeScript |
| Observability | LangSmith |
| Quality | ruff, pytest |

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- (Local dev) Python 3.11+, Node 20+
- API keys: Google Gemini (free — https://aistudio.google.com/apikey), Cloudinary, LangSmith (optional)

### 1. Configure environment
```bash
cp .env.example .env
# edit .env and fill in your API keys
```

### 2. Run with Docker
```bash
docker compose up --build          # starts postgres, qdrant, redis, api, worker
docker compose exec api alembic upgrade head   # create the relational schema (first run)
```
- API:      http://localhost:8000  (docs at `/docs`)
- Qdrant:   http://localhost:6333/dashboard
- Frontend: http://localhost:5173

### 3. Local backend dev (without Docker)
```bash
cd backend
pip install -e ".[dev]"      # or: uv pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## 🔌 API Overview (RESTful)

| Method | Path | Description |
|--------|------|-------------|
| GET  | `/api/v1/health` | Liveness/readiness probe |
| POST | `/api/v1/conversations` | Create a conversation |
| POST | `/api/v1/conversations/{id}/messages` | Send a message (chat) |
| POST | `/api/v1/documents` | Upload a document → triggers async ingestion |
| GET  | `/api/v1/documents/{id}` | Ingestion status |
| POST | `/api/v1/conversations/{id}/tasks` | Launch a long-running task |
| GET  | `/api/v1/tasks/{id}` | Task status / result |
| WS   | `/api/v1/ws/conversations/{id}` | Stream tokens & task progress |

## 🧪 Quality

```bash
cd backend
ruff check .          # lint
ruff format .         # format
pytest                # tests
```

## 📁 Project Structure

```
backend/app/
├── api/            FastAPI routers (REST + WebSocket) — thin controllers
├── core/           config, logging, cache, DI
├── schemas/        Pydantic request/response DTOs
├── services/       business logic
├── repositories/   data access (Protocol + impl)  ← SOLID DIP
├── agents/         LangGraph graph, nodes, supervisor, state
├── tools/          tool implementations + MCP client adapter
├── rag/            ingestion · chunking · indexing · retrieval
├── skills/         reusable skill packages
├── workers/        ARQ background workers
└── models/         SQLAlchemy ORM
backend/mcp_server/  MCP server exposing tools
frontend/            React + Vite + TS
```

## 🗺️ Roadmap

- [x] M0 — Scaffold, config, Docker, lint/test baseline
- [x] M1 — RAG core (ingestion + Qdrant + hybrid retriever + cited QA)
- [x] M2 — Multi-agent graph (supervisor + agents) on LangGraph + Postgres checkpointer
- [ ] M3 — Tools via MCP server (live web/financial research)
- [x] M4 — Async tasks (ARQ + Redis pub/sub + WebSocket)  *(ingestion path)*
- [ ] M5 — React frontend
- [ ] M6 — Skills, caching, evals, polish & publish

## 📄 License

MIT
