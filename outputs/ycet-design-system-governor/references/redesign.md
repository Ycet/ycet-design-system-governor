# Existing-page redesign

## Inputs

- Confirmed system and reviewed rule bundle.
- Existing code/project plus any screenshots, URL, Figma source, or product requirements.
- Behaviors and content that must remain unchanged.

## Baseline first

1. Inventory routes, components, states, responsive behavior, interactions, and tests.
2. Capture a visual baseline when browser or screenshot access exists.
3. Label unavailable inputs and checks before proposing changes.
4. Separate functional defects from design-system inconsistencies.

## Redesign actions

1. Check requirements against the selected system and resolve conflicts before edits.
2. Create a change map for hierarchy, tokens, typography, layout, components, and interaction states.
3. Preserve working behavior unless the user explicitly changes it.
4. Make surgical edits that follow the project’s existing architecture and stack.
5. Avoid unrelated refactors and speculative component-library work.
6. Compare the result against both the baseline and DesignRuleBundle.
7. Run tests, builds, static audit, and visual checks available in the environment.

## Output

- Baseline summary and preserved behavior.
- Files/components changed and why.
- Before/after differences tied to rules.
- Validation evidence, degraded checks, and approved deviations.
- Final ComplianceReport.

## Error paths

- Existing behavior is unclear: pause before changing that behavior.
- Source cannot be accessed: state the limitation and do not claim faithful preservation.
- Conflict appears: issue a ConflictReport and enter `awaiting-user-decision`.

## Completion

The redesign completes when scoped changes are implemented, preserved behavior remains verified, available checks pass, and the difference summary is evidence-backed.
