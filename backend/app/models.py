"""Pydantic schemas for API endpoints."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response after documents are ingested."""

    documents_ingested: int = Field(..., ge=0)
    detail: str


class AskRequest(BaseModel):
    """User question payload."""

    query: str = Field(..., min_length=3)
    top_k: int | None = Field(None, ge=1, le=10)


class SourceDocument(BaseModel):
    """Metadata for retrieved document chunks."""

    source: str
    page: int | None = None
    score: float | None = None
    content_preview: str


class AskResponse(BaseModel):
    """Response payload for generated answers."""

    answer: str
    sources: List[SourceDocument]
    used_model: str
    latency_ms: float
    created_at: datetime

