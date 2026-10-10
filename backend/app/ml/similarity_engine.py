import logging
import numpy as np
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings

logger = logging.getLogger(__name__)

class SimilarityEngine:
    _instance: Optional['SimilarityEngine'] = None
    _model = None
    _is_model_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimilarityEngine, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        """Initializes the SentenceTransformers model with graceful fallback."""
        try:
            logger.info(f"Loading SentenceTransformer model: {settings.EMBEDDING_MODEL_NAME}...")
            from sentence_transformers import SentenceTransformer
            # Device: cpu or cuda
            device = "cuda" if settings.USE_GPU else "cpu"
            # The API must start even when this machine has no network access.
            # Use a cached model when available; the existing TF-IDF path below
            # remains the deterministic fallback when it is not.
            self._model = SentenceTransformer(
                settings.EMBEDDING_MODEL_NAME,
                device=device,
                local_files_only=True,
            )
            self._is_model_loaded = True
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({str(e)}). TF-IDF fallback will be utilized.")
            self._model = None
            self._is_model_loaded = False

    @property
    def is_model_loaded(self) -> bool:
        return self._is_model_loaded

    def compute_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """
        Computes cosine similarity (0.0 to 1.0) between two text representations.
        Uses SentenceTransformer dense embeddings first; falls back to TF-IDF if model is unavailable.
        """
        if not text_a or not text_b:
            return 0.0

        if self._is_model_loaded and self._model is not None:
            try:
                embeddings = self._model.encode([text_a, text_b], convert_to_numpy=True)
                emb_a = embeddings[0].reshape(1, -1)
                emb_b = embeddings[1].reshape(1, -1)
                sim = cosine_similarity(emb_a, emb_b)[0][0]
                # Bound between 0.0 and 1.0
                return float(max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim)))
            except Exception as e:
                logger.error(f"Error computing transformer embedding similarity: {e}. Falling back to TF-IDF.")

        # Robust TF-IDF cosine similarity fallback
        return self._compute_tfidf_similarity(text_a, text_b)

    def _compute_tfidf_similarity(self, text_a: str, text_b: str) -> float:
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
            tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(max(0.0, min(1.0, sim)))
        except Exception as e:
            logger.error(f"Error computing TF-IDF similarity: {e}")
            return 0.0

# Singleton instance
similarity_engine = SimilarityEngine()
