# Arabic Licensing Verifier  (الصندوق التحقيقي)

A gate-based engine that VALIDATES a claimed حكم by descending it to a preserved
origin (أصل) through licensed transitions. Built on four source documents;
theoretical basis in `theoretical_foundation.md`, plan in `docs/DEVELOPMENT_PLAN.md`.

## Path
Validating (تحقيقي) primary; generative engine underneath.

## Signature
    Θ_ar : (Input, PK0) → Verdict{ sink, layer, rank, trace, collapse_point? }
    Input carries a ClaimedJudgment = (status, rank, layer)   [Fork B]

## Governing invariant
No jump: no final حكم without every gate on the path licensing it.
Four sinks, nothing discarded: Licensed | Blocked | Deferred | Residual.

## Build order
See docs/DEVELOPMENT_PLAN.md — Phases 0→1→2, then 3‖4, then 5.
Every module's forbidden-output constraint is stated in its docstring.
