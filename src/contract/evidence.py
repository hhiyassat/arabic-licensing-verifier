"""
Phase 0 — Contract :: Evidence (الدليل)
=======================================
FORBIDDEN OUTPUT: any evaluation. Declares the shape of evidence only.

Rationale: the rule "no rank exceeds its evidence" is UNTESTABLE without a
first-class Evidence object. Required for audit/funding review:
"where did this license come from?"

Contract (مستنتج, per critique):
    Evidence := { source, kind, rank, scope, citation, confidence }
    source ∈ { catalog, rule, manual, lexicon, grammar_source,
               corpus_attestation, expert_annotation }

STATUS: filled minimally. Shape only; no evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CatalogEvidence:
    """A single matched catalog entry used by a verifier verdict."""
    catalog: str
    key: str
    entry: Mapping[str, Any]
    provenance: Mapping[str, Any]


@dataclass(frozen=True)
class EvidenceBundle:
    """Evidence gathered along a descent path."""
    root: CatalogEvidence | None = None
    wazn: CatalogEvidence | None = None
    surface: Mapping[str, Any] | None = None
