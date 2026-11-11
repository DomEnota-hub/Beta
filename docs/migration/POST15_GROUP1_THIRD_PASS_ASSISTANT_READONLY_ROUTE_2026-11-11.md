# RailBrake Beta — group 1/8, third pass: assistant search of family reference knowledge

Date: 11.11.2026. Status: **CI_PENDING / IN_PROGRESS**. Main-stage baseline **11/15**, not reclassified. Issue #4 remains OPEN.

## Actual code changes (Beta only)

Working branch: `audit/information-block-gaps-20261014`. Donor Test- @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` remains READ-ONLY.

- `52c29957633227dcbf065c2ac2b4e0f829b43952`: `AssistantFamilyReferencePolicy.search()` now uses the already-tested `FamilyReferencePreviewPolicy.searchBeforeExecution()` for **read-only** references when execution is not selected. The existing `search()` execution-scoped path is unchanged.
- `15a530a3800804905fa8acd78f18c6e1baa3bdb3`, `ffbbb0b3b23bab6d4fad09d6eff824142ac79d1a`: `AssistantSearchScreen` shows matching reference cards before execution selection with explicit "execution unknown / applicability and actions unverified" warnings, still offers execution buttons and never routes diagnostic actions.
- `0332c6c27ae61cd92e66548fd015c43a9b1241fb`: `MainActivity` carries nullable execution through the assistant→Atlas reference deep link, where `FamilyContentScreen` rechecks the same read-only scope.
- `76cbb775e12835935d2d2ae8a44c5aebdd72d29a`: JUnit tests cover single-execution TEM2 reference visibility, Ermak MSUD-N/015 uncertainty, CHME3T №6245 split, cross-model rejection, invalid donor SHA, fault-query rejection, and unchanged working-model selection.

**User-visible effect intended:** the existing **84 curated, donor-traceable, summary-only** family cards can be found through Assistant equipment search without forcing an execution selection. Search still filters to the explicit requested model or the working model, and only matched cards appear. A deep link opens a read-only Atlas description with warning. No additional family assets shipped, no new diagnostic graph, no crew action approved, no source status elevated.

## Source-to-source and safety boundary

The 84 summary objects were previously matched to Test- pinned Git blobs and migrated target IDs in the Stage 13 donor-summary parity gate. This pass **reuses that established lineage** and does not treat it as independent normative/redistribution approval. Full Ermak, CHME3 and TEM2 packs remain excluded by `ignoreAssetsPattern`; `FamilyPublicationGate` and `qa/check_stage13_apk_quarantine.py` were deliberately **not relaxed**, because their safe replacement still requires a rights/source/variant-specific selection. This is a narrow functional improvement, not full family parity.

The full crew-permissions audit in `docs/backlog/FUTURE_PERFORMANCE_AND_CREW_ACCESS_AUDIT.md` stays PARKED. No published diagnostic/action gate changed.

## Verification and delivery

At code HEAD `ffbbb0b3b23bab6d4fad09d6eff824142ac79d1a`, 29 GitHub Actions runs were observed **QUEUED**, including:
- [Stage 13 family gates](https://github.com/DomEnota-hub/Beta/actions/runs/43059778855)
- [Stage 10 assistant corpus](https://github.com/DomEnota-hub/Beta/actions/runs/43059778896)
- [Stage 9 assistant UI](https://github.com/DomEnota-hub/Beta/actions/runs/43059778638)
- [Stage 15 integration QA](https://github.com/DomEnota-hub/Beta/actions/runs/43059778528)
- [Modular bootstrap](https://github.com/DomEnota-hub/Beta/actions/runs/43059788131)

**NOT CLAIMED:** tests PASS, successful lint/assembleDebug, AndroidTest compilation, an APK for this commit, Google Drive delivery, or device QA. No new APK is available yet; do not substitute the previous group 8 APK.

## Precise resume point

1. Re-read code HEAD and the above five workflow runs; wait until terminal. Fix any failing Kotlin/test/Android lint in Beta and rerun.
2. On successful Stage 15/Stage 13 builds, fetch the **new unique** Debug/QA artifact, inspect APK contents and SHA256, deliver to Drive `Rail` folder ID `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd` (<=100MB one file, >100MB split ZIP), verify Drive metadata and hash. Record the real URL, size and SHA; do not claim delivery without confirmation.
3. Keep group 1 **IN_PROGRESS**: full family reference packs, Atlas and acceptance parity, execution/profile verification and lawful redistribution are still open. Next independent group is 2/8; do not start it while unresolved group-1 CI/build delivery needs completion.
