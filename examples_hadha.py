"""
Example 3 — هذا → Blocked  (runnable demonstration)
Applies the frozen constitution. Builds the claim, runs the qadih gate,
prints the verdict + trace.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from src.contract.claim import JudgmentClaim, ClaimKind, IsmIsharaPayload
from src.contract.layers import ClaimBand
from src.contract.ranks import Rank
from src.contract.sinks import Sink
from src.engine.qadih_gate import evaluate

# المدخل: «هذا أفضلُ» — دعوى اشتقاق فاعليّة من اسم إشارة (نوع نص فكري)
claim = JudgmentClaim(
    claim_id="hadha-ex3",
    band=ClaimBand.SYNTACTIC,
    kind=ClaimKind.ISM_ISHARA,
    payload=IsmIsharaPayload(surface="هذا", deictic_class="near-singular-masc"),
    claimed_status=Sink.LICENSED,   # المُدَّعِي يزعم بلوغ الترخيص عبر اشتقاق
    claimed_rank=Rank.STRONG,
)

print("=" * 60)
print("المدخل:  الكلمة = هذا  |  النوع المُدَّعى = IsmIshara")
print("         الحالة المُدَّعاة = Licensed (اشتقاق فاعليّة)")
print("=" * 60)
verdict = evaluate(claim)
print(verdict.render())
print("=" * 60)
assert verdict.sink == Sink.BLOCKED, "expected Blocked"
print("النتيجة المتوقَّعة: ممنوع (Blocked) عبر بوابة الفرق القادح ✓")
