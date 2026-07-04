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
from dataclasses import dataclass

from src.contract.claim import (
    JudgmentClaim, ClaimKind, GenericPayload,
    IsmFaelPayload, IsmMakanPayload, IsmIsharaPayload,
)
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
#   Present now: kind_ontology (referential/derivational).
#   ABSENT now:  roots catalog, awzan catalog, fiqh-evidence catalog.
# The harness must be honest about absence → Deferred, not Licensed.
# ═══════════════════════════════════════════════════════════════════════════
def _available_catalogs() -> dict[str, bool]:
    return {
        "kind_ontology": bool(_load_yaml("kind_ontology.yaml")),
        "roots": os.path.exists(os.path.join(_DATA, "roots.yaml")),
        "awzan": os.path.exists(os.path.join(_DATA, "awzan.yaml")),
        "fiqh_evidence": os.path.exists(os.path.join(_DATA, "fiqh_evidence.yaml")),
    }


# ═══════════════════════════════════════════════════════════════════════════
# The descent
# ═══════════════════════════════════════════════════════════════════════════
def descend(claim: JudgmentClaim) -> Verdict:
    trace: list[TraceEntry] = []
    step = 0
    cats = _available_catalogs()
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

    # ── Q2: EVIDENCE — do we have the catalogs this kind needs?
    step += 1
    needed = _evidence_needed(claim.kind)
    missing = [c for c in needed if not cats.get(c, False)]
    if missing:
        trace.append(TraceEntry(step, "evidence",
                     "هل الكتالوجات اللازمة متوفّرة؟", False,
                     f"ناقص: {', '.join(missing)} → لا يمكن بلوغ الترخيص بصدق"))
        # honest stop: missing evidence, no proven preventer → Deferred
        return Verdict(
            Sink.DEFERRED, _band_for(claim.kind), Rank.NONE, tuple(trace),
            block_reason=None,
            residual_kind=None,
        )
    trace.append(TraceEntry(step, "evidence",
                            "هل الأدلّة متوفّرة؟", True, "كلّ الكتالوجات اللازمة حاضرة"))

    # ── Q_RESIDUAL: competing readings? (e.g. مَضرِب makan/zaman/aala)
    step += 1
    if isinstance(claim.payload, IsmMakanPayload) and len(claim.payload.possible_readings) > 1:
        trace.append(TraceEntry(step, "residual",
                     "هل بقيت قراءاتٌ متنافسة؟", False,
                     f"قراءات متنافسة: {claim.payload.possible_readings}"))
        return Verdict(
            Sink.RESIDUAL, _band_for(claim.kind), Rank.PLAUSIBLE, tuple(trace),
            residual_kind=ResidualKind.COMPETING_CLAIM,
        )
    trace.append(TraceEntry(step, "residual", "هل بقيت احتمالات؟", True,
                            "لا احتمالات متنافسة غير محسومة"))

    # ── All gates cleared AND evidence present → Licensed.
    step += 1
    trace.append(TraceEntry(step, "closure",
                            "هل اجتازت كلّ البوابات برخصة؟", True,
                            "كلّ البوابات مرخّصة، والدليل حاضر"))
    return Verdict(Sink.LICENSED, _band_for(claim.kind), claim.claimed_rank, tuple(trace))


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
