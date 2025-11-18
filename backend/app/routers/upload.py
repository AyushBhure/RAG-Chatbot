"""Document upload endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..models import UploadResponse
from ..rag import RAGPipeline
from ..logger import logger

router = APIRouter(prefix="/upload", tags=["documents"])


def get_pipeline() -> RAGPipeline:
    return RAGPipeline()


@router.post("", response_model=UploadResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    pipeline: RAGPipeline = Depends(get_pipeline),
) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    try:
        chunks = pipeline.ingest_files(files)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        import traceback
        error_msg = f"Upload error: {exc}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(exc)}") from exc

    return UploadResponse(
        documents_ingested=chunks,
        detail=f"Ingested {chunks} chunks from {len(files)} files.",
    )

