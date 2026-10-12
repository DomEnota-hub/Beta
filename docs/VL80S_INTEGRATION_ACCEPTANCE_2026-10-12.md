# VL80S integration acceptance — progress

Specification: `RailBrakeCalculator_Work_HandOff_2026-10-12.md` supplied by the user on 2026-10-12. Work branch: `DomEnota-maker/Beta:modular-rebuild`. Read-only donor: `DomEnota-maker/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`.

## Stage 0 — baseline (2026-10-12)

- Initial HEAD: `67c61e8d9e3bdb2da2161a6aabe8ae7a0e6a7cfc`. Its diff updates only `docs/VL80S_REMAINING_MIGRATION_AUDIT.md`; no user code changed after the two recorded successful runs.
- Android UI: [run 38156179846](https://github.com/DomEnota-maker/Beta/actions/runs/38156179846), `emulator-smoke` completed/success on `58cc8516c242f6fa84826821b2b485e7d1f0b0d0`, five Pixel API 34 tests.
- Module contracts, lint, debug APK and asset verification: [run 38156156994](https://github.com/DomEnota-maker/Beta/actions/runs/38156156994), `validate` completed/success on `9aa743c443c18afbdb57e22cdeca81f1a2e74202`. These are prior code commits, not independent runs on the documentation-only HEAD.
- Local `git` transport is unavailable in the scratch runner (browser-proxy connection failed); GitHub connector provides repository reads and content writes. Device evidence comes from Actions. A new code commit must trigger current-SHA validation; no baseline UI suite is claimed for this HEAD.

| Area | User access in current shell | Migrated / gated data | Baseline QA |
|---|---|---|---|
| Atlas layout, 4 pneumatic modes, 5 electrical flows | Atlas is initial screen; flow buttons reachable | model-owned, educational | existing Pixel smoke 5/5 on previous code |
| Equipment and Technical Data | exact hotspot to entry and typed links | 89 + 89 entries | one tested route; broad Back/touch QA open |
| Acceptance | only an individual item can open through a typed link | 81 items and 8 routes in assets | **route index not loaded by `MainActivity`; no route UI entry** |
| Safety | typed entry links | model-owned safety content | route coverage open |
| Diagnostics | shared catalog entry | 103 executable graphs are all `CANDIDATE` | published catalog intentionally empty; gate must remain closed |

### Working QA matrix

| Stage | Focus | Status | Evidence / next check |
|---|---|---|---|
| 1 | physical/system Back, nested entries, scroll | PARTIAL | existing tests cover selected return paths; add device tests |
| 2 | all mode steps, touch maps, scaling | PARTIAL | five existing tests cover flow navigation; real touch geometry and visual review open |
| 3 | eight routes, search, status, note, progress, persistence | FAIL (integration) | route UI not reachable; add entry and tests without changing donor sequence |
| 4 | compact/large text | NOT_TESTED | second display profile required |
| 5 | typed links, provenance and fail-closed | PARTIAL | existing validators; failure cases to inspect |
| 6 | 103 candidate graphs and publication gate | PARTIAL | graph validator and empty catalog; negative UI cases to extend |
| 7 | final code-SHA CI | NOT_TESTED | run after implementation |

## Change log

Stage 0 recorded. Subsequent major stages append exact SHA, tests, results and limitations here. Do not change `RailBrakeCalculator_BACKLOG.md`.

### Stage 3a — route entry (2026-10-12)

- RED: `Vl80sAcceptanceNavigationInstrumentationTest.allEightRoutesOpenFromShellInSourceOrder` failed on Pixel API 34 because the “Приёмка” entry was absent. [Run 38217349283](https://github.com/DomEnota-maker/Beta/actions/runs/38217349283), one new failure and five previous tests passing. An earlier attempt `125f501` did not compile due to an invalid test import; corrected in `eae0f73`.
- GREEN: shared `AcceptanceRoutesScreen` lists the eight index routes in their declared order. `app-shell` loads and resolves their canonical items, checks model ownership and pack membership, and navigates Atlas → route list → route → item → route. No acceptance pack sequence changed.
- Commits: `af7d4f8` (shared chooser), `f515cea` (Atlas entry), `f8922c79a415256bfb36a3a0b1ed95ec75d1ca40` (shell integration).
- [Bootstrap run 38218174385](https://github.com/DomEnota-maker/Beta/actions/runs/38218174385): completed/success (contract/unit, lint, debug APK, indexed assets). [Android UI run 38218174433](https://github.com/DomEnota-maker/Beta/actions/runs/38218174433): completed/success, 6/6 tests, including all eight route counts.
- Remaining Stage 3: search, canonical shared status, notes, summary and restart persistence need direct device regression evidence. Route sequence equality is covered by the pack validator, but actual operational order remains subject to source review.
