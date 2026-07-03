"""Phase 0 acceptance :: JudgmentClaim shape + constitutional guard."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from src.contract.claim import (
    JudgmentClaim, ClaimKind,
    IsmFaelPayload, IsmMakanPayload, IsmIsharaPayload, GenericPayload,
)
from src.contract.layers import ClaimBand
from src.contract.ranks import Rank
from src.contract.sinks import Sink


def test_darib_ism_fael_instantiates():
    c = JudgmentClaim("darib-1", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_FAEL,
                      IsmFaelPayload(root="ض ر ب", wazn="فاعل"),
                      Sink.LICENSED, Rank.STRONG)
    assert not c.is_generic and c.payload.root == "ض ر ب"


def test_madrib_ism_makan_with_competing_readings():
    c = JudgmentClaim("madrib-1", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_MAKAN,
                      IsmMakanPayload(root="ض ر ب", wazn="مَفعِل",
                                      possible_readings=("makan", "zaman")),
                      Sink.RESIDUAL, Rank.PROBABLE)
    assert c.payload.possible_readings == ("makan", "zaman")


def test_hadha_ism_ishara():
    c = JudgmentClaim("hadha-1", ClaimBand.SYNTACTIC, ClaimKind.ISM_ISHARA,
                      IsmIsharaPayload(surface="هذا", deictic_class="near-sg-masc"),
                      Sink.LICENSED, Rank.STRONG)
    assert c.payload.surface == "هذا"


def test_payload_kind_mismatch_rejected():
    with pytest.raises(ValueError, match="payload/kind mismatch"):
        JudgmentClaim("bad-1", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_ISHARA,
                      IsmFaelPayload(root="ض ر ب", wazn="فاعل"),
                      Sink.DEFERRED, Rank.WEAK)


def test_generic_cannot_claim_licensed():
    with pytest.raises(ValueError, match="cannot claim Licensed"):
        JudgmentClaim("gen-bad", ClaimBand.SEMANTIC, ClaimKind.GENERIC,
                      GenericPayload(raw={"note": "ربما اسم فاعل"},
                                     reason="kind not yet modeled"),
                      Sink.LICENSED, Rank.STRONG)


def test_generic_allowed_as_deferred():
    c = JudgmentClaim("gen-ok", ClaimBand.SEMANTIC, ClaimKind.GENERIC,
                      GenericPayload(raw={"note": "ربما اسم فاعل"},
                                     reason="kind not yet modeled"),
                      Sink.DEFERRED, Rank.WEAK)
    assert c.is_generic
