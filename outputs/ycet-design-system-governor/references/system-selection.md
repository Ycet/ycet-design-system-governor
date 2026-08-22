# System selection

## Inputs

- The exact message that invoked the skill.
- `assets/catalog/design-systems.index.json` and `assets/catalog/selection-profiles.json`.
- A validated SelectionProfile when no system is explicit.
- Browser-control availability.

## Resolve an explicit system

1. Normalize the named value without broadening its meaning.
2. Match against ID, exact name, then unambiguous aliases.
3. Require exactly one bundled match.
4. Report invalid or ambiguous values and pause; do not silently substitute a nearby system.

The invocation must itself name the system. Adjectives such as “minimal,” “premium,” or “glass-like” are requirements, not selections, unless they resolve to one catalog alias without ambiguity.

## Recommend when no system is explicit

1. Preserve the user brief in a SelectionProfile.
2. Run `python scripts/recommend_systems.py --profile <profile.json> --catalog assets/catalog/design-systems.index.json`.
3. Read each returned `manifest.json` and the relevant visual, typography, layout, responsive, and Do/Don't sections of `DESIGN.md`.
4. Remove any candidate whose score is not supported by source evidence.
5. Present normally three reliable systems; present fewer when fewer qualify, and at most five when close alternatives have meaningful differences.
6. Include fit evidence, unmatched needs, risk, score, and preview URL.

## Preview action

Use `https://open-design.ai/zh/plugins/systems/` only as a visual preview directory, never as a rule source. Open it directly when browser control is available; otherwise include a clickable link.

## Pause states

- Reliable candidates exist: `awaiting-user-selection`.
- No reliable candidate exists: `awaiting-manual-selection`.
- Explicit name is invalid or ambiguous: `awaiting-valid-system-selection`.

Every state above ends the current task turn before design or implementation.

## Output

State the selection status, candidate list or honest empty result, preview action, and the single decision required from the user.

## Error paths

- Invalid SelectionProfile: report the JSON field path and request only missing user information.
- Missing or invalid catalog: stop and report the local file path; do not invent systems.
- Browser unavailable: provide the URL and continue to the same pause state.

## Completion

Selection completes only when the user explicitly chooses one valid bundled system in a later message.
