"""
Engine :: Verdict + Trace  (minimal surface for Example 3)
==========================================================
Applies the constitution's four-sink doctrine. Does NOT amend it.

A Verdict is the box's output object:
    { sink, band_reached, rank, trace, block_reason?, offending_gate?, residual_kind? }

Constitutional obligations honoured here (declaration only — enforcement is per gate):
    - every outcome lands in exactly one Sink
    - no result without a trace (لا حكم بلا دليل)
    - block carries WHERE and WHY (offending_gate + block_reason)
"""
from __future__ import annotations
from dataclasses import dataclass, field

from src.contract.layers import Layer
from src.contract.ranks import Rank
from src.contract.sinks import Sink, ResidualKind


@dataclass(frozen=True)
class TraceEntry:
    """One ordered step in the descent. The trace is part of the output."""
    step: int
    gate_id: str
    question: str          # the license-question asked at this gate
    passed: bool
    note: str = ""

    def __str__(self) -> str:
        mark = "✓" if self.passed else "✗"
        return f"[{self.step}] {mark} {self.gate_id}: {self.note}"


@dataclass(frozen=True)
class Verdict:
    sink: Sink
    band_reached: Layer
    rank: Rank
    trace: tuple[TraceEntry, ...]
    block_reason: str | None = None
    offending_gate: str | None = None
    residual_kind: ResidualKind | None = None

    def __post_init__(self):
        # Constitutional guard: a Blocked verdict MUST say where and why.
        if self.sink == Sink.BLOCKED and (not self.block_reason or not self.offending_gate):
            raise ValueError("Blocked verdict must carry offending_gate + block_reason")
        # Constitutional guard: no result without a trace.
        if not self.trace:
            raise ValueError("no verdict without a trace (لا حكم بلا دليل)")

    def render(self) -> str:
        lines = [f"الحالة (Sink):        {self.sink}",
                 f"الطبقة المبلوغة:      {self.band_reached}",
                 f"الرتبة (Rank):        {self.rank}"]
        if self.offending_gate:
            lines.append(f"البوابة القادحة:      {self.offending_gate}")
        if self.block_reason:
            lines.append(f"سبب المنع:            {self.block_reason}")
        if self.residual_kind:
            lines.append(f"نوع البقايا:          {self.residual_kind}")
        lines.append("الأثر (Trace):")
        lines += [f"    {t}" for t in self.trace]
        return "\n".join(lines)
