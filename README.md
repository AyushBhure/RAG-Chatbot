# RAG Chatbot

End-to-end Retrieval-Augmented Generation (RAG) chatbot for querying private PDF/TXT documents. Built with FastAPI, LangChain, and React.

**Live Demo:** https://rag-chatbot-six-gules.vercel.app

## Features

- Document ingestion with chunking, embeddings, and vector storage
- GPT-4 powered answers with source citations via LangChain RetrievalQA
- FastAPI backend with `/upload`, `/ask`, `/health` endpoints
- React chat UI with document uploader
- Automatic fallbacks for Windows compatibility
- MLflow tracking (optional, disabled by default)
- Pytest test suite
- Dockerized backend/frontend with docker-compose
- Vercel deployment ready

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
├── api/                     # Vercel serverless entrypoint
├── docker-compose.yml
└── vercel.json
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & docker-compose (optional)
- OpenAI API key (optional - app works with mock LLM for testing)

## Environment Variables

### Backend

Create `backend/.env`:
```
OPENAI_API_KEY=sk-your-key  # Optional - app works with mock LLM if not set
ENVIRONMENT=dev
LLM__PROVIDER=openai  # or "mock" for testing
LLM__MODEL_NAME=gpt-4o-mini
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K=4
ENABLE_MLFLOW=false  # Set to true to enable MLflow tracking
```

### Frontend

Create `frontend/.env` for local development:
```
VITE_API_BASE=http://localhost:8000
```

Note: For Vercel deployment, this defaults to `/api` automatically.

## Installation

### Backend Setup

```bash
cd backend
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will automatically:
- Use fake embeddings if PyTorch/transformers fail (Windows DLL issues)
- Fall back to in-memory vector store if ChromaDB fails
- Use mock LLM if `OPENAI_API_KEY` is not set

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and connects to the backend at `http://localhost:8000`.

### Docker Compose

```bash
docker-compose up --build
```

Backend listens on `http://localhost:8000`, frontend on `http://localhost:5173`.

## Usage

1. Upload PDF/TXT files via frontend or `POST /upload`
2. Ask questions via frontend chat or `POST /ask` with `{"query": "..."}`
3. Responses include contextual answers and cited sources

Example API call:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize the uploaded docs"}'
```

## API Endpoints

- `POST /upload` - Upload PDF/TXT files (multipart/form-data)
- `POST /ask` - Ask a question (JSON: `{"query": "your question"}`)
- `GET /health` - Health check endpoint

## Testing

Run the test suite:
```bash
cd backend
pytest
```

Sample data: Upload `data/sample_docs/rag_intro.txt` and query "What is Retrieval Augmented Generation?"

## Deployment

### Vercel

1. Install Vercel CLI and log in:
   ```bash
   npm i -g vercel
   vercel login
   ```

2. Set environment variables via Vercel dashboard or CLI:
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add VECTOR_STORE_DIR /tmp/vectorstore
   vercel env add MLFLOW_TRACKING_URI /tmp/mlflow
   ```

3. Deploy:
   ```bash
   vercel --prod
   ```

4. Add custom domain (optional):
   - Go to Vercel Dashboard → Project Settings → Domains
   - Add your domain and follow DNS configuration instructions
   - SSL certificate is automatically provisioned

### Other Platforms

- **Azure App Service**: Build Docker images and push to Azure Container Registry
- **Render / Railway**: Deploy backend container with `OPENAI_API_KEY` secret; deploy frontend as static site
- **Note**: Vercel's filesystem is ephemeral. For production persistence, use Pinecone or another managed vector DB.

## MLflow Tracking

MLflow is disabled by default. To enable:

1. Set `ENABLE_MLFLOW=true` in `backend/.env`
2. Set `MLFLOW_TRACKING_URI` to a valid file:// URI or remote server
3. Launch the UI:
   ```bash
   mlflow ui --backend-store-uri file:///path/to/mlflow --port 5001
   ```

Note: On Windows, use proper `file://` URI format or disable MLflow for testing.

## Current Status

**Working Features:**
- Document upload (PDF/TXT)
- Document chunking and storage
- Question answering with RAG pipeline
- React chat UI
- Automatic fallbacks for compatibility

**Current Configuration:**
- Embeddings: Uses fake embeddings (fallback due to Windows PyTorch DLL issues)
- Vector Store: Uses SimpleMemoryStore (fallback due to ChromaDB/onnxruntime issues)
- LLM: Uses mock LLM by default (set `OPENAI_API_KEY` for real GPT-4)

**To Enable Full Features:**
1. Set `OPENAI_API_KEY` and `LLM__PROVIDER=openai` for real GPT-4 responses
2. Fix PyTorch installation for real embeddings (or use OpenAI embeddings)
3. Install `onnxruntime` for ChromaDB (or switch to Pinecone)

## Extending

- Swap ChromaDB with Pinecone by replacing the vector store instantiation in `rag.py`
- Enable real embeddings by fixing PyTorch or using OpenAI embeddings
- Integrate scheduled ingest pipelines (Airflow), monitoring (Prometheus), or auth (OAuth/JWT) as needed

## License

MIT
