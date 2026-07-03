"""
Phase 0 — Contract :: Ranks (الرتبة)
====================================
FORBIDDEN OUTPUT: any pricing logic (that is Phase 4).
Declares the rank scale only. The invariant K ≤ evidence is enforced
elsewhere (Phase 4/5), never here.

Mathematical contract (Fork A):
    Rank is a totally ordered scale, 0..5.
        0 None | 1 Weak | 2 Plausible | 3 Probable | 4 Strong | 5 Certain
    (مستنتج — working scale; the source docs fix the ORDER "K ≤ evidence",
     not these specific numeric labels. Numbers are provisional until Phase 4.)

    A verdict carries two ranks:
        claimed_rank  — asserted by the claimant
        earned_rank   — computed by the descent
    Over-claim  :⟺  claimed_rank > earned_rank      (the core تحقيقي signal)

STATUS: filled (Phase 0). Scale only — no cost logic.
"""
from __future__ import annotations
from enum import IntEnum


class Rank(IntEnum):
    """Ordered evidential rank. IntEnum so comparisons (K ≤ evidence) are total."""
    NONE = 0
    WEAK = 1
    PLAUSIBLE = 2
    PROBABLE = 3
    STRONG = 4
    CERTAIN = 5

    def __str__(self) -> str:  # readable trace output
        return self.name.capitalize()
