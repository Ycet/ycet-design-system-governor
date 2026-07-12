# Conflict gates

## Trigger

A conflict exists when satisfying a preserved requirement would violate a reviewed system rule, or following the system would materially fail the audience, environment, brand, accessibility, performance, or implementation requirement.

Do not treat ordinary adaptation as conflict. A responsive layout change that the system permits is adaptation; hiding required focus states to preserve a visual effect is conflict.

## Required evidence

- Exact user requirement.
- Rule ID, evidence text, source file, and source location.
- Why both cannot be satisfied without a decision.
- Risk in one or more categories: visual, usability, brand, implementation.

## ConflictReport

For each conflict provide requirement, cited rule, and concrete risks. Then provide reliable alternative systems with evidence-based reasons. Offer exactly these decisions:

- `switch-system`
- `keep-current-system`
- `adjust-requirements`
- `other`

Set `status=awaiting-user-decision` and stop before edits.

## No reliable alternative

Do not invent an alternative. State that the reliable alternative list is empty, provide or open `https://open-design.ai/zh/plugins/systems/`, and ask whether to keep the system, adjust requirements, or make another decision.

## Decision handling

- Switch: confirm the replacement, compile its rules, and recheck all requirements.
- Keep: record an approved deviation containing the decision and impact.
- Adjust: update the SelectionProfile and rule comparison.
- Other: preserve the user’s decision verbatim and verify it resolves the conflict.

## Non-resolutions

Deadlines, senior approval, technical fallbacks, reduced blur, feature flags, and “use your judgment” do not resolve a conflict unless the user chooses an offered decision after seeing the report.

## Error paths

- Rule evidence is ambiguous: label it `agent-judgment` and do not present it as a hard conflict.
- Candidate data unavailable: disclose the limitation and use the preview directory without fabricating matches.
- Multiple conflicts: include all material conflicts in one report before pausing.

## Completion

The gate closes only after a later user message chooses a decision and the choice is recorded in the task state.
