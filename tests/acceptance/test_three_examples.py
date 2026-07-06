"""
Acceptance :: the three worked examples (Phase 2 closure criterion)
==================================================================
These are the oracle for the Descent with the real verifier catalogs present.

1) هذا     → Blocked at the qadih-difference gate
2) مَضرِب  → Residual, because place/time readings compete
3) ضارب   → Licensed, because root + wazn catalogs are now present
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.contract.claim import (
    ClaimKind,
    IsmFaelPayload,
    IsmIsharaPayload,
    IsmMakanPayload,
    JudgmentClaim,
)
from src.contract.layers import ClaimBand
from src.contract.ranks import Rank
from src.contract.sinks import ResidualKind, Sink
from src.descent.harness import descend


def test_hadha_stays_blocked_by_qadih():
    claim = JudgmentClaim(
        "acceptance-hadha",
        ClaimBand.SYNTACTIC,
        ClaimKind.ISM_ISHARA,
        IsmIsharaPayload("هذا", "near-singular-masc"),
        Sink.LICENSED,
        Rank.STRONG,
    )

    verdict = descend(claim)

    assert verdict.sink == Sink.BLOCKED
    assert verdict.offending_gate == "qadih.difference.referential_vs_derivational"


def test_madrib_is_residual():
    claim = JudgmentClaim(
        "acceptance-madrib",
        ClaimBand.MORPHOLOGICAL,
        ClaimKind.ISM_MAKAN,
        IsmMakanPayload(
            "ض ر ب", "مَفعِل",
            possible_readings=("makan", "zaman"),
            surface="مَضرِب",
        ),
        Sink.RESIDUAL,
        Rank.PROBABLE,
    )

    verdict = descend(claim)

    assert verdict.sink == Sink.RESIDUAL
    assert verdict.residual_kind == ResidualKind.COMPETING_CLAIM
    assert verdict.rank == Rank.PLAUSIBLE


def test_darib_is_licensed_with_real_catalogs():
    claim = JudgmentClaim(
        "acceptance-darib",
        ClaimBand.MORPHOLOGICAL,
        ClaimKind.ISM_FAEL,
        IsmFaelPayload("ض ر ب", "فاعل", surface_pattern="ضارب"),
        Sink.LICENSED,
        Rank.STRONG,
    )

    verdict = descend(claim)

    assert verdict.sink == Sink.LICENSED
    assert verdict.rank == Rank.STRONG
