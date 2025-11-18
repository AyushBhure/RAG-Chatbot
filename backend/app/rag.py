"""Core RAG pipeline components."""

from __future__ import annotations

import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import mlflow
from fastapi import UploadFile
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
)
from langchain_community.document_loaders.base import BaseLoader
# Chroma import delayed to handle DLL errors gracefully
from langchain_core.language_models import BaseLanguageModel
from langchain_core.retrievers import BaseRetriever
from langchain_openai import ChatOpenAI
from langchain_community.llms.fake import FakeListLLM

from .config import Settings, get_settings
from .embeddings import EmbeddingFactory
from .logger import logger
from .models import AskResponse, SourceDocument


PROMPT_TEMPLATE = """You are an AI assistant that answers questions using the provided context.
Use only the information from the context. When you use a piece of context, cite it as [source:page].

Context:
{context}

Question: {question}

Answer in a concise paragraph followed by a bullet list of cited sources.
"""


class RAGPipeline:
    """Encapsulates ingestion, retrieval, and generation."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        embeddings = EmbeddingFactory(self.settings).build()
        
        # Initialize vector store - try Chroma first, fallback to FAISS if DLL errors
        vector_store_initialized = False
        try:
            # Try to import and use Chroma - this may fail if chromadb has DLL issues
            from langchain_community.vectorstores import Chroma
            self.vector_store = Chroma(
                collection_name="rag_documents",
                embedding_function=embeddings,
                persist_directory=str(self.settings.vector_store_dir),
            )
            logger.info("Using ChromaDB vector store")
            vector_store_initialized = True
        except Exception as e:
            # ChromaDB failed (DLL errors, import errors, etc.) - use simple in-memory fallback
            logger.warning(f"ChromaDB unavailable ({type(e).__name__}: {e}). Using InMemoryVectorStore fallback.")
            vector_store_initialized = False
        
        if not vector_store_initialized:
            # Fallback to simple in-memory vector store (no external deps)
            from langchain_core.vectorstores import VectorStore
            
            # Use the embeddings we already created (fake embeddings from fallback)
            
            # Create a simple in-memory vector store
            class SimpleMemoryStore(VectorStore):
                def __init__(self, embedding):
                    self.embedding = embedding
                    self._docs = []
                    self._embeddings_cache = []
                
                @classmethod
                def from_texts(cls, texts, embedding, metadatas=None, **kwargs):
                    """Required abstract method."""
                    store = cls(embedding)
                    from langchain.docstore.document import Document
                    docs = [Document(page_content=text, metadata=meta or {}) 
                            for text, meta in zip(texts, metadatas or [{}] * len(texts))]
                    store.add_documents(docs)
                    return store
                
                def similarity_search(self, query, k=4, **kwargs):
                    """Required abstract method."""
                    if not self._docs:
                        return []
                    # Simple: return first k documents
                    return self._docs[:k] if len(self._docs) >= k else self._docs
                
                def add_documents(self, documents):
                    self._docs.extend(documents)
                    # Generate embeddings
                    texts = [doc.page_content for doc in documents]
                    self._embeddings_cache.extend(self.embedding.embed_documents(texts))
                    return [str(i) for i in range(len(self._docs) - len(documents), len(self._docs))]
                
                def as_retriever(self, **kwargs):
                    from langchain_core.retrievers import BaseRetriever
                    
                    store = self  # Capture self for closure
                    search_kwargs = kwargs.get('search_kwargs', {})
                    k = search_kwargs.get('k', 4)
                    
                    class SimpleRetriever(BaseRetriever):
                        def _get_relevant_documents(self, query: str, *, run_manager=None):
                            if not store._docs:
                                return []
                            # Simple retrieval: return top_k documents
                            return store._docs[:k] if len(store._docs) >= k else store._docs
                    
                    return SimpleRetriever()
                
                def persist(self):
                    pass  # No-op for in-memory
            
            self.vector_store = SimpleMemoryStore(embeddings)
            logger.info("Using SimpleMemoryStore as fallback")
        
        self.retriever: BaseRetriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.settings.top_k}
        )
        self.llm = self._build_llm()
        self.qa_chain = self._build_chain()

    def _build_llm(self) -> BaseLanguageModel:
        if self.settings.environment == "test" or self.settings.llm.provider == "mock":
            return FakeListLLM(responses=["Mock answer with citations from your documents."])

        if not self.settings.openai_api_key:
            logger.warning("OPENAI_API_KEY not set, using mock LLM")
            return FakeListLLM(responses=["Mock answer with citations from your documents."])

        return ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model_name=self.settings.llm.model_name,
            temperature=self.settings.llm.temperature,
            max_tokens=self.settings.llm.max_tokens,
        )

    def _build_chain(self) -> RetrievalQA:
        prompt = PromptTemplate(
            input_variables=["context", "question"], template=PROMPT_TEMPLATE
        )
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )

    # --------------------------------------------------------------------- ingestion
    def ingest_files(self, files: Iterable[UploadFile]) -> int:
        """Ingest uploaded files into the vector store."""

        documents: List[Document] = []
        for file in files:
            loader = self._loader_from_upload(file)
            docs = loader.load()
            documents.extend(docs)
            logger.info("Loaded %s with %d pages/chunks", file.filename, len(docs))

        if not documents:
            return 0

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        split_docs = splitter.split_documents(documents)
        self.vector_store.add_documents(split_docs)
        self.vector_store.persist()
        logger.info("Persisted %d chunks to vector store", len(split_docs))
        return len(split_docs)

    def _loader_from_upload(self, upload: UploadFile) -> BaseLoader:
        suffix = Path(upload.filename or "").suffix.lower()
        tmp_dir = Path(tempfile.mkdtemp())
        tmp_path = tmp_dir / (upload.filename or "upload")
        
        # Read file content
        content = upload.file.read()
        tmp_path.write_bytes(content)
        # Reset file pointer for potential reuse
        if hasattr(upload.file, 'seek'):
            upload.file.seek(0)

        if suffix == ".pdf":
            try:
                return PyPDFLoader(str(tmp_path))
            except ImportError:
                raise ValueError(
                    "PDF support requires 'pypdf' package. "
                    "Install it with: pip install pypdf"
                )
        if suffix in {".txt", ".md"}:
            return TextLoader(str(tmp_path), autodetect_encoding=True)

        tmp_path.unlink(missing_ok=True)
        raise ValueError("Unsupported file type. Only PDF and TXT are allowed.")

    # --------------------------------------------------------------------- querying
    def ask(self, query: str, top_k: int | None = None) -> AskResponse:
        """Run the full retrieval and generation pipeline."""

        start = time.perf_counter()
        k = top_k or self.settings.top_k
        # Update retriever k if it supports search_kwargs (ChromaDB), otherwise use default
        if hasattr(self.retriever, 'search_kwargs'):
            self.retriever.search_kwargs["k"] = k

        result = self.qa_chain.invoke({"query": query})
        latency_ms = (time.perf_counter() - start) * 1000
        sources = self._format_sources(result.get("source_documents", []))
        answer = result.get("result", "No answer generated.")

        response = AskResponse(
            answer=answer,
            sources=sources,
            used_model=self.settings.llm.model_name,
            latency_ms=latency_ms,
            created_at=datetime.utcnow(),
        )

        if self.settings.enable_mlflow:
            self._log_mlflow(query, response)

        return response

    def _format_sources(self, documents: List[Document]) -> List[SourceDocument]:
        formatted: List[SourceDocument] = []
        for doc in documents:
            metadata = doc.metadata or {}
            formatted.append(
                SourceDocument(
                    source=str(metadata.get("source", "unknown")),
                    page=metadata.get("page"),
                    score=metadata.get("score"),
                    content_preview=doc.page_content[:200] + "...",
                )
            )
        return formatted

    def _log_mlflow(self, query: str, response: AskResponse) -> None:
        """Log query and response to MLflow, gracefully handle errors."""
        if not self.settings.enable_mlflow:
            return
        
        try:
            mlflow.set_tracking_uri(self.settings.mlflow_tracking_uri)
            with mlflow.start_run(run_name="rag_query", nested=True):
                mlflow.log_params(
                    {
                        "top_k": len(response.sources),
                        "model": response.used_model,
                    }
                )
                mlflow.log_metrics({"latency_ms": response.latency_ms})
                mlflow.log_dict(
                    {
                        "query": query,
                        "answer": response.answer,
                        "sources": [source.model_dump() for source in response.sources],
                    },
                    artifact_file="response.json",
                )
        except Exception as e:
            logger.warning(f"MLflow logging failed: {e}. Continuing without logging.")

