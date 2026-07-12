# Output contracts

## Selection output

- `status`: `awaiting-user-selection`, `awaiting-manual-selection`, or `awaiting-valid-system-selection`.
- Candidate ID/name, score, matched needs, unmatched needs, and risks.
- Preview URL or confirmation that it was opened.
- One explicit question asking the user to select or revise constraints.

No design or implementation output belongs in the same response.

## Conflict output

- Selected system and asset version.
- Conflict list with requirement, rule evidence, and concrete risk.
- Reliable alternatives and reasons, or an honest empty alternative result plus preview URL.
- Four decisions: switch, keep, adjust, other.
- `status=awaiting-user-decision`.

## New design output

- Confirmed system, scope, and implemented states.
- Rule-to-decision evidence summary.
- Validation and degraded-check summary.
- ComplianceReport.

## Redesign output

- Baseline and preserved behavior.
- Changed files/components and before/after summary.
- Validation, approved deviations, and unresolved findings.
- ComplianceReport.

## Audit output

Each finding contains severity, rule ID, target evidence, violation reason, repair recommendation, confidence, and verification status. Before approval, `status=review-required`, `diffSummary.after=null`, and `diffSummary.modified=false`.

End report-first audit output with `status=awaiting-repair-approval` and a request to approve all or named findings.

## Verification labels

- `verified`: directly checked by a reliable tool or exact source evidence.
- `agent-judgment`: semantic evaluation that requires Agent reasoning.
- `degraded-unverified`: intended check could not be completed.
- `user-approved-deviation`: the user accepted a documented departure and its impact.

## Error output

Name the failing local path or JSON field path, explain the blocked capability, state what remains safe to do, and stop at the relevant gate. Do not replace missing evidence with assumptions.

## Completion

An output is complete when it has the required state, evidence slots, decision request, and verification labels for its mode.
