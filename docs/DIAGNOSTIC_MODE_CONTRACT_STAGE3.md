# Diagnostic mode contract — Stage 3

The third stage establishes one reusable diagnostic contract before populating every model/scenario. It does not publish candidate content or change the Android screens.

## Independent choices

- `DiagnosticCardVersion`: `SHORT` and `DETAILED`. A scenario/profile contract must supply both routes. Each route owns its own node graph and an independently authored extended branch graph tied to that exact scenario and profile, with explicit evidence; there is no automatic short-to-detailed fallback or branch inheritance. The same source may support both versions, but copying one branch into the other does not satisfy the contract.
- `DiagnosticKnowledgeVolume`: `BASIC` or `EXPANDED`; `DiagnosticDisplayDepth`: `MINIMAL`, `STANDARD` or `DETAILED`. These are independent presentation inputs. The contract carries them through selection without claiming that all source text has already been authored at every depth.
- Extended evidence appears only after a separate mode enablement and warning acknowledgement. It is bound to the exact scenario profile; an unknown or different profile yields no route or evidence. The future UI must set the acknowledgement only after the user has reached the end of the warning, consistent with the preserved Test implementation.
- Evidence visibility and action permission are separate. Historical/extended evidence remains non-executable. A standard action additionally requires `ACTIVE`, `CONDITIONAL_ACTION`, an executable runtime, verified source authority, confirmed exact profile and confirmed installed equipment. Missing facts fail closed. No existing candidate gains any of these confirmations.

The unit vertical slice uses the preserved `CHME3-DIAG-001` and `EXT2-CHME3-DIAG-001` identities with the source's `chme3-base` profile. The test's abstract node keys (`start`, `short-end`, `detailed-end`, `extended-start`) exercise routing only; they are **not** source procedures or a published card. The source record is `PROHIBITED` and remains non-executable. Both versions can refer to the same original evidence without creating another source, while their route and extended branch graphs are independently authored. An absent or copied extended branch is rejected.

The existing `DiagnosticAccessPolicy` now requires warning acknowledgement for extended catalog visibility and explicit action inputs for execution. Its previous `ACTIVE + executableFlow` shortcut is removed. Existing catalogs and candidate packs are not rewritten. This contract is not yet consumed by Android screens, and the remaining scenario versions are not represented as completed content. The following scenario-population stages must provide source-backed text and version-specific branches for every locomotive, with applicability review before runtime integration.

## Stage 3/51 authoring source-gap addendum (21 October 2026)

The historical "Stage 3" heading above refers to the shared runtime contract,
**not** this 51-step authoring cycle. In the new cycle, absence of evidence must
never be solved by inventing a placeholder graph.

`DiagnosticCardRoute.extendedSourceGapReason` records an authoring-only, nonblank
reason for an unbound extension of that **specific version**. Such a route has
`extendedRoutes = emptyList()`. Bound extensions must not carry a gap reason.
Neither state publishes a scenario. `DiagnosticActionGate` remains unchanged.
The independently authored SHORT and DETAILED *main* graphs must have distinct
structure. If both extensions are bound, their graphs must be distinct as well.
A source gap for one version must not inherit an extension from the other.

The graph validator rejects duplicate and dangling nodes, unreachable nodes,
and nodes which have no possible exit to an explicit terminal. This is graph
topology validation, **not** proof that every possible path terminates, that a
question is safe, or that UNKNOWN answers are substantively correct.

Source/role/profile/equipment and current-revision evidence review is defined
in `docs/diagnostics/DIAGNOSTIC_AUTHORING_STAGE3_ACCEPTANCE.md`. Its negative
fixtures are synthetic software tests and never railway operating advice.
