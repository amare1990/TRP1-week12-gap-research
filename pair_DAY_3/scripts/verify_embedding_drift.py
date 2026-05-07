

## data-contract-enforcer/scripts/verify_embedding_drift.py

"""
Verify embedding-drift risk for the Week 7 Data Contract Enforcer.

Purpose:
    Demonstrate why absolute cosine-similarity thresholds should be
    recalibrated after post-training or checkpoint changes.

Usage:
    uv run python scripts/verify_embedding_drift.py


Optional:
    uv add torch transformers scikit-learn numpy
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np


SCHEMAS = [
    "user_id INT, email VARCHAR, created_at TIMESTAMP",
    "user_id INT, email VARCHAR, created_at TIMESTAMP, name VARCHAR",
    "product_id INT, price FLOAT, inventory INT",
]

LABELS = [
    "schema_v1",
    "schema_v2_minor_drift",
    "unrelated_schema",
]


@dataclass
class SimilarityReport:
    model_name: str
    similarity_matrix: np.ndarray
    v1_to_minor_drift: float
    v1_to_unrelated: float
    related_margin: float


def cosine_similarity_matrix(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    safe_norms = np.where(norms == 0, 1.0, norms)
    normalized = vectors / safe_norms
    return normalized @ normalized.T


def print_matrix(title: str, labels: List[str], matrix: np.ndarray) -> None:
    print(f"\n=== {title} ===")
    print(f"{'':28s}" + "".join(f"{label[:16]:>18s}" for label in labels))

    for label, row in zip(labels, matrix):
        values = "".join(f"{value:18.4f}" for value in row)
        print(f"{label[:28]:28s}{values}")


def build_synthetic_embeddings() -> Tuple[np.ndarray, np.ndarray]:
    """
    Synthetic vectors that mimic the failure mode from Yosef's explainer.

    Base geometry:
        - schema_v1 and schema_v2 are clearly close.
        - unrelated schema is farther away.

    Post-trained geometry:
        - schema_v1 and schema_v2 remain close.
        - unrelated schema moves closer to schema_v1.
        - the discriminative margin compresses.

    This keeps the script lightweight and runnable without downloading models.
    Replace this function with real model embeddings if needed.
    """
    base = np.array(
        [
            [1.00, 0.00, 0.00, 0.00],
            [0.96, 0.28, 0.00, 0.00],
            [0.88, 0.08, 0.45, 0.00],
        ],
        dtype=np.float32,
    )

    post_trained = np.array(
        [
            [1.00, 0.00, 0.00, 0.00],
            [0.93, 0.36, 0.00, 0.00],
            [0.92, 0.10, 0.30, 0.00],
        ],
        dtype=np.float32,
    )

    return base, post_trained


def make_report(model_name: str, embeddings: np.ndarray) -> SimilarityReport:
    sims = cosine_similarity_matrix(embeddings)

    v1_to_minor_drift = float(sims[0, 1])
    v1_to_unrelated = float(sims[0, 2])
    related_margin = v1_to_minor_drift - v1_to_unrelated

    return SimilarityReport(
        model_name=model_name,
        similarity_matrix=sims,
        v1_to_minor_drift=v1_to_minor_drift,
        v1_to_unrelated=v1_to_unrelated,
        related_margin=related_margin,
    )


def threshold_decision(score: float, threshold: float) -> str:
    if score >= threshold:
        return "semantically_related"
    return "schema_drift"


def main() -> None:
    threshold = 0.95

    base_embeddings, post_embeddings = build_synthetic_embeddings()

    base_report = make_report("base_checkpoint", base_embeddings)
    post_report = make_report("post_trained_checkpoint", post_embeddings)

    print_matrix(
        "BASE MODEL SIMILARITY",
        LABELS,
        base_report.similarity_matrix,
    )

    print_matrix(
        "POST-TRAINED MODEL SIMILARITY",
        LABELS,
        post_report.similarity_matrix,
    )

    print("\n=== THRESHOLD CHECK ===")
    print(f"Threshold: {threshold:.2f}")

    base_decision = threshold_decision(base_report.v1_to_minor_drift, threshold)
    post_decision = threshold_decision(post_report.v1_to_minor_drift, threshold)

    print(
        "schema_v1 vs schema_v2_minor_drift "
        f"base={base_report.v1_to_minor_drift:.4f} -> {base_decision}"
    )
    print(
        "schema_v1 vs schema_v2_minor_drift "
        f"post={post_report.v1_to_minor_drift:.4f} -> {post_decision}"
    )

    print("\n=== MARGIN CHECK ===")
    print(
        "Base related-vs-unrelated margin: "
        f"{base_report.related_margin:.4f}"
    )
    print(
        "Post-trained related-vs-unrelated margin: "
        f"{post_report.related_margin:.4f}"
    )
    print(
        "Margin shift: "
        f"{post_report.related_margin - base_report.related_margin:+.4f}"
    )

    print("\n=== RANK CHECK ===")
    base_rank_correct = base_report.v1_to_minor_drift > base_report.v1_to_unrelated
    post_rank_correct = post_report.v1_to_minor_drift > post_report.v1_to_unrelated

    print(f"Base rank correct: {base_rank_correct}")
    print(f"Post-trained rank correct: {post_rank_correct}")

    print("\n=== RECOMMENDED MITIGATION ===")
    print(
        "Do not reuse absolute cosine thresholds across checkpoints. "
        "Recalibrate thresholds after model updates and track similarity-margin "
        "drift. Prefer rank-based attribution when portability matters."
    )


if __name__ == "__main__":
    main()