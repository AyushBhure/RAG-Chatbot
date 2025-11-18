# RAG Chatbot

End-to-end Retrieval-Augmented Generation (RAG) chatbot for querying private PDF/TXT documents with FastAPI, LangChain, ChromaDB, Sentence-Transformers, React, and MLflow.

## Features
- Document ingestion with chunking, embeddings, and persistent Chroma vector store
- GPT-4 (or compatible) powered answers with citations via LangChain RetrievalQA
- FastAPI backend with `/upload`, `/ask`, `/health` endpoints
- React chat UI with document uploader
- MLflow tracking for queries
- Pytest test suite
- Dockerized backend/frontend and `docker-compose` orchestration

## Project Structure
```
rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entrypoint
│   │   ├── rag.py           # LangChain RAG pipeline
│   │   ├── embeddings.py    # Embedding factory
│   │   ├── config.py        # Settings & env management
│   │   └── routers/         # API routers
│   ├── tests/               # Pytest suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/                 # React chat app
│   ├── package.json
│   └── Dockerfile
├── vectorstore/             # Chroma persistence
├── mlflow/                  # Local MLflow tracking dir
├── docker-compose.yml
└── README.md
```

## Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & docker-compose (for containerized deployment)
- OpenAI API key (or adjust `config.py` to plug in another LLM)

## Environment Variables
Create `.env` in project root:
```
OPENAI_API_KEY=sk-your-key
ENVIRONMENT=dev
LLM__MODEL_NAME=gpt-4o-mini
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K=4
MLFLOW_TRACKING_URI=mlflow
```

## Backend Setup
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests:
```bash
pytest
```

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Set `VITE_API_BASE=http://localhost:8000` in `.env` to point to backend.

## Docker Compose
```bash
docker-compose up --build
```
Backend listens on `http://localhost:8000`, frontend on `http://localhost:5173`.

## Deploy on Vercel
1. Install the Vercel CLI and log in:
   ```bash
   npm i -g vercel
   vercel login
   ```
2. In project root, set required environment variables for the backend (OpenAI key, optional Pinecone, etc.) via the Vercel dashboard or CLI:
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add VECTOR_STORE_DIR /tmp/vectorstore
   vercel env add MLFLOW_TRACKING_URI /tmp/mlflow
   ```
   (Use `/tmp` paths because Vercel’s filesystem is ephemeral; for production persistence swap to Pinecone or another managed vector DB.)
3. Deploy:
   ```bash
   vercel --prod
   ```
   The frontend builds from `frontend/` via Vite and serves at the project root; the FastAPI backend is exposed under `/api/*` using the serverless entrypoint at `backend/api/index.py`.
4. In the frontend, `VITE_API_BASE` defaults to `/api`, so no additional configuration is needed.

## Usage
1. Upload PDF/TXT files via frontend or `POST /upload`.
2. Ask questions via frontend chat or `POST /ask` with `{"query": "..."}`.
3. Responses include contextual answers and cited sources.

Example curl:
```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"query": "Summarize the uploaded docs"}'
```

## MLflow Tracking
Runs are stored in `mlflow/`. Launch the UI:
```bash
mlflow ui --backend-store-uri mlflow --port 5001
```

## Deployment
- **Azure App Service**: Build Docker images and push to Azure Container Registry, then configure Web App for Containers with backend/frontend images.
- **Render / Railway**: Deploy backend container with `OPENAI_API_KEY` secret; deploy frontend as static site pointing to backend URL.
- Ensure persistent storage for `vectorstore/` (Azure Files, Render persistent disk, etc.) or switch to managed vector DB (Pinecone) by editing `rag.py`.

## Sample Data & Tests
- `data/sample_docs/rag_intro.txt` can be uploaded to verify the pipeline.
- Example query: "What is Retrieval Augmented Generation?"

## Extending
- Swap Chroma with Pinecone by replacing the vector store instantiation in `rag.py`.
- Integrate scheduled ingest pipelines (Airflow), monitoring (Prometheus), or auth (OAuth/JWT) as needed.

