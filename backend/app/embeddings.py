"""Embedding utilities."""

import logging
from langchain.embeddings.base import Embeddings
from langchain_community.embeddings import FakeEmbeddings

from .config import Settings, get_settings

logger = logging.getLogger(__name__)


class EmbeddingFactory:
    """Factory to instantiate embeddings."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def build(self) -> Embeddings:
        """Return an embedding function."""

        if self.settings.environment == "test":
            logger.info("Using fake embeddings for test environment")
            return FakeEmbeddings(size=768)

        # Try to use HuggingFace embeddings, fallback to fake if PyTorch fails
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings

            model_kwargs = {"device": "cpu"}
            encode_kwargs = {"normalize_embeddings": True}

            return HuggingFaceEmbeddings(
                model_name=self.settings.embedding_model_name,
                cache_folder=str(self.settings.embedding_cache_dir)
                if self.settings.embedding_cache_dir
                else None,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs,
            )
        except (OSError, ImportError, Exception) as e:
            logger.warning(
                f"Failed to load HuggingFace embeddings (PyTorch issue?): {e}. "
                "Falling back to fake embeddings."
            )
            return FakeEmbeddings(size=768)

