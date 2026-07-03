"""
Phase 0 — Contract :: JudgmentClaim (محتوى الحكم المُدَّعى)
=========================================================
FORBIDDEN OUTPUT: any validation or descent logic. Declares the claim's SHAPE.

THE KEY FIX (critique's main finding): status + rank + layer describe the
claim's *position*, not its *content*. The descent cannot adjudicate a claim
it cannot read — so the claim carries kind + payload.

DECISION (your ruling): typed payloads for a small CLOSED first set, with a
GenericPayload escape hatch. Constitutional rule:

    GenericPayload CANNOT produce Licensed.
    GenericPayload may only end as Deferred | Residual | Experimental.

This preserves TypedClaim (systemic self-criterion #2: identity across
transitions) without exploding the taxonomy prematurely (Phase 0 stays deaf
to the full catalog — that is Phase 3).

Mathematical contract (Fork A):
    JudgmentClaim := (claim_id, band, kind, payload,
                      claimed_status, claimed_rank)
    payload : ClaimPayload  where ClaimPayload is a CLOSED union:
        IsmFaelPayload | IsmMakanPayload | IsmIsharaPayload | GenericPayload
    Constraint:  payload is GenericPayload  ⇒  claimed_status ≠ Licensed
                 (enforced structurally here; re-checked as an invariant later)

First closed set matches the three Phase-2 oracles:
    IsmFael   → ضارب      IsmMakan → مَضرِب      IsmIshara → هذا
    Generic   → deferred / residual / experimental only

STATUS: filled (Phase 0). Shape + first four payloads. No logic.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Union

from .layers import ClaimBand
from .ranks import Rank
from .sinks import Sink


# ─────────────────────────────────────────────────────────────────────────
# ClaimKind — the closed first set (Phase 0). Expanded only in later phases.
# ─────────────────────────────────────────────────────────────────────────
class ClaimKind(str, Enum):
    ISM_FAEL = "IsmFael"        # اسم فاعل   — oracle: ضارب
    ISM_MAKAN = "IsmMakan"      # اسم مكان   — oracle: مَضرِب
    ISM_ISHARA = "IsmIshara"    # اسم إشارة  — oracle: هذا
    GENERIC = "Generic"         # escape hatch — Deferred/Residual only

    def __str__(self) -> str:
        return self.value


# ─────────────────────────────────────────────────────────────────────────
# Typed payloads — one per licensed-eligible kind.
# frozen: a claim's content is immutable once asserted (identity preservation).
# ─────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class IsmFaelPayload:
    """اسم فاعل: derived agent noun. Needs a root and a wazn."""
    root: str                       # e.g. "ض ر ب"
    wazn: str                       # e.g. "فاعل"
    surface_pattern: str | None = None

    KIND = ClaimKind.ISM_FAEL


@dataclass(frozen=True)
class IsmMakanPayload:
    """اسم مكان: place noun. May carry competing readings (makan/zaman/aala)."""
    root: str
    wazn: str
    possible_readings: tuple[str, ...] = ()

    KIND = ClaimKind.ISM_MAKAN


@dataclass(frozen=True)
class IsmIsharaPayload:
    """اسم إشارة: demonstrative. A closed-class deictic; no root derivation."""
    surface: str                    # e.g. "هذا"
    deictic_class: str              # e.g. "near-singular-masc"

    KIND = ClaimKind.ISM_ISHARA


@dataclass(frozen=True)
class GenericPayload:
    """
    Escape hatch for unmodeled / experimental / deferred claims.
    CONSTITUTIONALLY barred from producing Licensed (see JudgmentClaim.__post_init__).
    """
    raw: Mapping[str, Any]
    reason: str                     # why this isn't (yet) a typed kind

    KIND = ClaimKind.GENERIC


# Closed union of accepted payloads (Phase 0 first set).
ClaimPayload = Union[
    IsmFaelPayload,
    IsmMakanPayload,
    IsmIsharaPayload,
    GenericPayload,
]


# ─────────────────────────────────────────────────────────────────────────
# JudgmentClaim — the full claimed حكم (five-field Fork B, revised).
# ─────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class JudgmentClaim:
    claim_id: str
    band: ClaimBand                 # coarse target layer of the claim
    kind: ClaimKind
    payload: ClaimPayload
    claimed_status: Sink            # the status the claimant asserts
    claimed_rank: Rank

    def __post_init__(self) -> None:
        # Structural guard #1: payload must match declared kind.
        declared = getattr(self.payload, "KIND", None)
        if declared is not None and declared != self.kind:
            raise ValueError(
                f"payload/kind mismatch: kind={self.kind} "
                f"but payload is for {declared}"
            )
        # Structural guard #2 (CONSTITUTIONAL):
        #   GenericPayload can never CLAIM Licensed.
        if isinstance(self.payload, GenericPayload) \
                and self.claimed_status == Sink.LICENSED:
            raise ValueError(
                "GenericPayload cannot claim Licensed "
                "(may only be Deferred/Residual/Experimental)"
            )

    @property
    def is_generic(self) -> bool:
        return isinstance(self.payload, GenericPayload)
