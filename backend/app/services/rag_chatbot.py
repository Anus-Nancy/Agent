from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from transformers import pipeline

from app.core.config import settings
from app.models.complaint import Complaint, ComplaintStatus
from app.models.knowledge_base import KnowledgeBaseEntry
from app.models.query_log import QueryLog


class RAGChatbotService:
    def __init__(self) -> None:
        self.embedder = SentenceTransformer(settings.sentence_transformer_model)
        self.dimension = self.embedder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata: dict[int, dict[str, str | int]] = {}
        self._next_vector_id = 0
        self._generator = None
        self._load_index()

    def _embed(self, text: str) -> np.ndarray:
        return self.embedder.encode([text], normalize_embeddings=True).astype("float32")

    def _ensure_dirs(self) -> None:
        Path(settings.kb_faiss_index_path).parent.mkdir(parents=True, exist_ok=True)

    def _save_index(self) -> None:
        self._ensure_dirs()
        faiss.write_index(self.index, settings.kb_faiss_index_path)
        Path(settings.kb_faiss_metadata_path).write_text(
            json.dumps({"next_vector_id": self._next_vector_id, "metadata": self.metadata}, indent=2),
            encoding="utf-8",
        )

    def _load_index(self) -> None:
        index_path = Path(settings.kb_faiss_index_path)
        meta_path = Path(settings.kb_faiss_metadata_path)
        if index_path.exists() and meta_path.exists():
            self.index = faiss.read_index(str(index_path))
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            self._next_vector_id = int(payload.get("next_vector_id", 0))
            self.metadata = {int(k): v for k, v in payload.get("metadata", {}).items()}

    def _get_generator(self):
        if self._generator is None:
            self._generator = pipeline(
                "text2text-generation",
                model=settings.llm_model_name,
                tokenizer=settings.llm_model_name,
                max_new_tokens=220,
            )
        return self._generator

    def add_knowledge_entry(self, entry_id: int, title: str, content: str, source_type: str) -> None:
        vector = self._embed(content)
        self.index.add(vector)
        self.metadata[self._next_vector_id] = {
            "entry_id": entry_id,
            "title": title,
            "content": content,
            "source_type": source_type,
        }
        self._next_vector_id += 1
        self._save_index()

    def rebuild_index(self, db: Session) -> None:
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = {}
        self._next_vector_id = 0

        entries = db.query(KnowledgeBaseEntry).order_by(KnowledgeBaseEntry.id.asc()).all()
        for entry in entries:
            self.add_knowledge_entry(entry.id, entry.title, entry.content, entry.source_type)

    def sync_knowledge_base(self, db: Session) -> None:
        self._sync_solved_complaints(db)
        self._sync_common_queries(db)
        self._sync_policy_documents(db)
        self.rebuild_index(db)

    def _upsert_entry(self, db: Session, source_type: str, source_id: str, title: str, content: str) -> None:
        existing = (
            db.query(KnowledgeBaseEntry)
            .filter(KnowledgeBaseEntry.source_type == source_type, KnowledgeBaseEntry.source_id == source_id)
            .first()
        )
        if existing:
            existing.title = title
            existing.content = content
        else:
            db.add(
                KnowledgeBaseEntry(
                    source_type=source_type,
                    source_id=source_id,
                    title=title,
                    content=content,
                )
            )

    def _sync_solved_complaints(self, db: Session) -> None:
        solved = (
            db.query(Complaint)
            .filter(Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]))
            .order_by(Complaint.id.asc())
            .all()
        )
        for complaint in solved:
            text = f"Complaint: {complaint.title}\nDetails: {complaint.description}\nStatus: {complaint.status.value}"
            self._upsert_entry(
                db,
                source_type="solved_complaint",
                source_id=str(complaint.id),
                title=f"Solved Complaint #{complaint.id}: {complaint.title}",
                content=text,
            )

    def _sync_common_queries(self, db: Session) -> None:
        answered = db.query(QueryLog).filter(QueryLog.answer_text.isnot(None)).order_by(QueryLog.id.asc()).all()
        for query in answered:
            text = f"Question: {query.query_text}\nAnswer: {query.answer_text}"
            self._upsert_entry(
                db,
                source_type="common_query",
                source_id=str(query.id),
                title=f"Common Query #{query.id}",
                content=text,
            )

    def _sync_policy_documents(self, db: Session) -> None:
        policy_dir = Path(settings.policy_docs_path)
        policy_dir.mkdir(parents=True, exist_ok=True)
        for file_path in policy_dir.glob("*.md"):
            content = file_path.read_text(encoding="utf-8").strip()
            if not content:
                continue
            self._upsert_entry(
                db,
                source_type="policy_document",
                source_id=file_path.name,
                title=f"Policy: {file_path.stem.replace('_', ' ').title()}",
                content=content,
            )

    def retrieve(self, question: str, top_k: int = 3) -> list[dict[str, str | int | float]]:
        if self.index.ntotal == 0:
            return []

        query_vector = self._embed(question)
        scores, indices = self.index.search(query_vector, top_k)

        contexts = []
        for idx, score in zip(indices[0], scores[0]):
            idx = int(idx)
            if idx < 0:
                continue
            meta = self.metadata.get(idx)
            if not meta:
                continue
            contexts.append(
                {
                    "id": int(meta["entry_id"]),
                    "title": str(meta["title"]),
                    "source_type": str(meta["source_type"]),
                    "content": str(meta["content"]),
                    "score": float(score),
                }
            )
        return contexts

    def generate_answer(self, question: str, contexts: list[dict[str, str | int | float]]) -> str:
        if not contexts:
            return "I could not find relevant information in the knowledge base. Your query has been forwarded to student support."

        context_text = "\n\n".join(
            [f"[{c['source_type']}] {c['title']}:\n{c['content']}" for c in contexts]
        )
        prompt = (
            "You are the TCF student support assistant. "
            "Answer the student's question using only the provided context. "
            "If unsure, clearly say so and suggest contacting support.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{context_text}\n\n"
            "Final Answer:"
        )

        try:
            generator = self._get_generator()
            result = generator(prompt)
            if result and isinstance(result, list):
                text = result[0].get("generated_text", "").strip()
                if text:
                    return text
        except Exception:
            pass

        return f"Based on TCF records: {contexts[0]['content'][:500]}"


rag_chatbot_service = RAGChatbotService()
