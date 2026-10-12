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
- Remaining Stage 3: search, canonical shared status, notes, summary and restart persistence need direct device regression evidence. The earlier validator checked membership and uniqueness, not exact order. On 2026-10-12 the seven donor sequences were compared in order against pinned `vl80s_acceptance.json.gz` and matched; `qa/validate_vl80s_acceptance.py` now pins SHA-256 of all eight route sequences. Operational appropriateness still requires source review.

### Stage 1a — linked entry Back (2026-10-12)

- RED: `Vl80sContentNavigationInstrumentationTest.systemBackFromLinkedTechnicalDataReturnsToEquipmentCard` failed after the actual Atlas transformer → equipment → Technical Data path: the technical link could not be found after Back, because the shell returned to Atlas. [Run 38218977310](https://github.com/DomEnota-maker/Beta/actions/runs/38218977310), 1/7 failed.
- GREEN: `5ed9dd930024546bc0edd255724a4a8ee40ad7da` retains a canonical entry history in the shell, clears it on each root entry and pops it before returning to the origin. A self-link does not push duplicate history.
- [Bootstrap run 38219634064](https://github.com/DomEnota-maker/Beta/actions/runs/38219634064): completed/success. [Android UI run 38219634156](https://github.com/DomEnota-maker/Beta/actions/runs/38219634156): completed/success, 7/7 tests. Ordinary on-screen Back from generic linked cards still needs a dedicated UI affordance and test; this check specifically exercises system Back.

### Stage 3b — state and sequence QA in progress

- Source comparison: the pinned donor gzip at `Test-` commit `3176d6ee228f0ed4b78371f45209e10c1c724eff` was decoded read-only. All seven donor `itemIds` sequences equal the generated route sequences after the 15-item required prefix and duplicate removal; the required route is the 15 generated `VL80-REQ-xx` IDs. SHA-256 pins for all eight sequences were added to `qa/validate_vl80s_acceptance.py` (`5da4363b`), with a successful migration validator run [38221576724](https://github.com/DomEnota-maker/Beta/actions/runs/38221576724).
- The first expanded device test `6efe565` did not compile because of a missing test import. After correction `16ba42f`, [UI run 38220753354](https://github.com/DomEnota-maker/Beta/actions/runs/38220753354) failed: the test could not locate a count and note placeholder. Stable Compose semantic tags were added to the shared route count and note field (`bde7b63`, `8bf140e`); a second test compile failed for another missing assertion import ([run 38221526429](https://github.com/DomEnota-maker/Beta/actions/runs/38221526429)). The import was corrected in `9871d772`. **State/persistence assertions remain unverified** until the next device run completes.
- The acceptance generator workflow is now idempotent when generated packs have no diff (`efcaf86a`). It retains the optimistic branch SHA guard and never edits the donor.
