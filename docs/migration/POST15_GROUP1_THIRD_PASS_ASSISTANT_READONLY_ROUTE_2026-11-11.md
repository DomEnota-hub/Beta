# RailBrake Beta — group 1/8, third pass: assistant search of family reference knowledge

Date: 11.11.2026. Status: **CODE/CI PASS; GROUP IN_PROGRESS / DEVICE_QA_PENDING**. Main-stage baseline **11/15**, not reclassified. Issue #4 remains OPEN.

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

## CI correction after first checkpoint

The initial code HEAD `ffbbb0b3` produced a **real lint failure** in [Stage 7 #43059778892](https://github.com/DomEnota-hub/Beta/actions/runs/43059778892): `AssistantSearchScreen.kt:241 SuspiciousIndentation` after removing the execution-only wrapper. Fixed by dedenting the reference results block in [`f38518f401ce87a71e8f21ef30d9f0f16b098d38`](https://github.com/DomEnota-hub/Beta/commit/f38518f401ce87a71e8f21ef30d9f0f16b098d38). **The previous code HEAD is not accepted.**

New final-code verification started: [Stage 13 #43060860552](https://github.com/DomEnota-hub/Beta/actions/runs/43060860552), [Stage 10 #43060860542](https://github.com/DomEnota-hub/Beta/actions/runs/43060860542), [Stage 9 #43060860468](https://github.com/DomEnota-hub/Beta/actions/runs/43060860468), [Stage 15 #43060860490](https://github.com/DomEnota-hub/Beta/actions/runs/43060860490), [modular #43060870854](https://github.com/DomEnota-hub/Beta/actions/runs/43060870854). At checkpoint, runs remain QUEUED/IN_PROGRESS. Resume on **`f38518f4`**, not `ffbbb0b3`.

## Verified final result and Google Drive delivery (11.11.2026)

Final implementation SHA **`f38518f401ce87a71e8f21ef30d9f0f16b098d38`**; all **29/29** GitHub Actions workflows for that exact code commit finished **terminal SUCCESS**. The earlier lint-failing SHA `ffbbb0b3` remains recorded as failed, not counted as accepted.

- [Stage 13 family gates #43060860552](https://github.com/DomEnota-hub/Beta/actions/runs/43060860552) SUCCESS: family source/variant gates, JUnit, lint, Debug APK and source-parity/actual APK quarantine.
- [Stage 10 assistant corpus #43060860542](https://github.com/DomEnota-hub/Beta/actions/runs/43060860542) SUCCESS.
- [Stage 9 Compose UI #43060860468](https://github.com/DomEnota-hub/Beta/actions/runs/43060860468) SUCCESS.
- [Stage 15 integration QA #43060860490](https://github.com/DomEnota-hub/Beta/actions/runs/43060860490) SUCCESS: JUnit, lint, Debug APK, AndroidTest **compilation**, actual APK integrity and source/profile gates.
- [Modular bootstrap #43060870854](https://github.com/DomEnota-hub/Beta/actions/runs/43060870854) SUCCESS.

Stage 15 artifact **`13874236302`** ZIP integrity PASS, contains exactly `app-shell-debug.apk`; extracted APK ZIP integrity PASS. Verified actual APK still contains `assets/crew-reference/summaries.json` and **0** family full-pack asset paths `electric/ermak/`, `diesel/chme3-family/`, `diesel/tem2-family/` (known incomplete migration, not celebrated as parity).

**Delivered and re-downloaded** to Google Drive folder `Rail` (`1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`):
- [`RailBrake_Beta_1.2.2-modular-alpha01_group1-third-pass_stage15_f38518f4.apk`](https://drive.google.com/file/d/1QpBcCajaVnM84JmPqwGc0DLlJnV9ozWY/view)
- Google Drive file ID: `1QpBcCajaVnM84JmPqwGc0DLlJnV9ozWY`; **9,663,001 bytes**, Debug/QA, version `1.2.2-modular-alpha01`.
- Original APK SHA256 **`cdd641cd9a058bcec1b2e5ecff89d293adea075806a4d9dee0c94eaa422c6a1b`**. Re-downloaded from Drive, byte-for-byte identical and SHA256 matched. Drive metadata confirms exact filename, size and parent folder.
- ZIP source SHA256 `a6d6da7bd5b307a62113c5464787e856fba9e148fa43abf416f223864005e159`, size 9,280,039 bytes.

**Functional scope:** the existing 84 reference descriptions (12 each for 2ЭС5К, 3ЭС5К, ЧМЭ3/Т/Э, ТЭМ2/У) are now searchable from Assistant without execution selection, but only matching, scoped entries are displayed. No new cards created, no full family pack restored, no diagnostic graph or approved crew action. Unknown applicability is explicitly marked. Device QA remains pending; this is NOT production.

**Next scheduled group:** 2/8 diagnostics; do not repeat already successful group-1 CI. Keep group 1 and stages 13/15 open until full family parity and final acceptance. No new APK is needed for the documentation-only checkpoint.
