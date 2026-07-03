"""
Phase 0 — Contract :: Closure Invariant TYPES (صمّاء فقط)
========================================================
FORBIDDEN OUTPUT: any check execution. Per the architectural decision,
Phase 0 only DECLARES that closure-criteria exist. It does NOT run them.
Execution lives in src/validation/invariants.py (Phase 5).

This file holds the META-level vocabulary (about system soundness), kept
strictly separate from object-level judgment (layers.py, claim.py).

Types to declare:
    ClosureCriterion   — a named acceptance criterion
    InvariantCheck     — a criterion + the run it applies to
    InvariantResult    — pass/fail + reason (no logic to produce it yet)

The eight Implementation Criteria (names only, defined in Phase 5):
    TypedInput | TypedClaim | ExplicitLayer | LicensedPath
    | TraceCompleteness | RankBoundedness | SinkTotality | ForbiddenOutputSafety

These TRANSLATE your systemic self-criteria; they do not replace them.
Mapping lives in docs/closure_criteria.md.

STATUS: stub. Deaf declarations only — no execution in Phase 0.
"""
# TODO(Phase0): declare ClosureCriterion, InvariantCheck, InvariantResult (inert)
