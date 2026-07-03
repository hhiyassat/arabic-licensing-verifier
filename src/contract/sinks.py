"""
Phase 0 — Contract :: Sinks (المصبّات الأربعة)
==============================================
FORBIDDEN OUTPUT: routing logic (Phase 1 engine/router.py decides WHICH sink).
Declares the four sink identities and their per-sink payload shapes.

Mathematical contract (Fork A):
    Sink := Licensed | Blocked | Deferred | Residual        (منقول §1-3)
    The four are EXHAUSTIVE and DISJOINT: every outcome lands in exactly one.

    Sinks are NOT symmetric — each carries different data:
        Licensed  → earned_rank, licensed path
        Blocked   → offending gate, proven preventer / explicit violation
        Deferred  → what evidence is missing (no proven preventer)
        Residual  → a CLASSIFIED remainder (NOT a success)

    Constitutional rule (منقول): Residual is not Licensed.
        A preserved, classified, unresolved remainder — a respected sink,
        never a grant.

STATUS: filled (Phase 0). Identities + residual taxonomy; payload bodies
are light stubs (fleshed out with the router in Phase 1).
"""
from __future__ import annotations
from enum import Enum


class Sink(str, Enum):
    """The four exhaustive, disjoint outcome sinks."""
    LICENSED = "Licensed"
    BLOCKED = "Blocked"
    DEFERRED = "Deferred"
    RESIDUAL = "Residual"

    def __str__(self) -> str:
        return self.value


class ResidualKind(str, Enum):
    """
    Classification of residuals (مستنتج, per critique). Residual must never be
    a general dump — every remainder is typed.
    """
    AMBIGUITY = "AmbiguityResidual"
    MISSING_CATALOG = "MissingCatalogResidual"
    LAYER_BOUNDARY = "LayerBoundaryResidual"
    COMPETING_CLAIM = "CompetingClaimResidual"
    UNPRICED_LICENSE = "UnpricedLicenseResidual"

    def __str__(self) -> str:
        return self.value


# Per-sink payload bodies are intentionally light in Phase 0.
# They are declared as forward markers; filled with the router in Phase 1.
# TODO(Phase1): LicensedPayload, BlockedPayload, DeferredPayload, ResidualPayload
