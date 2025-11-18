# RAG Chatbot

End-to-end Retrieval-Augmented Generation (RAG) chatbot for querying private PDF/TXT documents with FastAPI, LangChain, React, and optional MLflow tracking.

## Features
- Document ingestion with chunking, embeddings, and vector storage (ChromaDB with fallback to in-memory store)
- GPT-4 (or mock LLM for testing) powered answers with citations via LangChain RetrievalQA
- FastAPI backend with `/upload`, `/ask`, `/health` endpoints
- React chat UI with document uploader
- Automatic fallbacks for Windows compatibility (fake embeddings, in-memory vector store)
- MLflow tracking (optional, disabled by default)
- Pytest test suite
- Dockerized backend/frontend and `docker-compose` orchestration
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
├── vectorstore/             # Chroma persistence
├── mlflow/                  # Local MLflow tracking dir
├── docker-compose.yml
└── README.md
```

## Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & docker-compose (for containerized deployment)
- OpenAI API key (optional - app works with mock LLM for testing)

## Environment Variables

### Backend (create `backend/.env`):
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

### Frontend (create `frontend/.env` for local development):
```
VITE_API_BASE=http://localhost:8000
```
Note: For Vercel deployment, this defaults to `/api` automatically.

## Backend Setup
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

For local development, create `frontend/.env`:
```
VITE_API_BASE=http://localhost:8000
```

The frontend will run on `http://localhost:5173` and connect to the backend.

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
5. Add a custom domain (optional):
   ```bash
   vercel domains add <your-domain.com>
   vercel alias <deployment-url> <your-domain.com>
   ```
   Update DNS records per Vercel’s instructions. Once propagated, your domain will serve the React UI while `/api/*` continues to proxy to FastAPI.

## Usage
1. Upload PDF/TXT files via frontend or `POST /upload`.
2. Ask questions via frontend chat or `POST /ask` with `{"query": "..."}`.
3. Responses include contextual answers and cited sources.

Example curl:
```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"query": "Summarize the uploaded docs"}'
```

## MLflow Tracking (Optional)
MLflow is **disabled by default** for easier testing. To enable:

1. Set `ENABLE_MLFLOW=true` in `backend/.env`
2. Set `MLFLOW_TRACKING_URI` to a valid file:// URI or remote server
3. Launch the UI:
   ```bash
   mlflow ui --backend-store-uri file:///path/to/mlflow --port 5001
   ```

Note: On Windows, use proper `file://` URI format or disable MLflow for testing.

## Deployment

### Vercel (Recommended)
The project is configured for Vercel deployment with:
- FastAPI backend as serverless functions (`backend/api/index.py`)
- React frontend as static site
- Automatic routing via `vercel.json`

See "Deploy on Vercel" section above for detailed steps.

### Other Platforms
- **Azure App Service**: Build Docker images and push to Azure Container Registry, then configure Web App for Containers with backend/frontend images.
- **Render / Railway**: Deploy backend container with `OPENAI_API_KEY` secret; deploy frontend as static site pointing to backend URL.
- **Important**: Vercel's filesystem is ephemeral. For production persistence, switch to managed vector DB (Pinecone) by editing `rag.py` or use persistent storage on other platforms.

## Sample Data & Tests
- `data/sample_docs/rag_intro.txt` can be uploaded to verify the pipeline.
- Example query: "What is Retrieval Augmented Generation?"

## Current Status & Notes

### Working Features ✅
- ✅ Document upload (PDF/TXT)
- ✅ Document chunking and storage
- ✅ Question answering with RAG pipeline
- ✅ React chat UI
- ✅ Automatic fallbacks for compatibility

### Current Configuration
- **Embeddings**: Uses fake embeddings (fallback due to Windows PyTorch DLL issues)
- **Vector Store**: Uses SimpleMemoryStore (fallback due to ChromaDB/onnxruntime issues)
- **LLM**: Uses mock LLM by default (set `OPENAI_API_KEY` for real GPT-4)

### To Enable Full Features
1. **Real Embeddings**: Fix PyTorch installation or use OpenAI embeddings
2. **ChromaDB**: Install `onnxruntime` or use Pinecone
3. **Real LLM**: Set `OPENAI_API_KEY` and `LLM__PROVIDER=openai`

## Extending
- Swap Chroma with Pinecone by replacing the vector store instantiation in `rag.py`.
- Enable real embeddings by fixing PyTorch or using OpenAI embeddings.
- Integrate scheduled ingest pipelines (Airflow), monitoring (Prometheus), or auth (OAuth/JWT) as needed.

