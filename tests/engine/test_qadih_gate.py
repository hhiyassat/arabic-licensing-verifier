"""Example 3 acceptance :: هذا → Blocked via qadih-difference gate."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.contract.claim import (
    JudgmentClaim, ClaimKind, IsmIsharaPayload, IsmFaelPayload,
)
from src.contract.layers import ClaimBand
from src.contract.ranks import Rank
from src.contract.sinks import Sink
from src.engine.qadih_gate import evaluate, GATE_ID


def _hadha(status=Sink.LICENSED):
    return JudgmentClaim("h", ClaimBand.SYNTACTIC, ClaimKind.ISM_ISHARA,
                         IsmIsharaPayload("هذا", "near-singular-masc"),
                         status, Rank.STRONG)


def test_hadha_blocked_by_qadih():
    """هذا claiming derived agency → Blocked at the qadih gate."""
    v = evaluate(_hadha())
    assert v.sink == Sink.BLOCKED
    assert v.offending_gate == GATE_ID
    assert "قادح" in v.block_reason


def test_block_carries_where_and_why():
    """Constitutional: a block must say WHERE and WHY (not a bare 'no')."""
    v = evaluate(_hadha())
    assert v.offending_gate and v.block_reason      # both present
    assert len(v.trace) >= 2                         # trace records the steps
    assert v.trace[-1].passed is False               # the failing step is logged


def test_gate_does_not_overblock_derivational():
    """A legitimate derivational kind (IsmFael) is NOT blocked by THIS gate."""
    c = JudgmentClaim("d", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_FAEL,
                      IsmFaelPayload(root="ض ر ب", wazn="فاعل"),
                      Sink.LICENSED, Rank.STRONG)
    v = evaluate(c)
    assert v.sink != Sink.BLOCKED     # this gate lets it through (deferred to others)


def test_ishara_not_asserting_derivation_not_blocked():
    """هذا claimed merely as Deferred (not asserting agency) is not blocked here."""
    v = evaluate(_hadha(status=Sink.DEFERRED))
    assert v.sink != Sink.BLOCKED
