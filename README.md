# Arabic Licensing Verifier — الصندوق التحقيقي

A gate-based verifier that **adjudicates a claimed Arabic linguistic judgment**
by descending it to a preserved origin (أصل) through licensed transitions.
It is **validating, not generative**: it receives a claim and judges its
legitimacy — it does not invent meaning.

> Independent of H2RS / Qiyas. Any resemblance is methodological inspiration
> only — there is **no dependency on, or import of, H2RS or Qiyas code**.

---

## What it does

The box receives a *claimed judgment* about a word and returns an honest
verdict — one of four sinks, never a leap:

```
Licensed  — every gate cleared AND sufficient evidence present
Blocked   — a قادح (invalidating) preventer exists
Deferred  — a required gate or evidence is missing (no proven preventer)
Residual  — undecided competing possibilities remain, classified
```

The core rule: **no final judgment without every gate on the path licensing
it, and no rank that exceeds its evidence.** When evidence is absent, the
honest output is `Deferred` — the box never fabricates a `Licensed`.

## Signature

```
descend : JudgmentClaim → Verdict { sink, band, rank, trace, block_reason?, residual_kind? }

JudgmentClaim = (status, rank, band, kind, payload)      [five fields]
    payload is typed per kind (IsmFael | IsmMakan | IsmIshara)
    with a GenericPayload escape hatch that can NEVER reach Licensed.
```

## The three worked cases

| Input | Claim | Result (no catalogs) | Result (catalogs present) |
|-------|-------|----------------------|---------------------------|
| هذا | derive agency from a demonstrative | **Blocked** (referential ↛ derivational) | Blocked |
| مَضرِب | place-noun, competing readings | **Deferred** (missing roots/awzan) | **Residual** (competing) |
| ضارب | IsmFael, claim Licensed | **Deferred** (missing evidence) | **Licensed** |

Run them:
```bash
python3 examples_three_cases.py     # the three cases through the descent harness
python3 examples_hadha.py           # the single-gate هذا → Blocked demo
python3 -m pytest -q                # 23 passed, 3 skipped
```

## Layout

```
docs/
  constitution.md                 # الدستور — what must be (frozen)
  development_plan.md             # how it will be built (phases)
  closure_criteria.md             # systemic ↔ technical criteria pairing
  implementation_status.md        # what is actually built (living)
  theoretical_foundation.md       # the theory (نقل vs استنتاج)
  CONSTITUTION_FREEZE.md          # freeze record + fingerprints
  ENTRANCE_ADAPTER_CONSTITUTION.md# constitution of the entrance adapter
  PROJECT_PREAMBLE.md             # reader entry-point (non-binding)

src/
  contract/    # Phase 0 — types (claim, layers, ranks, sinks, evidence...)
  engine/      # verdict + qadih-difference gate
  descent/     # the general descent harness
  ...

adapter/       # Entrance Adapter (P1–P4): raw text → candidates (no judgment)
tests/         # contract / engine / descent / adapter / acceptance
```

## Two constitutions, kept apart

- **`constitution.md`** governs the verifier: the court that adjudicates.
- **`ENTRANCE_ADAPTER_CONSTITUTION.md`** governs the adapter that stands
  *before* it: it prepares candidates and hands off `deferred_to_verifier` —
  it never licenses. *The entrance prepares candidates; only the verifier
  adjudicates.*

The frozen documents are fingerprinted in `CONSTITUTION_FREEZE.md`; any change
to them is a recorded, deliberate decision — never silent.
