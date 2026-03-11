from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.query_log import QueryLog


class QuerySimilarityService:
    def __init__(self) -> None:
        self.model = SentenceTransformer(settings.sentence_transformer_model)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata: dict[int, dict[str, str | int]] = {}
        self._next_vector_id = 0
        self._load()

    def _embed(self, text: str) -> np.ndarray:
        emb = self.model.encode([text], normalize_embeddings=True)
        return emb.astype("float32")

    def _ensure_parent(self) -> None:
        Path(settings.faiss_index_path).parent.mkdir(parents=True, exist_ok=True)

    def _save(self) -> None:
        self._ensure_parent()
        faiss.write_index(self.index, settings.faiss_index_path)
        Path(settings.faiss_metadata_path).write_text(
            json.dumps(
                {
                    "next_vector_id": self._next_vector_id,
                    "metadata": self.metadata,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def _load(self) -> None:
        index_path = Path(settings.faiss_index_path)
        meta_path = Path(settings.faiss_metadata_path)
        if index_path.exists() and meta_path.exists():
            self.index = faiss.read_index(str(index_path))
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            self._next_vector_id = int(payload.get("next_vector_id", 0))
            self.metadata = {int(k): v for k, v in payload.get("metadata", {}).items()}

    def add_answered_query(self, query_id: int, query_text: str, answer_text: str) -> None:
        vector = self._embed(query_text)
        self.index.add(vector)
        self.metadata[self._next_vector_id] = {
            "query_id": query_id,
            "query_text": query_text,
            "answer_text": answer_text,
        }
        self._next_vector_id += 1
        self._save()

    def find_similar_answer(self, query_text: str, threshold: float) -> str | None:
        if self.index.ntotal == 0:
            return None

        vector = self._embed(query_text)
        scores, indices = self.index.search(vector, 1)
        best_score = float(scores[0][0])
        best_idx = int(indices[0][0])

        if best_idx < 0 or best_score < threshold:
            return None
        hit = self.metadata.get(best_idx)
        if not hit:
            return None
        return str(hit["answer_text"])

    def rebuild_from_database(self, db: Session) -> None:
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = {}
        self._next_vector_id = 0

        answered_queries = (
            db.query(QueryLog)
            .filter(QueryLog.answer_text.isnot(None))
            .order_by(QueryLog.id.asc())
            .all()
        )
        for item in answered_queries:
            self.add_answered_query(item.id, item.query_text, item.answer_text or "")


query_similarity_service = QuerySimilarityService()
