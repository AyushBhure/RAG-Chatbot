# RAG Chatbot 🚀

A smart document chatbot that actually understands your PDFs and text files. Upload your documents, ask questions, and get answers with source citations. Built with FastAPI, LangChain, and React.

🌐 **Try it live:** https://rag-chatbot-six-gules.vercel.app

## What It Does

Ever wish you could just ask questions about your documents instead of scrolling through pages? That's what this does. Upload PDFs or text files, and the chatbot uses RAG (Retrieval-Augmented Generation) to find relevant chunks and generate accurate answers with citations.

## Key Features

- 📄 **Document Upload**: Drag and drop PDFs or text files
- 🔍 **Smart Search**: Vector embeddings find the most relevant document chunks
- 💬 **Chat Interface**: Clean, ChatGPT-like UI for asking questions
- 📚 **Source Citations**: Every answer shows which documents and pages it came from
- 🛡️ **Automatic Fallbacks**: Works even if some dependencies fail (Windows-friendly!)
- 🐳 **Docker Ready**: One command to run everything locally
- ☁️ **Vercel Deployed**: Already live and ready to use

## Quick Start

### Prerequisites

- Python 3.11+ 
- Node.js 18+
- Docker (optional, for containerized setup)

### Local Development

**Backend:**
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and connects to the backend at `http://localhost:8000`.

### Docker (Easiest Way)

```bash
docker-compose up --build
```

That's it! Backend on port 8000, frontend on port 5173.

## Configuration

### Backend Environment Variables

Create `backend/.env`:
```env
OPENAI_API_KEY=sk-your-key-here  # Optional - works without it for testing
ENVIRONMENT=dev
LLM__PROVIDER=openai  # or "mock" for testing
LLM__MODEL_NAME=gpt-4o-mini
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K=4
ENABLE_MLFLOW=false
```

**Note:** The app is smart about fallbacks. If you don't set `OPENAI_API_KEY`, it uses a mock LLM. If PyTorch fails (common on Windows), it uses fake embeddings. If ChromaDB fails, it falls back to in-memory storage. Everything still works!

### Frontend Environment Variables

For local development, create `frontend/.env`:
```env
VITE_API_BASE=http://localhost:8000
```

On Vercel, this defaults to `/api` automatically - no config needed.

## How It Works

1. **Upload**: Documents are chunked into smaller pieces (800 chars with 100 char overlap)
2. **Embed**: Each chunk gets converted to a vector embedding
3. **Store**: Embeddings are stored in a vector database (ChromaDB or in-memory fallback)
4. **Query**: When you ask a question, it finds the most similar chunks
5. **Generate**: An LLM (GPT-4 or mock) generates an answer using those chunks
6. **Cite**: Sources are included so you know where the answer came from

## API Endpoints

- `POST /upload` - Upload PDF/TXT files
- `POST /ask` - Ask a question: `{"query": "your question"}`
- `GET /health` - Check if the API is running

Example:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```

## Deployment

### Vercel (Already Deployed!)

The app is already live at https://rag-chatbot-six-gules.vercel.app

To deploy your own version:

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   vercel login
   ```

2. **Set environment variables** (via dashboard or CLI):
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add VECTOR_STORE_DIR /tmp/vectorstore
   vercel env add MLFLOW_TRACKING_URI /tmp/mlflow
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

4. **Add custom domain** (optional):
   - Go to Vercel Dashboard → Your Project → Settings → Domains
   - Add your domain and follow DNS setup instructions
   - SSL is automatic!

### Other Platforms

- **Azure/Render/Railway**: Deploy the Docker containers with your `OPENAI_API_KEY` set
- **Important**: Vercel's filesystem is temporary. For production, consider using Pinecone or another managed vector DB for persistence.

## Testing

Run the test suite:
```bash
cd backend
pytest
```

Try uploading `data/sample_docs/rag_intro.txt` and asking "What is Retrieval Augmented Generation?"

## Project Structure

```
rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── rag.py           # RAG pipeline logic
│   │   ├── embeddings.py    # Embedding factory
│   │   ├── config.py        # Settings
│   │   └── routers/         # API endpoints
│   ├── tests/               # Test suite
│   └── requirements.txt
├── frontend/
│   ├── src/                 # React components
│   └── package.json
├── api/                     # Vercel serverless entrypoint
├── docker-compose.yml
└── vercel.json
```

## Current Status

✅ **Working:**
- Document upload and processing
- Vector search and retrieval
- Question answering with citations
- Professional chat UI
- Automatic fallbacks for compatibility

🔧 **Current Setup:**
- Using fake embeddings (fallback mode)
- Using in-memory vector store (fallback mode)
- Using mock LLM by default

**To enable full features:**
1. Set `OPENAI_API_KEY` for real GPT-4 responses
2. Fix PyTorch installation for real embeddings (or use OpenAI embeddings)
3. Install `onnxruntime` for ChromaDB (or switch to Pinecone)

## MLflow Tracking (Optional)

Disabled by default. To enable:

1. Set `ENABLE_MLFLOW=true` in `backend/.env`
2. Set `MLFLOW_TRACKING_URI` to a file:// path or remote server
3. Run: `mlflow ui --backend-store-uri file:///path/to/mlflow --port 5001`

## Extending the Project

- **Swap vector stores**: Replace ChromaDB with Pinecone in `rag.py`
- **Add auth**: Integrate OAuth/JWT for user authentication
- **Monitoring**: Add Prometheus metrics or logging services
- **Scheduling**: Use Airflow for scheduled document ingestion

## Contributing

Found a bug? Want to add a feature? Pull requests welcome!

## License

MIT

---

Built with ❤️ using FastAPI, LangChain, React, and lots of coffee.
