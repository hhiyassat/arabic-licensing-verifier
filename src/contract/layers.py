"""
Phase 0 — Contract :: Layers (طبقات الحكم)
==========================================
FORBIDDEN OUTPUT: any logic. Declares the ORDERED judgment layers only.
These are OBJECT-LEVEL (they judge Arabic). They are NOT implementation
criteria (meta-level, in invariants.py) and NOT PK0 categories (boot data).

Mathematical contract (Fork A):
    Layer is a totally ordered chain. The descent moves DOWNWARD
    (from Hukm toward Trace) seeking a preserved origin (أصل).

    Full descent chain (منقول, foundation doc §1-4):
        Trace < Carrier < LetterHaraka < Syllable < Surface
              < RootZiyada < Wazn < Masdar < Role
              < Relation < Ifadah < Hukm

    Working claim-layer taxonomy (مستنتج — the coarse bands a claim targets):
        Surface < Lexical < Morphological < Syntactic
                < Semantic < Rhetorical < UsulFiqh

    Both are exposed; the fine chain is the ground truth, the coarse bands
    are a convenience view used by claim.layer.

STATUS: filled (Phase 0). Ordered declarations only.
"""
from __future__ import annotations
from enum import IntEnum


class Layer(IntEnum):
    """
    Fine-grained ordered descent chain (منقول §1-4).
    Lower value = closer to the preserved origin (أصل).
    Higher value = closer to the final judgment (Hukm).
    """
    TRACE = 0
    CARRIER = 1
    LETTER_HARAKA = 2
    SYLLABLE = 3
    SURFACE = 4
    ROOT_ZIYADA = 5
    WAZN = 6
    MASDAR = 7
    ROLE = 8
    RELATION = 9
    IFADAH = 10
    HUKM = 11

    def __str__(self) -> str:
        return self.name.replace("_", "/").title()


class ClaimBand(IntEnum):
    """
    Coarse claim-targeting bands (مستنتج). Used by JudgmentClaim.layer as a
    human-facing grouping. Maps onto ranges of the fine Layer chain.
    """
    SURFACE = 0
    LEXICAL = 1
    MORPHOLOGICAL = 2
    SYNTACTIC = 3
    SEMANTIC = 4
    RHETORICAL = 5
    USUL_FIQH = 6

    def __str__(self) -> str:
        return self.name.replace("_", "-").title()
