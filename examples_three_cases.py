#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The three use-cases through the general descent harness — HONEST outputs.
Run from project root:  python3 examples_three_cases.py
No HR2S import. The verifier alone adjudicates.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from src.contract.claim import (
    JudgmentClaim, ClaimKind,
    IsmFaelPayload, IsmMakanPayload, IsmIsharaPayload,
)
from src.contract.layers import ClaimBand
from src.contract.ranks import Rank
from src.contract.sinks import Sink
from src.descent.harness import descend


def show(title, claim):
    print("=" * 64)
    print(title)
    print("=" * 64)
    v = descend(claim)
    print(v.render())
    print()
    return v


# ── الحالة البسيطة: هذا + دعوى اشتقاق فاعليّة → Blocked (referential ↛ derivational)
show("الحالة البسيطة — هذا (دعوى اشتقاق) → متوقّع: Blocked",
    JudgmentClaim("c-hadha", ClaimBand.SYNTACTIC, ClaimKind.ISM_ISHARA,
                  IsmIsharaPayload("هذا", "near-singular-masc"),
                  Sink.LICENSED, Rank.STRONG))

# ── الحالة الوسط: مَضرِب بقراءات متنافسة → Residual  (لا نُرغمها على Licensed)
show("الحالة الوسط — مَضرِب (قراءات متنافسة) → متوقّع: Residual",
    JudgmentClaim("c-madrib", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_MAKAN,
                  IsmMakanPayload("ض ر ب", "مَفعِل",
                                  possible_readings=("makan", "zaman"),
                                  surface="مَضرِب"),
                  Sink.RESIDUAL, Rank.PROBABLE))

# ── الحالة الكبيرة: ضارب دعوى ترخيص → Licensed (الجذر والوزن مشهودان في الكتالوجات الدنيا)
show("الحالة الكبيرة — ضارب (دعوى Licensed رتبة عالية) → متوقّع: Licensed",
    JudgmentClaim("c-darib", ClaimBand.MORPHOLOGICAL, ClaimKind.ISM_FAEL,
                  IsmFaelPayload("ض ر ب", "فاعل", surface_pattern="ضارب"),
                  Sink.LICENSED, Rank.STRONG))

print("#" * 64)
print("القاعدة: الصندوق يُخرج الصادق حسب الدليل المتاح — لا Licensed بلا دليل.")
