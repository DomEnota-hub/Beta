# Diagnostic mode contract — Stage 3

The third stage establishes one reusable diagnostic contract before populating every model/scenario. It does not publish candidate content or change the Android screens.

## Independent choices

- `DiagnosticCardVersion`: `SHORT` and `DETAILED`. A scenario/profile contract must supply both routes. Each route owns its own node graph and explicitly listed extended evidence; there is no automatic short-to-detailed fallback or evidence inheritance.
- `DiagnosticKnowledgeVolume`: `BASIC` or `EXPANDED`; `DiagnosticDisplayDepth`: `MINIMAL`, `STANDARD` or `DETAILED`. These are independent presentation inputs. The contract carries them through selection without claiming that all source text has already been authored at every depth.
- Extended evidence appears only after a separate mode enablement and warning acknowledgement. It is bound to the exact scenario profile; an unknown or different profile yields no route or evidence. The future UI must set the acknowledgement only after the user has reached the end of the warning, consistent with the preserved Test implementation.
- Evidence visibility and action permission are separate. Historical/extended evidence remains non-executable. A standard action additionally requires `ACTIVE`, `CONDITIONAL_ACTION`, an executable runtime, verified source authority, confirmed exact profile and confirmed installed equipment. Missing facts fail closed. No existing candidate gains any of these confirmations.

The unit vertical slice uses the preserved `CHME3-DIAG-001` and `EXT2-CHME3-DIAG-001` identities with the source's `chme3-base` profile. The test's abstract node keys (`start`, `short-end`, `detailed-end`) exercise routing only; they are **not** source procedures or a published card. The source record is `PROHIBITED` and remains non-executable. Both versions can refer to the same original evidence without creating another source, while their route graphs and evidence lists are independent.

The existing `DiagnosticAccessPolicy` now requires warning acknowledgement for extended catalog visibility and explicit action inputs for execution. Its previous `ACTIVE + executableFlow` shortcut is removed. Existing catalogs and candidate packs are not rewritten. This contract is not yet consumed by Android screens, and the remaining scenario versions are not represented as completed content. The following scenario-population stages must provide source-backed text and version-specific branches for every locomotive, with applicability review before runtime integration.
