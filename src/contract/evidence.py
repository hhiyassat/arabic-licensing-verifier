"""
Phase 0 — Contract :: Evidence (الدليل)
=======================================
FORBIDDEN OUTPUT: any evaluation. Declares the shape of evidence only.

Rationale: the rule "no rank exceeds its evidence" is UNTESTABLE without a
first-class Evidence object. Required for audit/funding review:
"where did this license come from?"

Contract (مستنتج, per critique):
    Evidence := { source, kind, rank, scope, citation, confidence }
    source ∈ { catalog, rule, manual, lexicon, grammar_source,
               corpus_attestation, expert_annotation }

STATUS: stub. Declarations only.
"""
# TODO(Phase0): declare Evidence, EvidenceSource, EvidenceKind
