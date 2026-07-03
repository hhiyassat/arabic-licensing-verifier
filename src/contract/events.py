"""
Phase 0 — Contract :: TraceEvent, FailureKind, VersionStamp
===========================================================
FORBIDDEN OUTPUT: any logic. Typed vocabulary so the trace is auditable
from day one.

TraceEvent (مستنتج, per critique):
    { event_type, layer, gate_id, input_snapshot,
      evidence, rank_before, rank_after, sink, reason }

FailureKind:
    MissingEvidence | RankOverclaim | ScopeMismatch
    | ResidualUnresolved | ManiPresent
    | ForbiddenOutputViolation | UnknownGate

VersionStamp (audit/funding requirement):
    { engine_version, gate_table_version,
      catalog_version, rank_pricing_version }

STATUS: stub. Declarations only.
"""
# TODO(Phase0): declare TraceEvent, FailureKind, VersionStamp
