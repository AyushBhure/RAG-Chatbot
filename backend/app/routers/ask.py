"""Question answering endpoint."""

from fastapi import APIRouter, Depends

from ..models import AskRequest, AskResponse
from ..rag import RAGPipeline

router = APIRouter(prefix="/ask", tags=["qa"])


def get_pipeline() -> RAGPipeline:
    return RAGPipeline()


@router.post("", response_model=AskResponse)
async def ask_question(
    request: AskRequest, pipeline: RAGPipeline = Depends(get_pipeline)
) -> AskResponse:
    return pipeline.ask(query=request.query, top_k=request.top_k)

