"""
Descent harness :: the three cases produce HONEST sinks per available evidence.
Proves the box behaves correctly in BOTH worlds (evidence absent vs present).
"""
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.contract.claim import (
    JudgmentClaim, ClaimKind,
    IsmFaelPayload, IsmMakanPayload, IsmIsharaPayload, GenericPayload,
)
from src.contract.layers import ClaimBand
from src.contract.ranks import Rank
from src.contract.sinks import Sink, ResidualKind
from src.descent import harness


# ── Case 1: هذا claiming derivation → Blocked (proven preventer)
def test_case_simple_hadha_blocked():
    c = JudgmentClaim("h", ClaimBand.SYNTACTIC, ClaimKind.ISM_ISHARA,
                      IsmIsharaPayload("هذا", "near-singular-masc"),
                      Sink.LICENSED, Rank.STRONG)
    v = harness.descend(c)
    assert v.sink == Sink.BLOCKED
    assert v.offending_gate.startswith("qadih")


# ── Case 2 & 3 with NO catalogs: honest Deferred (missing evidence)
def test_case_medium_madrib_deferred_without_catalogs():
    c = JudgmentClaim("m", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_MAKAN,
                      IsmMakanPayload("ض ر ب", "مَفعِل", possible_readings=("makan", "zaman")),
                      Sink.RESIDUAL, Rank.PROBABLE)
    v = harness.descend(c)
    assert v.sink == Sink.DEFERRED           # honest: catalogs absent
    assert any("evidence" == t.gate_id for t in v.trace)


def test_case_large_darib_deferred_not_licensed():
    """The big case must NOT fake Licensed without evidence."""
    c = JudgmentClaim("d", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_FAEL,
                      IsmFaelPayload("ض ر ب", "فاعل"),
                      Sink.LICENSED, Rank.STRONG)
    v = harness.descend(c)
    assert v.sink == Sink.DEFERRED           # NOT Licensed — no fiqh/roots evidence
    assert v.rank == Rank.NONE


# ── With catalogs PRESENT: prove the box CAN reach Residual and Licensed
def _with_catalogs(tmp_path, monkeypatch):
    """Point the harness at a temp catalog dir that HAS roots + awzan."""
    d = tmp_path
    # copy kind_ontology so scope still works
    src_onto = os.path.join(os.path.dirname(harness.__file__), "..", "..",
                            "data", "catalogs", "kind_ontology.yaml")
    with open(src_onto, encoding="utf-8") as f:
        onto = f.read()
    with open(os.path.join(d, "kind_ontology.yaml"), "w", encoding="utf-8") as f:
        f.write(onto)
    # create minimal roots + awzan attestations
    with open(os.path.join(d, "roots.yaml"), "w", encoding="utf-8") as f:
        f.write("roots:\n  - ض ر ب\n")
    with open(os.path.join(d, "awzan.yaml"), "w", encoding="utf-8") as f:
        f.write("awzan:\n  - فاعل\n  - مَفعِل\n")
    monkeypatch.setattr(harness, "_DATA", str(d))


def test_madrib_becomes_residual_when_catalogs_present(tmp_path, monkeypatch):
    _with_catalogs(tmp_path, monkeypatch)
    c = JudgmentClaim("m", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_MAKAN,
                      IsmMakanPayload("ض ر ب", "مَفعِل", possible_readings=("makan", "zaman")),
                      Sink.RESIDUAL, Rank.PROBABLE)
    v = harness.descend(c)
    assert v.sink == Sink.RESIDUAL
    assert v.residual_kind == ResidualKind.COMPETING_CLAIM


def test_darib_licensed_when_catalogs_present(tmp_path, monkeypatch):
    _with_catalogs(tmp_path, monkeypatch)
    c = JudgmentClaim("d", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_FAEL,
                      IsmFaelPayload("ض ر ب", "فاعل"),
                      Sink.LICENSED, Rank.STRONG)
    v = harness.descend(c)
    assert v.sink == Sink.LICENSED           # now evidence exists → honest Licensed
    assert v.rank == Rank.STRONG
