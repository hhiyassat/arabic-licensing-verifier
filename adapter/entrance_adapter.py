#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrance Adapter — P1–P4 only  (arabic_verifier)
================================================
Standalone. This is NOT H2RS and NOT Qiyas. H2RS knowledge is used only as
METHODOLOGY: candidate-only, trace, rank, residuals, no silent success/failure.
No import of, or dependency on, any H2RS or Qiyas code.

Governed by ENTRANCE_ADAPTER_CONSTITUTION.md:
    "المِهْيَع يُحضّر المرشّحات، ولا يُرخّص الأحكام."
    Entrance Adapter prepares candidates; it does not license judgments.

SCOPE (hard limits):
    P1_NORMALIZED_SURFACE  — surface normalization only
    P2_TOKEN_CANDIDATE     — whitespace/punctuation tokenization only
    P3_SLOT_GEOMETRY        — CV/slot geometry only (approximate, conservative)
    P4_CATALOG_MATCH        — catalog attestation only (mabniyat / operators)

FINAL OUTPUT of this script: EntranceRecord ONLY.
    - NOT ClaimCandidate  (that is P5 — not implemented here)
    - NOT a verifier verdict  (that is the box — not implemented here)

FORBIDDEN (never computed or claimed anywhere below):
    root · wazn · bab · iʿrab · syntactic role · relations · meaning ·
    truth · hukm · tafsir · Licensed status
Any such fields present in CSV rows stay as RAW catalog metadata only;
they are never promoted into computed conclusions.

Allowed output vocabulary:  catalog_attested · candidate · generic_surface
                            · residual_candidate · deferred_to_verifier
Forbidden output vocabulary: licensed · verified · final · proven_judgment
                            · official_qiyas_layer · official_hr2s_layer
"""
from __future__ import annotations

import csv
import os
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════
# Allowed status vocabulary (constitutional — nothing beyond candidate level)
# ═══════════════════════════════════════════════════════════════════════════
STATUS_CATALOG_ATTESTED = "catalog_attested"
STATUS_CANDIDATE = "candidate"
STATUS_GENERIC_SURFACE = "generic_surface"
STATUS_RESIDUAL_CANDIDATE = "residual_candidate"
STATUS_DEFERRED_TO_VERIFIER = "deferred_to_verifier"
STATUS_NO_CATALOG_MATCH = "no_catalog_match"

_ALLOWED_STATUSES = {
    STATUS_CATALOG_ATTESTED, STATUS_CANDIDATE, STATUS_GENERIC_SURFACE,
    STATUS_RESIDUAL_CANDIDATE, STATUS_DEFERRED_TO_VERIFIER,
    STATUS_NO_CATALOG_MATCH,
}
# Rank here is a methodological confidence marker, NOT a licensing rank.
RANK_NONE = "none"
RANK_CATALOG_ATTESTED = "catalog_attested"


# ═══════════════════════════════════════════════════════════════════════════
# Trace — no silent success/failure. Every phase records what it did.
# ═══════════════════════════════════════════════════════════════════════════
@dataclass
class TraceEvent:
    phase: str          # P1 / P2 / P3 / P4
    action: str
    detail: str
    ok: bool = True

    def __str__(self) -> str:
        mark = "✓" if self.ok else "·"
        return f"{mark} [{self.phase}] {self.action}: {self.detail}"


# ═══════════════════════════════════════════════════════════════════════════
# P1 — NORMALIZED_SURFACE  (surface normalization only; no root/wazn/meaning)
# ═══════════════════════════════════════════════════════════════════════════
_ARABIC_DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")  # harakat + tatweel(0640)
_TATWEEL = "\u0640"


@dataclass
class NormalizedSurface:
    original_surface: str
    normalized_surface: str
    undiacritized_surface: str
    trace: list[TraceEvent] = field(default_factory=list)


def p1_normalize(text: str) -> NormalizedSurface:
    trace: list[TraceEvent] = []
    original = text
    trace.append(TraceEvent("P1", "preserve", f"original_surface kept ({len(original)} chars)"))

    # Unicode NFC (compose), conservative.
    s = unicodedata.normalize("NFC", text)

    # Remove tatweel.
    if _TATWEEL in s:
        s = s.replace(_TATWEEL, "")
        trace.append(TraceEvent("P1", "remove_tatweel", "tatweel removed"))
    else:
        trace.append(TraceEvent("P1", "remove_tatweel", "no tatweel present"))

    # Unify whitespace runs to single spaces; strip ends.
    before = s
    s = re.sub(r"\s+", " ", s).strip()
    trace.append(TraceEvent("P1", "unify_spaces",
                            "whitespace collapsed" if before != s else "spacing already clean"))

    # Cautious alif normalization: أ إ آ ٱ → ا  (surface only; reversible info kept in original)
    normalized = s
    alif_variants = "أإآٱ"
    if any(ch in normalized for ch in alif_variants):
        normalized = re.sub(r"[أإآٱ]", "ا", normalized)
        trace.append(TraceEvent("P1", "normalize_alif", "alif-variants folded to bare alif (cautious)"))
    else:
        trace.append(TraceEvent("P1", "normalize_alif", "no alif-variants"))

    # Undiacritized form = normalized minus harakat.
    undiacritized = _ARABIC_DIACRITICS.sub("", normalized)
    trace.append(TraceEvent("P1", "undiacritize", "harakat stripped for undiacritized_surface"))

    return NormalizedSurface(
        original_surface=original,
        normalized_surface=normalized,
        undiacritized_surface=undiacritized,
        trace=trace,
    )


# ═══════════════════════════════════════════════════════════════════════════
# P2 — TOKEN_CANDIDATE  (whitespace + punctuation only; NO morphological seg)
#   - does NOT split بِ/لِ/وَ from the word
# ═══════════════════════════════════════════════════════════════════════════
# Punctuation that separates tokens. Note: we do NOT treat Arabic letters,
# nor prefixes بِ/لِ/وَ, as separators — those stay attached (constitutional).
_PUNCT = r"[\s،؛؟!.,:;\"'()\[\]{}«»…]+"


@dataclass
class TokenCandidate:
    index: int
    token_original: str      # slice of original (as normalized-surface token)
    token_normalized: str
    token_undiacritized: str
    char_start: int
    char_end: int
    trace: list[TraceEvent] = field(default_factory=list)


def p2_tokenize(norm: NormalizedSurface) -> list[TokenCandidate]:
    text = norm.normalized_surface
    tokens: list[TokenCandidate] = []
    idx = 0
    for m in re.finditer(rf"(?:(?!{_PUNCT}).)+", text):
        piece = m.group(0)
        if not piece.strip():
            continue
        undiac = _ARABIC_DIACRITICS.sub("", piece)
        tr = [TraceEvent("P2", "token",
                         f"'{piece}' at [{m.start()}:{m.end()}] (no morph split, prefixes kept)")]
        tokens.append(TokenCandidate(
            index=idx,
            token_original=piece,
            token_normalized=piece,
            token_undiacritized=undiac,
            char_start=m.start(),
            char_end=m.end(),
            trace=tr,
        ))
        idx += 1
    if not tokens:
        # no silent failure: record the emptiness explicitly
        tokens = []
    return tokens


# ═══════════════════════════════════════════════════════════════════════════
# P3 — SLOT_GEOMETRY  (CV / cells only; approximate & conservative)
#   - NO root, NO wazn, NO bab
#   - if nothing is established → UNKNOWN + residual
# ═══════════════════════════════════════════════════════════════════════════
_ARABIC_LETTER = re.compile(r"[\u0621-\u064A]")
_HARAKA = re.compile(r"[\u064B-\u0652\u0670]")
# Long vowels (letters acting as vowels): ا و ي
_LONG_VOWEL_LETTERS = set("اوي")
CELL_TYPES = {"CV", "CVV", "CVC", "CVVC", "CVCC", "CVVCC", "UNKNOWN"}


@dataclass
class SlotGeometry:
    token_index: int
    letters: list[str]
    cv_pattern: str
    cells: list[str]
    has_unknown: bool
    residual: str | None
    trace: list[TraceEvent] = field(default_factory=list)


def _cv_skeleton(piece: str) -> tuple[list[str], str, list[TraceEvent]]:
    """
    Build a conservative CV skeleton. Consonant = C, vowel(short/long) = V.
    This is a SURFACE approximation only — it asserts no morphology.
    """
    trace: list[TraceEvent] = []
    letters = _ARABIC_LETTER.findall(piece)
    cv = []
    i = 0
    # Walk char by char, attaching harakat to preceding letter where possible.
    chars = list(piece)
    j = 0
    while j < len(chars):
        ch = chars[j]
        if _ARABIC_LETTER.match(ch):
            if ch in _LONG_VOWEL_LETTERS:
                cv.append("V")  # long vowel letter → V (conservative)
            else:
                cv.append("C")
                # look ahead: a following haraka means C+V
                if j + 1 < len(chars) and _HARAKA.match(chars[j + 1]):
                    cv.append("V")
                    j += 1  # consume haraka
            j += 1
        else:
            j += 1  # skip non-letters silently at skeleton level
    cv_pattern = "".join(cv)
    trace.append(TraceEvent("P3", "cv_skeleton",
                            f"letters={len(letters)} → cv='{cv_pattern}' (surface approx)"))
    return letters, cv_pattern, trace


def _cells_from_cv(cv_pattern: str) -> tuple[list[str], bool, str | None, TraceEvent]:
    """
    Segment a CV string into known cells greedily by longest match.
    Anything unresolved → UNKNOWN cell + residual.
    """
    ordered = ["CVVCC", "CVCC", "CVVC", "CVC", "CVV", "CV"]
    cells: list[str] = []
    i = 0
    unknown = False
    n = len(cv_pattern)
    while i < n:
        matched = None
        for cand in ordered:
            if cv_pattern.startswith(cand, i):
                matched = cand
                break
        if matched:
            cells.append(matched)
            i += len(matched)
        else:
            cells.append("UNKNOWN")
            unknown = True
            i += 1
    residual = None
    if unknown or not cells:
        residual = f"unresolved_cv:'{cv_pattern}'"
    ev = TraceEvent("P3", "cells",
                    f"cells={cells}" + (f" | residual={residual}" if residual else ""),
                    ok=not unknown)
    return (cells if cells else ["UNKNOWN"]), unknown, residual, ev


def p3_slot_geometry(tok: TokenCandidate) -> SlotGeometry:
    trace: list[TraceEvent] = []
    letters, cv_pattern, tr1 = _cv_skeleton(tok.token_normalized)
    trace.extend(tr1)
    if not letters:
        # nothing established → UNKNOWN + residual (no silent failure)
        ev = TraceEvent("P3", "cells", "no Arabic letters → UNKNOWN", ok=False)
        trace.append(ev)
        return SlotGeometry(tok.index, letters, "", ["UNKNOWN"], True,
                            "no_arabic_letters", trace)
    cells, unknown, residual, ev = _cells_from_cv(cv_pattern)
    trace.append(ev)
    return SlotGeometry(tok.index, letters, cv_pattern, cells, unknown, residual, trace)


# ═══════════════════════════════════════════════════════════════════════════
# P4 — CATALOG_MATCH  (attestation only; NO ClaimCandidate, NO judgment)
#   - match via original / normalized / undiacritized
#   - no match → residual / no_catalog_match  (never a verdict)
# ═══════════════════════════════════════════════════════════════════════════
_CATALOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalogs")


def _load_catalog(filename: str) -> list[dict[str, str]]:
    path = os.path.join(_CATALOG_DIR, filename)
    rows: list[dict[str, str]] = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


@dataclass
class CatalogEvidence:
    token_index: int
    status: str                 # catalog_attested | no_catalog_match
    catalog: str | None         # mabniyat | operators
    matched_on: str | None      # original | normalized | undiacritized
    # RAW catalog metadata — carried verbatim, NEVER promoted to a conclusion:
    raw_metadata: dict[str, str] = field(default_factory=dict)
    residual: str | None = None
    rank: str = RANK_NONE
    trace: list[TraceEvent] = field(default_factory=list)

    def __post_init__(self):
        assert self.status in _ALLOWED_STATUSES, f"forbidden status: {self.status}"


def _match_row(tok: TokenCandidate, rows: list[dict[str, str]]) -> tuple[dict | None, str | None]:
    """Try matching on original, then normalized, then undiacritized."""
    keys = [
        ("original", tok.token_original),
        ("normalized", tok.token_normalized),
        ("undiacritized", tok.token_undiacritized),
    ]
    for how, value in keys:
        for row in rows:
            if value == row.get("surface") or value == row.get("undiacritized"):
                return row, how
    return None, None


def p4_catalog_match(tok: TokenCandidate,
                     mabniyat: list[dict], operators: list[dict]) -> CatalogEvidence:
    trace: list[TraceEvent] = []

    for cat_name, rows in (("mabniyat", mabniyat), ("operators", operators)):
        row, how = _match_row(tok, rows)
        if row:
            # Carry the row as RAW metadata. We do NOT interpret category as a
            # computed conclusion — it is attestation metadata only.
            trace.append(TraceEvent("P4", "match",
                                    f"'{tok.token_normalized}' attested in {cat_name} via {how}"))
            return CatalogEvidence(
                token_index=tok.index,
                status=STATUS_CATALOG_ATTESTED,
                catalog=cat_name,
                matched_on=how,
                raw_metadata=dict(row),          # verbatim, not promoted
                residual=None,
                rank=RANK_CATALOG_ATTESTED,
                trace=trace,
            )

    # No match anywhere → residual / no_catalog_match (no silent failure, no verdict)
    trace.append(TraceEvent("P4", "no_match",
                            f"'{tok.token_normalized}' not in any catalog", ok=False))
    return CatalogEvidence(
        token_index=tok.index,
        status=STATUS_NO_CATALOG_MATCH,
        catalog=None,
        matched_on=None,
        raw_metadata={},
        residual=f"no_catalog_match:'{tok.token_normalized}'",
        rank=RANK_NONE,
        trace=trace,
    )


# ═══════════════════════════════════════════════════════════════════════════
# EntranceRecord — the ONLY final output of this script (NOT ClaimCandidate)
# ═══════════════════════════════════════════════════════════════════════════
@dataclass
class TokenEntrance:
    token: TokenCandidate
    geometry: SlotGeometry
    evidence: CatalogEvidence


@dataclass
class EntranceRecord:
    surface: NormalizedSurface
    tokens: list[TokenEntrance]
    # Downstream marker: everything here is prepared, nothing licensed.
    handoff: str = STATUS_DEFERRED_TO_VERIFIER

    def all_trace(self) -> list[TraceEvent]:
        events = list(self.surface.trace)
        for te in self.tokens:
            events += te.token.trace
            events += te.geometry.trace
            events += te.evidence.trace
        return events


def build_entrance_record(text: str) -> EntranceRecord:
    """Run P1 → P2 → P3 → P4 and assemble an EntranceRecord. No P5, no verifier."""
    norm = p1_normalize(text)                         # P1
    tokens = p2_tokenize(norm)                         # P2
    mabniyat = _load_catalog("mabniyat.csv")
    operators = _load_catalog("operators.csv")

    entrances: list[TokenEntrance] = []
    for tok in tokens:
        geom = p3_slot_geometry(tok)                   # P3
        ev = p4_catalog_match(tok, mabniyat, operators)  # P4
        entrances.append(TokenEntrance(token=tok, geometry=geom, evidence=ev))

    return EntranceRecord(surface=norm, tokens=entrances)


# ═══════════════════════════════════════════════════════════════════════════
# Rendering / demo
# ═══════════════════════════════════════════════════════════════════════════
def render(record: EntranceRecord) -> str:
    L = []
    s = record.surface
    L.append("EntranceRecord (P1–P4 only — NOT a ClaimCandidate, NOT a verdict)")
    L.append("=" * 64)
    L.append(f"original_surface     : {s.original_surface}")
    L.append(f"normalized_surface   : {s.normalized_surface}")
    L.append(f"undiacritized_surface: {s.undiacritized_surface}")
    L.append("-" * 64)
    for te in record.tokens:
        t, g, e = te.token, te.geometry, te.evidence
        L.append(f"[token {t.index}] '{t.token_normalized}'  @[{t.char_start}:{t.char_end}]")
        L.append(f"    P3 cv='{g.cv_pattern}' cells={g.cells}"
                 + (f" residual={g.residual}" if g.residual else ""))
        L.append(f"    P4 status={e.status}"
                 + (f" catalog={e.catalog} via {e.matched_on}" if e.catalog else "")
                 + (f" residual={e.residual}" if e.residual else ""))
        if e.raw_metadata:
            L.append(f"       raw_metadata (NOT a conclusion): {e.raw_metadata}")
    L.append("-" * 64)
    L.append(f"handoff: {record.handoff}")
    return "\n".join(L)


if __name__ == "__main__":
    samples = [
        "هذا أفضلُ",
        "الرجلُ في البيتِ",
        "ضارب",
    ]
    for smp in samples:
        rec = build_entrance_record(smp)
        print(render(rec))
        print("\nTRACE:")
        for ev in rec.all_trace():
            print("   ", ev)
        print("\n" + "#" * 64 + "\n")
