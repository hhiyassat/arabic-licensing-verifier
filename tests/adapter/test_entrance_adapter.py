"""P1–P4 entrance adapter :: scope + constitutional boundary tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "adapter"))

import entrance_adapter as ea


def test_p1_preserves_original_and_normalizes():
    r = ea.p1_normalize("هٰذاـــ  أفضلُ")
    assert r.original_surface == "هٰذاـــ  أفضلُ"      # original kept verbatim
    assert "ـ" not in r.normalized_surface              # tatweel removed
    assert "  " not in r.normalized_surface             # spaces unified
    assert all(d not in r.undiacritized_surface for d in "ًٌٍَُِّْ")  # harakat gone


def test_p2_does_not_split_prefixes():
    r = ea.p1_normalize("والبيت للرجل")
    toks = ea.p2_tokenize(r)
    # وَ and لِ prefixes must stay attached — no morphological split
    assert toks[0].token_normalized == "والبيت"
    assert toks[1].token_normalized == "للرجل"
    assert len(toks) == 2


def test_p3_unknown_yields_residual():
    r = ea.p1_normalize("زخ")
    tok = ea.p2_tokenize(r)[0]
    g = ea.p3_slot_geometry(tok)
    # every cell type is from the allowed set
    assert all(c in ea.CELL_TYPES for c in g.cells)
    # if unknown, a residual must exist (no silent failure)
    if g.has_unknown:
        assert g.residual is not None


def test_p4_attested_carries_raw_metadata_not_conclusion():
    r = ea.p1_normalize("هذا")
    tok = ea.p2_tokenize(r)[0]
    mab = ea._load_catalog("mabniyat.csv")
    ops = ea._load_catalog("operators.csv")
    ev = ea.p4_catalog_match(tok, mab, ops)
    assert ev.status == ea.STATUS_CATALOG_ATTESTED
    # category is present ONLY as raw metadata, never as a promoted field
    assert "category" in ev.raw_metadata
    assert not hasattr(ev, "root") and not hasattr(ev, "wazn") and not hasattr(ev, "bab")


def test_p4_no_match_is_residual_not_verdict():
    r = ea.p1_normalize("زخشون")
    tok = ea.p2_tokenize(r)[0]
    ev = ea.p4_catalog_match(tok, ea._load_catalog("mabniyat.csv"),
                             ea._load_catalog("operators.csv"))
    assert ev.status == ea.STATUS_NO_CATALOG_MATCH
    assert ev.residual is not None


def test_no_forbidden_status_anywhere():
    """No output may carry licensed/verified/final/proven/official."""
    forbidden = {"licensed", "verified", "final", "proven_judgment",
                 "official_qiyas_layer", "official_hr2s_layer"}
    rec = ea.build_entrance_record("هذا في البيتِ ضارب")
    # collect every status string produced
    statuses = {te.evidence.status for te in rec.tokens} | {rec.handoff}
    assert statuses.isdisjoint(forbidden)
    # and every status is from the allowed vocabulary
    for te in rec.tokens:
        assert te.evidence.status in ea._ALLOWED_STATUSES


def test_final_output_is_entrance_record_not_claim():
    rec = ea.build_entrance_record("هذا")
    assert isinstance(rec, ea.EntranceRecord)
    # deferred handoff — nothing licensed here
    assert rec.handoff == ea.STATUS_DEFERRED_TO_VERIFIER
    # there is NO ClaimCandidate type in this module (P5 not implemented)
    assert not hasattr(ea, "ClaimCandidate")


def test_no_hukm_root_wazn_fields_on_outputs():
    """Forbidden computed fields must not exist on any output dataclass."""
    rec = ea.build_entrance_record("هذا في")
    for te in rec.tokens:
        for obj in (te.token, te.geometry, te.evidence):
            for banned in ("root", "wazn", "bab", "irab", "hukm", "meaning",
                           "role", "tafsir", "licensed"):
                assert not hasattr(obj, banned), f"{banned} leaked onto {type(obj).__name__}"
