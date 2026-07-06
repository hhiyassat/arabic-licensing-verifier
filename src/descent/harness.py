#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descent Harness — the general verifier engine (Phase 2, honest edition)
=======================================================================
Adjudicates a JudgmentClaim by descending it through an ordered sequence of
governing questions. It returns the HONEST sink given the AVAILABLE evidence —
never a stronger result than the catalogs support.

Governing order (مُستنتَج, per development_plan.md — Scope first):
    Scope? → Evidence? → Rank? → Mani? → Residual?

Honest-output doctrine (منقول, constitution):
    Blocked   — a قادح preventer / explicit invalidating difference exists
    Deferred  — a required gate or evidence is missing (no proven preventer)
    Residual  — undecided competing possibilities remain, classified
    Licensed  — every gate cleared AND sufficient evidence present

NO dependency on HR2S or Qiyas. NO import of adapter internals. The verifier
alone adjudicates; the entrance only prepares candidates elsewhere.

This harness does NOT invent evidence. Where a real catalog (roots, awzan,
fiqh) is absent, the correct output is Deferred — not a fabricated Licensed.
"""
from __future__ import annotations
import os
import yaml

from src.contract.claim import (
    JudgmentClaim, ClaimKind, GenericPayload,
    IsmFaelPayload, IsmMakanPayload, IsmIsharaPayload,
)
from src.contract.evidence import CatalogEvidence, EvidenceBundle
from src.contract.layers import Layer
from src.contract.ranks import Rank
from src.contract.sinks import Sink, ResidualKind
from src.engine.verdict import Verdict, TraceEntry

_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data", "catalogs")


def _load_yaml(name: str) -> dict:
    path = os.path.join(_DATA, name)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ═══════════════════════════════════════════════════════════════════════════
# Evidence availability — what catalogs do we ACTUALLY have?
# The harness must be honest about absence or non-matching content:
# Deferred, not Licensed.
# ═══════════════════════════════════════════════════════════════════════════
def _available_catalogs() -> dict[str, bool]:
    return {
        "kind_ontology": bool(_load_yaml("kind_ontology.yaml")),
        "roots": os.path.exists(os.path.join(_DATA, "roots.yaml")),
        "awzan": os.path.exists(os.path.join(_DATA, "awzan.yaml")),
        "fiqh_evidence": os.path.exists(os.path.join(_DATA, "fiqh_evidence.yaml")),
    }


def _catalog_entries(catalog: dict, key: str) -> dict:
    entries = catalog.get(key, {})
    if isinstance(entries, dict):
        return entries
    if isinstance(entries, list):
        return {str(item): {"status": "attested"} for item in entries}
    return {}


def _source_details(catalog: dict, source_id: str | None) -> dict:
    if not source_id:
        return {}
    source = catalog.get("sources", {}).get(source_id, {})
    if not isinstance(source, dict):
        return {}
    return {"source_id": source_id, **source}


def _entry_source_id(entry: dict) -> str | None:
    provenance = entry.get("provenance", {})
    if isinstance(provenance, dict) and provenance.get("source"):
        return provenance["source"]
    source = entry.get("source", {})
    if isinstance(source, dict) and source.get("catalog"):
        return source["catalog"]
    return None


def _evidence_for(claim: JudgmentClaim) -> tuple[EvidenceBundle | None, str | None]:
    needed = _evidence_needed(claim.kind)
    catalogs = {name: _load_yaml(f"{name}.yaml") for name in needed}
    missing_files = [name for name, data in catalogs.items() if not data]
    if missing_files:
        return None, f"ناقص: {', '.join(missing_files)}"

    if not isinstance(claim.payload, (IsmFaelPayload, IsmMakanPayload)):
        return EvidenceBundle(), None

    roots = _catalog_entries(catalogs["roots"], "roots")
    awzan = _catalog_entries(catalogs["awzan"], "awzan")
    root_entry = roots.get(claim.payload.root)
    if not root_entry:
        return None, f"الجذر غير مشهود في roots.yaml: {claim.payload.root}"
    wazn_entry = awzan.get(claim.payload.wazn)
    if not wazn_entry:
        return None, f"الوزن غير مشهود في awzan.yaml: {claim.payload.wazn}"

    surface = _payload_surface(claim.payload)
    compatible, expected = _surface_compatible(claim.payload.root, claim.payload.wazn, surface)
    if not compatible:
        return None, (
            f"السطح لا يوافق الوزن المشهود: surface={surface!r}, "
            f"expected={expected!r}"
        )

    root_source_id = _entry_source_id(root_entry)
    wazn_source_id = _entry_source_id(wazn_entry)
    root_provenance = {
        "entry": root_entry.get("provenance", {}),
        "source": _source_details(catalogs["roots"], root_source_id),
    }
    wazn_provenance = {
        "entry": wazn_entry.get("source", {}),
        "source": _source_details(catalogs["awzan"], wazn_source_id),
    }
    return EvidenceBundle(
        root=CatalogEvidence("roots", claim.payload.root, root_entry, root_provenance),
        wazn=CatalogEvidence("awzan", claim.payload.wazn, wazn_entry, wazn_provenance),
        surface={
            "surface": surface,
            "expected": expected,
            "compatible": True,
        },
    ), None


def _payload_surface(payload: IsmFaelPayload | IsmMakanPayload) -> str | None:
    if isinstance(payload, IsmFaelPayload):
        return payload.surface_pattern
    return payload.surface


def _surface_compatible(root: str, wazn: str, surface: str | None) -> tuple[bool, str | None]:
    expected = _minimal_surface(root, wazn)
    if expected is None:
        return False, None
    if surface is None:
        return False, expected
    return _normalize_surface(surface) == _normalize_surface(expected), expected


def _minimal_surface(root: str, wazn: str) -> str | None:
    letters = root.split()
    if len(letters) != 3:
        return None
    fa, ayn, lam = letters
    if wazn == "فاعل":
        return f"{fa}ا{ayn}{lam}"
    if wazn == "مَفعِل":
        return f"مَ{fa}ْ{ayn}ِ{lam}"
    return None


def _normalize_surface(surface: str) -> str:
    return surface.replace("ْ", "")


# ═══════════════════════════════════════════════════════════════════════════
# The descent
# ═══════════════════════════════════════════════════════════════════════════
def descend(claim: JudgmentClaim) -> Verdict:
    trace: list[TraceEntry] = []
    step = 0
    ontology = _load_yaml("kind_ontology.yaml").get("kind_class", {})

    # ── Q1: SCOPE — is this claim's kind even in a band the box can adjudicate?
    step += 1
    kind_class = ontology.get(claim.kind.value)
    if kind_class is None:
        trace.append(TraceEntry(step, "scope",
                     "هل النوع ضمن نطاقٍ يعرفه الصندوق؟", False,
                     f"النوع {claim.kind.value} خارج جدول المقولات"))
        return Verdict(Sink.DEFERRED, Layer.SURFACE, Rank.NONE, tuple(trace),
                       residual_kind=None)
    trace.append(TraceEntry(step, "scope", "هل النوع ضمن النطاق؟", True,
                            f"{claim.kind.value} → {kind_class}"))

    # ── Q_QADIH: invalidating-difference check (referential ↛ derivational)
    #    A referential anchor claiming a derivational (Licensed) ascent is Blocked.
    step += 1
    asserts_ascent = claim.claimed_status == Sink.LICENSED
    if kind_class == "referential" and asserts_ascent:
        trace.append(TraceEntry(step, "qadih_difference",
                     "هل يُقاس مشغّل الإحالة على الأصل الحدثيّ؟", False,
                     "فرقٌ قادح: referential ↛ derivational"))
        return Verdict(
            Sink.BLOCKED, Layer.SURFACE, Rank.NONE, tuple(trace),
            block_reason=("النوع المُدَّعى إحالةٌ مقاميّة لا أصلٌ حدثيّ؛ "
                          "اشتقاق فاعليّةٍ منه قياسٌ فاسدٌ عبر فرقٍ قادح."),
            offending_gate="qadih.difference.referential_vs_derivational",
        )
    trace.append(TraceEntry(step, "qadih_difference",
                            "هل يوجد فرقٌ قادح؟", True, "لا فرق قادح عند هذه البوابة"))

    # ── Generic payloads may never be Licensed (constitutional). → Deferred.
    if isinstance(claim.payload, GenericPayload):
        step += 1
        trace.append(TraceEntry(step, "generic_guard",
                     "هل الحمولة عامّة (Generic)؟", True,
                     "GenericPayload لا يبلغ Licensed — يُؤجَّل"))
        return Verdict(Sink.DEFERRED, Layer.SURFACE, Rank.NONE, tuple(trace))

    # ── Q2: EVIDENCE — do the catalogs contain this claim's exact evidence?
    step += 1
    evidence, evidence_error = _evidence_for(claim)
    if evidence_error:
        trace.append(TraceEntry(step, "evidence",
                     "هل الجذر والوزن والسطح مشهودات تحديدًا؟", False,
                     f"{evidence_error} → لا يمكن بلوغ الترخيص بصدق"))
        # honest stop: missing evidence, no proven preventer → Deferred
        return Verdict(
            Sink.DEFERRED, _band_for(claim.kind), Rank.NONE, tuple(trace),
            block_reason=None,
            residual_kind=None,
            evidence=evidence,
        )
    trace.append(TraceEntry(step, "evidence",
                            "هل الأدلّة المحدّدة متوفّرة؟", True,
                            _evidence_note(evidence)))

    # ── Q_RESIDUAL: competing readings? (e.g. مَضرِب makan/zaman/aala)
    step += 1
    if isinstance(claim.payload, IsmMakanPayload) and len(claim.payload.possible_readings) > 1:
        trace.append(TraceEntry(step, "residual",
                     "هل بقيت قراءاتٌ متنافسة؟", False,
                     f"قراءات متنافسة: {claim.payload.possible_readings}"))
        return Verdict(
            Sink.RESIDUAL, _band_for(claim.kind), Rank.PLAUSIBLE, tuple(trace),
            residual_kind=ResidualKind.COMPETING_CLAIM,
            evidence=evidence,
        )
    trace.append(TraceEntry(step, "residual", "هل بقيت احتمالات؟", True,
                            "لا احتمالات متنافسة غير محسومة"))

    # ── All gates cleared AND evidence present → Licensed.
    step += 1
    trace.append(TraceEntry(step, "closure",
                            "هل اجتازت كلّ البوابات برخصة؟", True,
                            "كلّ البوابات مرخّصة، والدليل حاضر"))
    return Verdict(
        Sink.LICENSED, _band_for(claim.kind), claim.claimed_rank, tuple(trace),
        evidence=evidence,
    )


def _evidence_note(evidence: EvidenceBundle | None) -> str:
    if not evidence or not evidence.root or not evidence.wazn:
        return "لا يحتاج هذا النوع إلى كتالوج جذر/وزن"
    root_source = evidence.root.provenance.get("source", {}).get("source_id", "unknown")
    wazn_source = evidence.wazn.provenance.get("source", {}).get("source_id", "unknown")
    surface = evidence.surface or {}
    return (
        f"root={evidence.root.key} via {root_source}; "
        f"wazn={evidence.wazn.key} via {wazn_source}; "
        f"surface={surface.get('surface')}~{surface.get('expected')}"
    )


def _evidence_needed(kind: ClaimKind) -> list[str]:
    """Which catalogs a kind needs to reach Licensed (honest requirements)."""
    if kind == ClaimKind.ISM_FAEL:
        return ["roots", "awzan"]           # derivation needs root + wazn attestation
    if kind == ClaimKind.ISM_MAKAN:
        return ["roots", "awzan"]
    if kind == ClaimKind.ISM_ISHARA:
        return ["kind_ontology"]            # closed class; ontology suffices
    return ["kind_ontology"]


def _band_for(kind: ClaimKind) -> Layer:
    if kind == ClaimKind.ISM_ISHARA:
        return Layer.SURFACE
    return Layer.WAZN
