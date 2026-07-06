"""P5 Claim Bridge :: pure conversion from entrance metadata to verifier drafts."""
import hashlib
import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from adapter.entrance_adapter import (
    RANK_CATALOG_ATTESTED,
    STATUS_CATALOG_ATTESTED,
    STATUS_DEFERRED_TO_VERIFIER,
    build_entrance_record,
)
from src.bridge import claim_bridge
from src.bridge.claim_bridge import (
    DraftStatus,
    VerifierInputDraft,
    adjudicate_draft,
    draft_to_judgment_claim,
    propose_verifier_input_drafts,
)
from src.contract.claim import ClaimKind, GenericPayload, IsmFaelPayload, IsmIsharaPayload
from src.contract.ranks import Rank
from src.contract.sinks import Sink


FORBIDDEN_DRAFT_FIELDS = {"Licensed", "final_verdict", "final_sink", "proved", "verified"}
EXPECTED_FROZEN_HASHES = {
    "constitution": "1afdc449718a",
    "closure_criteria": "09d9a458bb2e",
    "development_plan": "a3fa125a9f10",
}


def _single_draft(raw_text: str) -> tuple[object, VerifierInputDraft]:
    record = build_entrance_record(raw_text)
    drafts = propose_verifier_input_drafts(record)
    assert len(drafts) == 1
    return record, drafts[0]


def _attested_record(raw_text: str, metadata: dict[str, str]):
    record = build_entrance_record(raw_text)
    evidence = record.tokens[0].evidence
    evidence.status = STATUS_CATALOG_ATTESTED
    evidence.catalog = "test_catalog"
    evidence.matched_on = "test"
    evidence.rank = RANK_CATALOG_ATTESTED
    evidence.raw_metadata.update(metadata)
    evidence.residual = None
    return record


def test_bridge_source_has_no_hardcoded_surface_to_kind_mappings():
    source = inspect.getsource(claim_bridge)
    assert "ضارب" not in source
    assert "مَضرِب" not in source
    assert "مضرب" not in source
    assert "هذا" not in source
    assert "surface ==" not in source
    assert "undiacritized ==" not in source


def test_bridge_source_has_no_h2rs_or_qiyas_imports():
    source = inspect.getsource(claim_bridge).lower()
    assert "h2rs" not in source
    assert "hr2s" not in source
    assert "qiyas" not in source


def test_draft_shape_has_no_final_judgment_fields():
    _, draft = _single_draft("ضارب")
    assert FORBIDDEN_DRAFT_FIELDS.isdisjoint(draft.__dataclass_fields__)
    assert draft.status in {
        DraftStatus.CANDIDATE,
        DraftStatus.DEFERRED_TO_VERIFIER,
        DraftStatus.RESIDUAL_CANDIDATE,
    }


def test_unknown_or_no_catalog_token_becomes_generic_deferred_to_verifier():
    record, draft = _single_draft("ضارب")
    assert record.handoff == STATUS_DEFERRED_TO_VERIFIER
    assert draft.kind == ClaimKind.GENERIC
    assert isinstance(draft.payload, GenericPayload)
    assert draft.status == DraftStatus.DEFERRED_TO_VERIFIER

    claim = draft_to_judgment_claim(draft, Sink.DEFERRED, "p5-generic-darib")
    assert claim.kind == ClaimKind.GENERIC
    verdict = adjudicate_draft(draft, Sink.DEFERRED, "p5-generic-darib")
    assert verdict.sink == Sink.DEFERRED


def test_catalog_attested_ism_ishara_converts_from_metadata():
    record, draft = _single_draft("هذا")
    assert record.handoff == STATUS_DEFERRED_TO_VERIFIER
    assert draft.kind == ClaimKind.ISM_ISHARA
    assert isinstance(draft.payload, IsmIsharaPayload)
    assert draft.payload.surface == "هذا"
    assert draft.payload.deictic_class == "near-singular-masc"
    assert draft.status == DraftStatus.DEFERRED_TO_VERIFIER

    verdict = adjudicate_draft(draft, Sink.LICENSED, "p5-hadha")
    assert verdict.sink == Sink.BLOCKED
    assert verdict.offending_gate == "qadih.difference.referential_vs_derivational"


def test_darib_with_explicit_entrance_attestation_can_reach_licensed():
    record = _attested_record("ضارب", {
        "kind": "IsmFael",
        "root": "ض ر ب",
        "wazn": "فاعل",
    })
    draft = propose_verifier_input_drafts(record)[0]
    assert draft.kind == ClaimKind.ISM_FAEL
    assert isinstance(draft.payload, IsmFaelPayload)
    assert draft.payload.root == "ض ر ب"
    assert draft.payload.wazn == "فاعل"
    assert draft.payload.surface_pattern == "ضارب"
    assert draft.status == DraftStatus.CANDIDATE

    verdict = adjudicate_draft(draft, Sink.LICENSED, "p5-darib-attested")
    assert verdict.sink == Sink.LICENSED
    assert verdict.rank == Rank.STRONG


def test_missing_root_absent_from_roots_yaml_returns_deferred_not_licensed():
    record = _attested_record("خازق", {
        "kind": "IsmFael",
        "root": "خ ز ق",
        "wazn": "فاعل",
    })
    draft = propose_verifier_input_drafts(record)[0]
    verdict = adjudicate_draft(draft, Sink.LICENSED, "p5-missing-root")
    assert verdict.sink == Sink.DEFERRED
    assert verdict.rank == Rank.NONE
    assert "الجذر غير مشهود" in verdict.trace[-1].note


def test_frozen_constitution_hashes_remain_unchanged():
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs")
    for name, expected in EXPECTED_FROZEN_HASHES.items():
        path = os.path.join(docs_dir, f"{name}.md")
        with open(path, "rb") as handle:
            digest = hashlib.sha256(handle.read()).hexdigest()[:12]
        assert digest == expected
