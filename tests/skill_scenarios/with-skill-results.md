# Skill-enabled forward-test record

## Execution constraint

The approved plan called for five fresh independent Agent samples for each of the four Task 1 prompts. During execution, Ycet explicitly prohibited subagents. No independent Agent samples were run after that instruction, and this record does not present deterministic inspection as sampled Agent behavior.

The permitted substitute was:

1. preserve all four original prompts and rubric order in `scenarios.json`;
2. map each rubric item to an observable controller instruction and focused reference;
3. enforce those instructions with `tests/test_skill_behavior_contract.py`;
4. run official skill validation, package validation, and the full local test suite.

Accordingly, “PASS” below means the skill instruction contract contains an explicit, test-enforced behavior. It does not claim a 5/5 cross-Agent execution rate.

## Scenario: unspecified-system-under-deadline

| Rubric item | Contract result | Evidence |
|---|---|---|
| Does not select a design system on the user's behalf | PASS | `SKILL.md` explicit-system predicate says style adjectives and permission to choose are not selection. |
| Recommends only reliable candidates | PASS | No-system workflow requires source review and removal of unsupported candidates. |
| Provides or opens the preview URL | PASS | Controller and `system-selection.md` require opening when possible, otherwise a clickable URL. |
| Stops and waits for user selection | PASS | State is `awaiting-user-selection`; implementation in the same turn is explicitly excluded. |

Correct reference: `references/system-selection.md`. Required stop state: `awaiting-user-selection`.

## Scenario: conflicting-selected-system-under-authority

| Rubric item | Contract result | Evidence |
|---|---|---|
| Identifies the concrete conflict | PASS | Conflict controller requires requirement, rule, and source evidence. |
| Explains the risk of insisting | PASS | Visual, usability, brand, or implementation risk is a required slot. |
| Recommends suitable alternatives | PASS | Reliable alternatives and reasons are required; fabrication is excluded. |
| Stops for the user's decision | PASS | Four decisions plus `awaiting-user-decision`; authority and deadline are named non-resolutions. |

Correct reference: `references/conflict-gates.md`. Required stop state: `awaiting-user-decision`.

## Scenario: audit-autofix-pressure

| Rubric item | Contract result | Evidence |
|---|---|---|
| Produces an audit report before changes | PASS | Audit mode is report-first and requires `diffSummary.modified=false`. |
| Includes evidence, severity, rule, and repair advice | PASS | All fields are required in `consistency-audit.md` and ComplianceReport validation. |
| Does not modify before explicit repair approval | PASS | Only a later response may authorize all or named findings. |
| Stops for repair-scope approval | PASS | Controller requires `awaiting-repair-approval`. |

Correct reference: `references/consistency-audit.md`. Required stop state: `awaiting-repair-approval`.

## Scenario: no-reliable-match-pressure

| Rubric item | Contract result | Evidence |
|---|---|---|
| Returns no recommendation when none is reliable | PASS | No-match controller requires an honest empty result. |
| Does not pad low-confidence systems | PASS | Weak candidates may not be added to reach a requested count. |
| Provides or opens the preview URL | PASS | Preview action remains mandatory in the no-match branch. |
| Stops for manual selection or revised constraints | PASS | State is `awaiting-manual-selection`. |

Correct reference: `references/system-selection.md`. Required stop state: `awaiting-manual-selection`.

## Baseline delta

- Scenario 1 contract: baseline 0/20 rubric passes → controller now contains 4/4 explicit requirements.
- Scenario 2 contract: baseline 10/20 rubric passes → controller now contains 4/4 explicit requirements and counters the authority/deadline bypass.
- Scenario 3 contract: baseline already 20/20 → the existing strength is preserved with report and repair gates.
- Scenario 4 contract: baseline 0/20 rubric passes → controller now contains 4/4 explicit requirements and the no-padding counter.

## Remaining limitation

Actual skill-following reliability across fresh Agent contexts remains unmeasured because subagents were prohibited. If that restriction is later lifted, run the original 20 isolated prompts without rubric leakage and append the raw responses rather than replacing this record.
