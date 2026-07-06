# P5 Claim Bridge Constitution — دستور جسر الدعوى

> Status: local, living, non-frozen.
> Scope: P5 only. This document does not amend the frozen verifier constitution.

## Purpose

The P5 Claim Bridge prepares verifier input drafts.

It does not license claims.
It does not prove morphology.
It does not issue final judgments.
Only the Arabic Licensing Verifier may produce:

```text
Licensed
Blocked
Deferred
Residual
```

## Three Components

### Entrance Adapter

The Entrance Adapter prepares surface-level candidate material and may carry
explicit catalog-attested metadata:

```text
surface
kind candidate, if present in metadata
root candidate, if present in metadata
wazn candidate, if present in metadata
trace
raw catalog evidence
```

It never produces a final sink.
It never says Licensed, Verified, Final, proved, or adjudicated.

### P5 Claim Bridge

The P5 Claim Bridge converts explicit candidate material into verifier input drafts.

It may produce `VerifierInputDraft` objects with one of these statuses:

```text
Candidate
DeferredToVerifier
ResidualCandidate
```

It must preserve entrance evidence and trace.
It must read kind/root/wazn only from entrance metadata or explicit candidate fields.
It must not assign kind/root/wazn by surface matching.
If no explicit candidate metadata is present, it must produce a Generic draft
deferred to the verifier.
It must not promote candidate material into a final judgment.

### Arabic Licensing Verifier

The verifier receives a `JudgmentClaim`.
It alone adjudicates the claim.
It alone returns the final sink:

```text
Licensed | Blocked | Deferred | Residual
```

## Forbidden In P5

The bridge must not contain fields or outputs named:

```text
Licensed
final_verdict
final_sink
proved
verified
```

## Current Minimal Baseline

This bridge is intentionally narrow. It is a converter only.

It does not implement general Arabic morphology.
It does not infer universal roots or awzan.
It does not import H2RS, HR2S, Qiyas, or external project code.

H2RS-derived artifacts may remain catalog provenance only.
