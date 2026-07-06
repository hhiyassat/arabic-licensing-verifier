"""
P5 Claim Bridge — EntranceRecord → VerifierInputDraft → JudgmentClaim.

Candidate-only. No licensing, no final sink, no general morphology.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from adapter.entrance_adapter import EntranceRecord
from src.contract.claim import (
    ClaimKind,
    ClaimPayload,
    GenericPayload,
    IsmFaelPayload,
    IsmIsharaPayload,
    IsmMakanPayload,
    JudgmentClaim,
)
from src.contract.layers import ClaimBand
from src.contract.ranks import Rank
from src.contract.sinks import Sink
from src.descent.harness import descend
from src.engine.verdict import Verdict


class DraftStatus(str, Enum):
    CANDIDATE = "Candidate"
    DEFERRED_TO_VERIFIER = "DeferredToVerifier"
    RESIDUAL_CANDIDATE = "ResidualCandidate"


@dataclass(frozen=True)
class VerifierInputDraft:
    surface: str
    kind: ClaimKind
    payload: ClaimPayload
    rank: Rank
    band: ClaimBand
    evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    trace: tuple[str, ...] = field(default_factory=tuple)
    source: str = "P5ClaimBridge"
    status: DraftStatus = DraftStatus.CANDIDATE


def propose_verifier_input_drafts(record: EntranceRecord) -> tuple[VerifierInputDraft, ...]:
    drafts: list[VerifierInputDraft] = []
    entrance_trace = tuple(str(event) for event in record.all_trace())

    for token_entrance in record.tokens:
        token = token_entrance.token
        surface = token.token_normalized
        evidence = (_entrance_evidence(token_entrance.evidence),)
        raw_metadata = token_entrance.evidence.raw_metadata

        drafts.append(_draft_from_metadata(surface, raw_metadata, evidence, entrance_trace))

    return tuple(drafts)


def draft_to_judgment_claim(
    draft: VerifierInputDraft,
    claimed_status: Sink,
    claim_id: str | None = None,
) -> JudgmentClaim:
    return JudgmentClaim(
        claim_id=claim_id or f"p5-{draft.surface}",
        band=draft.band,
        kind=draft.kind,
        payload=draft.payload,
        claimed_status=claimed_status,
        claimed_rank=draft.rank,
    )


def adjudicate_draft(
    draft: VerifierInputDraft,
    claimed_status: Sink,
    claim_id: str | None = None,
) -> Verdict:
    return descend(draft_to_judgment_claim(draft, claimed_status, claim_id))


def _entrance_evidence(evidence: Any) -> dict[str, Any]:
    return {
        "status": evidence.status,
        "catalog": evidence.catalog,
        "matched_on": evidence.matched_on,
        "raw_metadata": dict(evidence.raw_metadata),
        "residual": evidence.residual,
        "rank": evidence.rank,
    }


def _draft_from_metadata(
    surface: str,
    raw_metadata: dict[str, str],
    evidence: tuple[dict[str, Any], ...],
    trace: tuple[str, ...],
) -> VerifierInputDraft:
    kind = _kind_from_metadata(raw_metadata)
    if kind == ClaimKind.ISM_ISHARA:
        return VerifierInputDraft(
            surface=surface,
            kind=ClaimKind.ISM_ISHARA,
            payload=IsmIsharaPayload(
                surface=surface,
                deictic_class=raw_metadata.get("deictic_class") or raw_metadata.get("note", ""),
            ),
            rank=_rank_from_metadata(raw_metadata, Rank.STRONG),
            band=ClaimBand.SYNTACTIC,
            evidence=evidence,
            trace=trace,
            status=DraftStatus.DEFERRED_TO_VERIFIER,
        )

    if kind == ClaimKind.ISM_FAEL:
        root = raw_metadata.get("root")
        wazn = raw_metadata.get("wazn")
        if root and wazn:
            return VerifierInputDraft(
                surface=surface,
                kind=ClaimKind.ISM_FAEL,
                payload=IsmFaelPayload(root, wazn, surface_pattern=surface),
                rank=_rank_from_metadata(raw_metadata, Rank.STRONG),
                band=ClaimBand.MORPHOLOGICAL,
                evidence=evidence,
                trace=trace,
                status=DraftStatus.CANDIDATE,
            )

    if kind == ClaimKind.ISM_MAKAN:
        root = raw_metadata.get("root")
        wazn = raw_metadata.get("wazn")
        if root and wazn:
            return VerifierInputDraft(
                surface=surface,
                kind=ClaimKind.ISM_MAKAN,
                payload=IsmMakanPayload(
                    root,
                    wazn,
                    possible_readings=_readings_from_metadata(raw_metadata),
                    surface=surface,
                ),
                rank=_rank_from_metadata(raw_metadata, Rank.PROBABLE),
                band=ClaimBand.MORPHOLOGICAL,
                evidence=evidence,
                trace=trace,
                status=DraftStatus.RESIDUAL_CANDIDATE,
            )

    return VerifierInputDraft(
        surface=surface,
        kind=ClaimKind.GENERIC,
        payload=GenericPayload(
            raw={"surface": surface, "metadata": dict(raw_metadata)},
            reason="no explicit entrance kind/root/wazn candidate",
        ),
        rank=Rank.NONE,
        band=ClaimBand.SURFACE,
        evidence=evidence,
        trace=trace,
        status=DraftStatus.DEFERRED_TO_VERIFIER,
    )


def _kind_from_metadata(raw_metadata: dict[str, str]) -> ClaimKind:
    value = raw_metadata.get("kind") or raw_metadata.get("category") or ""
    if value in {ClaimKind.ISM_FAEL.value, "اسم_فاعل"}:
        return ClaimKind.ISM_FAEL
    if value in {ClaimKind.ISM_MAKAN.value, "اسم_مكان"}:
        return ClaimKind.ISM_MAKAN
    if value in {ClaimKind.ISM_ISHARA.value, "اسم_اشارة"}:
        return ClaimKind.ISM_ISHARA
    return ClaimKind.GENERIC


def _readings_from_metadata(raw_metadata: dict[str, str]) -> tuple[str, ...]:
    value = raw_metadata.get("possible_readings") or raw_metadata.get("readings") or ""
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _rank_from_metadata(raw_metadata: dict[str, str], default: Rank) -> Rank:
    value = raw_metadata.get("rank")
    if not value:
        return default
    try:
        return Rank[value.upper()]
    except KeyError:
        return default
