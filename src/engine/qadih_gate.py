"""
Engine :: Qadih-Difference Gate (اختبار الفرق القادح)
====================================================
Applies the constitution — does not amend it. Blocks a claim when the claimed
KIND's ontological class is incompatible with the derivation it asserts:

    "لا قياس بين مشغّل إحالة وأصل حدثي"
    (no analogy between a reference-anchor and an event-origin)

The gate itself knows NO specific words. It reads two catalogs (data):
    - kind_ontology.yaml : kind → {derivational | referential}
    - deictics.yaml      : which surfaces are closed-class demonstratives

Example 3: هذا is IsmIshara → referential. Claiming derived agency from it is
analogy across an invalidating difference → BLOCKED at this gate.
"""
from __future__ import annotations
import os
import yaml

from src.contract.claim import JudgmentClaim, ClaimKind, IsmIsharaPayload
from src.contract.layers import Layer
from src.contract.ranks import Rank
from src.contract.sinks import Sink
from src.engine.verdict import Verdict, TraceEntry

GATE_ID = "qadih.difference.referential_vs_derivational"
_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data", "catalogs")


def _load(name: str) -> dict:
    with open(os.path.join(_DATA, name), encoding="utf-8") as f:
        return yaml.safe_load(f)


def evaluate(claim: JudgmentClaim) -> Verdict:
    """
    Run the qadih-difference gate on a claim.
    Returns a Verdict — Blocked if the claimed derivation crosses the
    referential/derivational divide; otherwise a pass-through trace entry.
    """
    ontology = _load("kind_ontology.yaml")["kind_class"]
    trace: list[TraceEntry] = []

    # Step 1 — read the ontological class of the claimed kind (from data).
    kind_class = ontology.get(claim.kind.value)
    trace.append(TraceEntry(
        step=1, gate_id=GATE_ID,
        question="ما الجنس الأنطولوجيّ للنوع المُدَّعى؟ (derivational/referential)",
        passed=True,
        note=f"{claim.kind.value} → {kind_class}",
    ))

    # Step 2 — a referential anchor cannot license a derivational (agency) reading.
    #   claimed_status Licensed means the claimant asserts a derivational ascent.
    asserts_derivation = claim.claimed_status == Sink.LICENSED
    if kind_class == "referential" and asserts_derivation:
        reason = ("النوع المُدَّعى إحالةٌ مقاميّة (referential) لا أصلٌ حدثيّ؛ "
                  "اشتقاق فاعليّةٍ منه قياسٌ فاسدٌ عبر فرقٍ قادح "
                  "(لا قياس بين مشغّل إحالة وأصل حدثي).")
        trace.append(TraceEntry(
            step=2, gate_id=GATE_ID,
            question="هل يُقاس مشغّل الإحالة على الأصل الحدثيّ؟",
            passed=False,
            note="فرقٌ قادح: referential ↛ derivational",
        ))
        return Verdict(
            sink=Sink.BLOCKED,
            band_reached=Layer.SURFACE,   # blocked below word-capability-as-event
            rank=Rank.NONE,
            trace=tuple(trace),
            block_reason=reason,
            offending_gate=GATE_ID,
        )

    # Otherwise: this gate does not block. (Full ascent is other gates' job.)
    trace.append(TraceEntry(
        step=2, gate_id=GATE_ID,
        question="هل يوجد فرقٌ قادح يمنع القياس؟",
        passed=True,
        note="لا فرق قادح عند هذه البوابة",
    ))
    return Verdict(
        sink=Sink.DEFERRED,   # this gate alone can't license; downstream gates pending
        band_reached=Layer.SURFACE,
        rank=Rank.NONE,
        trace=tuple(trace),
    )
