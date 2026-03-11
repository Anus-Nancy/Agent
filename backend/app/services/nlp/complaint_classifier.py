from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "i",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "we",
    "with",
    "your",
}


@dataclass
class ClassificationResult:
    department: str
    confidence: float
    preprocessed_text: str
    scores: dict[str, float]


class ComplaintClassifier:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.department_keywords: dict[str, list[str]] = {}
        self.department_centroids: dict[str, np.ndarray] = {}

    def preprocess(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = [tok for tok in text.split() if tok and tok not in STOPWORDS]
        return " ".join(tokens)

    def _embed_texts(self, texts: Iterable[str]) -> np.ndarray:
        return self.model.encode(list(texts), normalize_embeddings=True)

    def train(self, department_keywords: dict[str, list[str]]) -> None:
        self.department_keywords = department_keywords
        self.department_centroids = {}

        for department, keywords in department_keywords.items():
            processed_keywords = [self.preprocess(keyword) for keyword in keywords]
            keyword_embeddings = self._embed_texts(processed_keywords)
            centroid = np.mean(keyword_embeddings, axis=0)
            centroid = centroid / np.linalg.norm(centroid)
            self.department_centroids[department] = centroid

    def classify(self, complaint_text: str) -> ClassificationResult:
        if not self.department_centroids:
            raise ValueError("Classifier is not trained. Call train() or load_artifacts() first.")

        preprocessed = self.preprocess(complaint_text)
        complaint_embedding = self._embed_texts([preprocessed])[0]

        scores = {
            department: float(np.dot(complaint_embedding, centroid))
            for department, centroid in self.department_centroids.items()
        }
        predicted_department = max(scores, key=scores.get)

        return ClassificationResult(
            department=predicted_department,
            confidence=scores[predicted_department],
            preprocessed_text=preprocessed,
            scores=scores,
        )

    def save_artifacts(self, output_dir: str) -> None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        metadata = {
            "model_name": self.model_name,
            "department_keywords": self.department_keywords,
            "departments": list(self.department_centroids.keys()),
        }
        (out / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        if self.department_centroids:
            matrix = np.stack([self.department_centroids[d] for d in metadata["departments"]])
            np.save(out / "department_centroids.npy", matrix)

    def load_artifacts(self, artifact_dir: str) -> None:
        src = Path(artifact_dir)
        metadata = json.loads((src / "metadata.json").read_text(encoding="utf-8"))

        self.model_name = metadata["model_name"]
        self.model = SentenceTransformer(self.model_name)

        self.department_keywords = metadata["department_keywords"]
        departments = metadata["departments"]
        matrix = np.load(src / "department_centroids.npy")
        self.department_centroids = {dept: matrix[i] for i, dept in enumerate(departments)}


def default_department_mapping() -> dict[str, list[str]]:
    return {
        "Fee Department": ["fee", "payment", "voucher", "tuition"],
        "Scholarship Department": ["scholarship", "funding", "financial support"],
        "Admissions Department": ["admission", "enrollment"],
        "IT Department": ["portal issue", "login problem", "system error"],
        "Student Support Department": ["document verification", "administrative support"],
    }
