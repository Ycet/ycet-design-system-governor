# Design consistency audit

## Inputs

- Confirmed design system and reviewed DesignRuleBundle.
- Target project, page, screenshots, URL, or design file.
- Declared access status for each input.

## Report-first audit

1. Record the target baseline without editing it.
2. Run `python scripts/audit_static.py --project <project> --bundle <bundle.json> --output <report.json>` when code is accessible.
3. Review hierarchy, visual semantics, content fit, responsive behavior, interaction states, and accessibility evidence that static checks cannot decide.
4. Deduplicate findings while retaining the strongest source and target evidence.
5. Assign severity, rule ID, actual evidence, reason, repair advice, confidence, and verification status.
6. Deliver the report with `diffSummary.modified=false`.

## Mandatory repair gate

After the report, set state `awaiting-repair-approval` and stop. The user may approve all findings, approve named findings, decline, or request a revised scope. Approval written before findings existed is not valid repair-scope approval.

## Repair after approval

1. Convert the user response into an explicit list of approved finding IDs.
2. Modify only that list.
3. Re-run applicable checks.
4. Update the difference summary and preserve declined findings.

## Severity

- `critical`: blocks core use, safety, or essential accessibility.
- `high`: violates a strong rule or materially harms usability/brand.
- `medium`: clear inconsistency with bounded impact.
- `low`: preference or polish issue with limited impact.

## Error paths

- Unreadable input: create a degraded finding or disclose the skipped check.
- No reliable target evidence: do not assert a violation.
- Conflict between requested repair and system: use the conflict gate.

## Completion

Audit-only work completes when the report is delivered and the repair gate is waiting or declined. Repair work completes only after approved findings are fixed and revalidated.
