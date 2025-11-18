"""Embedding utilities."""

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.base import Embeddings
from langchain_community.embeddings import FakeEmbeddings

from .config import Settings, get_settings


class EmbeddingFactory:
    """Factory to instantiate embeddings."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def build(self) -> Embeddings:
        """Return an embedding function."""

        if self.settings.environment == "test":
            return FakeEmbeddings(size=768)

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

