# Stage 1/15: pinned Kotlin feature/state parity and unresolved source quarantine (2026-11-09)

**Status: IN_PROGRESS.** Source accounting and fail-closed quarantine tests are implemented; functional equivalence, source authority and Android user journeys are **not** signed off. Read-only donor: `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Target branch: `audit/information-block-gaps-20261014`.

## Kotlin source coverage

`docs/migration/donor-kotlin-crosswalk.json` records **74/74** Kotlin files in the pinned donor `app/src/main/java/` tree, each with its original Git blob SHA, feature area, existing Beta architectural touchpoint(s), conservative status and `userJourneyVerified=false`. `patch/` and `app/src/test/` are explicitly out of scope for this 74-file count; do not treat it as a count of every Kotlin file in the donor repository.

- **33 PARTIAL**: related Beta module code exists, but donor behavior, source mapping and end-to-end wiring are not proven.
- **26 CONTRACT_ONLY**: an architectural interface or related module exists, not a feature-complete port.
- **15 NOT_MIGRATED**: no confirmed runtime target for that source component.
- **0 MIGRATED**: no Kotlin feature promoted without end-to-end proof.

`qa/validate_donor_kotlin_crosswalk.py` checks the exact 74-file pinned donor Git tree against the manifest and target file existence. `qa/test_donor_kotlin_crosswalk.py` covers **8 negative/positive tests**. CI [Pinned donor Kotlin feature/state crosswalk](https://github.com/DomEnota-hub/Beta/actions/workflows/donor-kotlin-crosswalk.yml) fetches the original Git tree from the fixed SHA; a changed source SHA, omitted source, duplicate, missing target, path traversal or unproven `MIGRATED` status fails closed. It additionally checks the current Beta shell/history wiring state.

**Key implementation gaps proven by source inspection:**
1. Beta shell starts `loadVl80sVerticalSlice()`, not the agreed model-selectable home. `app-shell/build.gradle.kts` does not depend on `:feature-calculations` or `:feature-history`.
2. Beta `assistant-core` has `AssistantScope.kt` only; donor text parser, index, conversation and offline voice are not ported.
3. Donor `WorkingLocomotiveRepository` persists `working_locomotive/selected`; Beta has no equivalent confirmed persistence. This selection is distinct from the confirmed diagnostic execution profile.
4. Donor `AcceptanceStateRepository` stores `technical_acceptance_states`, including item state, `note:<id>`, `disabled:<family>`, `save_parameters:<family>`, and `session:<family>:<field>`. Beta has acceptance state types but no verified on-device migration.
5. Donor `DiagnosticSessionRepository` stores `diagnostic_sessions/records` as URL-safe Base64 fields joined by `|`, up to 100 records. Beta has no proven compatible store.
6. Donor `LocomotiveProfileRepository` stores `locomotive_profile` and a separate `diagnostic_profile_confirmed` flag. The donor UI default to VL80S must **never** be interpreted as confirmation.
7. `BrakeCalculatorApp.kt` imports `ru.railbrake.calculator.data.HistoryRepository`, but **no `HistoryRepository.kt` exists anywhere in the pinned donor Git tree**. Its exact legacy storage format is therefore **not established**. Keep `HistoryStorageMigrationGate.legacyFormatVerified=false` until the original implementation or compatible evidence is recovered.
8. Encrypted exam questions have been source-audited, but `ExamQuestionRepository` / `ExamQuestionScreen` are not migrated to runtime.

The source Kotlin manifest maps architectural touchpoints, **not** line-by-line source equivalence. Actual behavior and storage migration remain future implementation tasks.

## Unresolved source links remain quarantined

New `qa/validate_stage1_unresolved_source_quarantine.py` and **7 regression tests** enforce these source-audit facts:

- **CHME3/T/E:** 610 distinct unresolved `(source, variant, sourceTargetId)` triples remain explicitly unresolved; a disappearing entry without reviewed evidence fails the baseline.
- **Ermak:** 55 source-gap IDs with **542 occurrences**, plus two ambiguous IDs with **6 occurrences**, remain unresolved. Automatic source-ID matching is forbidden; `source-identity-resolution.json` must remain `CANDIDATE` / `INFORMATION_ONLY` / `runtimeImport=false`.
- `ER-DIAG-136` remains a separate candidate without a Stage 7 link; `autoAddToStage7=false`.
- Neither CHME3 nor Ermak may gain a `runtime-index.json` while this quarantine baseline remains in effect.

CI [Stage 1 unresolved source quarantine](https://github.com/DomEnota-hub/Beta/actions/workflows/stage1-unresolved-source-quarantine.yml) tests loss/duplication of unresolved references, unsafe auto-match, index auto-link, candidate promotion and runtime-index creation.

**This is a deliberate conservative baseline.** When documented evidence resolves any gap, update the source audit, the quarantine validator and the associated regression together. Do not fabricate an ID to make the count zero.

## Remaining work before stage 1 closes

- Investigate whether the donor history implementation can be recovered from authoritative source history, not inferred from UI imports.
- Continue source link resolution with primary evidence and explicit variant applicability; retain unresolved references as non-executable candidates.
- Recover 329 exam question entries into a non-runtime candidate format only when authorization and provenance are established.
- Extend source-level mapping beyond Kotlin main and donor assets where required (tests, Gradle wiring, assets outside `app/src/main/assets`).
- Run full CI on final HEAD; only then decide whether stage 1 acceptance gates are met.

**Next concrete action:** inspect donor history source provenance, then resolve or explicitly quarantine individual CHME3/Ermak references in evidence-backed batches; do not begin stage 2 until all stage 1 gates have documented disposition.
