# New design workflow

## Inputs

- Confirmed system ID and reviewed DesignRuleBundle.
- Product goal, audience, content, required states, target breakpoints, and available source material.
- Approved deviations, if any.

## Actions

1. Preserve the product requirements separately from design-system rules.
2. Confirm there is no unresolved conflict gate.
3. Define page hierarchy, user flow, content priority, responsive behavior, and accessibility baseline.
4. Map layout, colors, typography, spacing, motion, and components to cited bundle rules.
5. Create only the screens and states required by the brief.
6. Implement with existing project conventions when code is in scope.
7. Run available build, test, static audit, browser, responsive, and accessibility checks.
8. Perform an Agent review for visual semantics that scripts cannot verify.

## Rules

- Prefer system tokens and component contracts over raw values.
- Preserve source evidence for hard constraints.
- Do not copy or execute bundled preview HTML as application code.
- Mark intentional departures as `user-approved-deviation`.
- Mark inaccessible screenshots, URLs, or tools as `degraded-unverified`.

## Output

- Confirmed design system and asset version.
- Implemented screens/components and state coverage.
- Rule-to-decision summary with evidence.
- Validation results and unresolved risks.
- ComplianceReport using the shared output contract.

## Error paths

- Missing content or user-flow decision that changes structure: ask for that decision before implementation.
- Tool unavailable: continue only with checks that remain reliable and label the gap.
- New conflict discovered during implementation: return to `awaiting-user-decision`.

## Completion

The design is complete when required states are implemented, available validations pass, Agent-review items are recorded, and no gate remains unresolved.
