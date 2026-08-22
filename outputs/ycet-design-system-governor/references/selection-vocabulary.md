# Selection vocabulary

## SelectionProfile fields

- `taskMode`: `new-design`, `redesign`, or `audit`.
- `brief`: faithful summary of the original request.
- `industry`, `audience`, `productType`: product context.
- `tone`, `theme`, `density`: visual and experiential requirements.
- `layoutNeeds`, `contentNeeds`, `componentNeeds`: structural needs.
- `requiredTraits`, `excludedTraits`: hard filters, not preferences.
- `inputSources`: accessible source inventory.
- `explicitSystem`: valid system named in the invocation, otherwise `null`.

All vocabulary arrays use lowercase hyphenated terms and stable input order. Do not add a term merely to improve a candidate’s score.

## Input source shape

Each source contains:

- `kind`: `project`, `code`, `screenshot`, `design-file`, `url`, `figma`, `document`, or `other`.
- `value`: non-empty path, identifier, or URL supplied by the user.
- `accessStatus`: `accessible`, `degraded`, or `unavailable`.

## Hard-filter guidance

Use `requiredTraits` only for conditions whose absence makes a system unsuitable, such as a verified accessibility trait. Use `excludedTraits` for unacceptable system characteristics such as `morphism` in a performance-constrained flat interface.

Put ordinary preferences in tone, theme, density, or layout fields so the scorer can expose partial matches rather than discarding candidates.

## Evidence mapping

- Product type comes from the page or application purpose.
- Industry and audience come from explicit user context.
- Tone and theme come from requested perception, not a guessed brand.
- Density comes from information volume and interaction constraints.
- Layout/content/component needs come from required user tasks and states.

## Example

```json
{
  "taskMode": "new-design",
  "industry": ["backend-data"],
  "audience": ["technical-operators"],
  "productType": ["analytics-dashboard"],
  "tone": ["calm", "professional"],
  "theme": ["dark"],
  "density": ["compact"],
  "layoutNeeds": ["dashboard-grid"],
  "contentNeeds": ["data-visualization"],
  "componentNeeds": ["tables", "charts", "filters"]
}
```

The complete object must also include the schema version, brief, trait arrays, input sources, and `explicitSystem`.

## Error paths

Invalid fields are reported with JSON-style paths. Preserve the valid fields, ask only for missing material information, and never convert uncertainty into an explicit system choice.

## Completion

The profile is complete when it validates, preserves the user’s constraints, and contains no inferred hard filter or system selection.
