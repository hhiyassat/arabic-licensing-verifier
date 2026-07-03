"""
Phase 0 — Contract :: Aggregator
================================
FORBIDDEN OUTPUT: any logic. This module re-exports the contract surface once
the split modules are filled. It declares NOTHING on its own.

The contract is decomposed (per architectural decision) into:
    claim.py      — JudgmentClaim, ClaimKind, ClaimPayload      (object-level)
    layers.py     — Layer (ordered judgment chain)              (object-level)
    ranks.py      — Rank scale                                   (object-level)
    sinks.py      — Sink + per-sink payloads                     (object-level)
    evidence.py   — Evidence                                     (object-level)
    events.py     — TraceEvent, FailureKind, VersionStamp        (support)
    invariants.py — ClosureCriterion, InvariantResult (DEAF)     (META-level)
    pk0.py        — the six Built-in-OS categories               (boot data)

Object-level (judging Arabic) is kept strictly apart from meta-level
(judging the machine). See docs/closure_criteria.md.

STATUS: stub. Re-exports wired in Phase 0 once members exist.
"""
# TODO(Phase0): from .claim import *  ; from .layers import * ; ... (when filled)
