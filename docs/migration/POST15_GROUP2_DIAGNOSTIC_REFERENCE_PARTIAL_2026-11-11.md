# RailBrakeCalculator — post-15 remediation group 2: diagnostic knowledge vs crew action (11.11.2026)

**Status: PARTIAL, CI-VERIFIED IMPLEMENTATION.** This is a real Kotlin/Compose change, **not** completion of group 2, stage 13 or the full migration. Main-stage completion remains **11/15** (1–10 and 12). No production release, no device tests and no full normative permissions audit.

## Scope, donor and code

- Working Beta branch: `audit/information-block-gaps-20261014`.
- Immutable read-only Test- donor: `3176d6ee228f0ed4b78371f45209e10c1c724eff`.
- Code/UI and new unit tests: [`603c467d`](https://github.com/DomEnota-hub/Beta/commit/603c467d1cf9044734e33272de50614bf2ba6394).
- Dedicated diagnostic CI: [`2c093a48`](https://github.com/DomEnota-hub/Beta/commit/2c093a48d5fa15b841a96d431d50583ff8a2f60c).
- Fix of brittle reflection assertion: [`6d06a29b`](https://github.com/DomEnota-hub/Beta/commit/6d06a29b1f7814d54ad7c8d956411b59857b9c4d).
- Real donor/runtime candidate parity script and CI: [`d36bc618`](https://github.com/DomEnota-hub/Beta/commit/d36bc618216cba6432473ad6a8c824ce926ca64d).
- This run worked **only group 2**. Group 1 remains PARTIAL and will be revisited after the first 7+1 pass.

## Actual user-facing implementation

1. Added `DiagnosticReferenceCatalog`: it builds a **text-only, non-executable** view from the already bundled VL80S diagnostic runtime and its exact-model STANDARD/CANDIDATE registry entries. The view contains **only title, summary, category, explicit source-status notice and execution-applicability caveat**. No question graph, checks, `immediateActions`, `prohibited`, repair instructions or unverified source claims can pass through this type.
2. Wired the read-only catalog into the real `MainActivity` → VL80S `DiagnosticCatalogScreen` route. The diagnostics list now includes searchable donor symptom descriptions marked **«Справочные описания · требуют проверки»**, and individual read-only cards with clear explanation that actions, contraindications and permission are **not verified**. The candidate **cannot** open the interactive questionnaire.
3. The reference path rejects foreign models, foreign owners, wrong content types, EXTENDED/RESTRICTED layers, non-CANDIDATE entries and registry-inapplicable variants. If the scenario's exact variant differs from the selected variant or the variant is unknown, the description may still be read with **«Применимость к выбранному исполнению не подтверждена»**; this is not permission to perform work.
4. For **already published and separately authorized** diagnostic cards, the existing UI now visibly renders `prohibited` as **«Противопоказания и недопустимые действия»**, `stopConditions`, `reportFields` as **«Что сообщить»**, and `sourceNote`. These are sourced from the accepted scenario data; the change does **not** publish any new actionable graph or claim that current VL80S candidates are approved. There are currently no newly approved executable scenarios from this run.
5. Existing `PublishedDiagnosticCatalog`, `DiagnosticActionGate`, family publication gate, source/profile checks, Android resource quarantine and extended-mode consent were **not weakened**. This is the requested distinction between readable knowledge and permission to act.

## Verified automated tests and APK

- Initial new diagnostic workflow [#42947384107](https://github.com/DomEnota-hub/Beta/actions/runs/42947384107) **FAILED**: 59 feature-diagnostics unit tests, 1 brittle new assertion expected exactly six reflected JVM fields, but Compose/Kotlin can generate additional fields. This was a **test assertion error, not a Kotlin production compile error**. Replaced exact field count with positive whitelist + negative executable-field checks.
- On fixed code SHA `6d06a29b`: **17/17 GitHub Actions workflows SUCCESS (terminal)**, including dedicated [post-15 group 2 #42947723298](https://github.com/DomEnota-hub/Beta/actions/runs/42947723298).
- On final code/test SHA `d36bc618`: **17/17 workflows SUCCESS (terminal)**, including [post-15 group 2 #42947997269](https://github.com/DomEnota-hub/Beta/actions/runs/42947997269) and [modular bootstrap #42948005160](https://github.com/DomEnota-hub/Beta/actions/runs/42948005160).
- Dedicated workflow ran `:feature-diagnostics:testDebugUnitTest`, `:app-shell:testDebugUnitTest`, Android lint, `:app-shell:assembleDebug`, `:app-shell:assembleDebugAndroidTest` (**compiled only**), runtime validator, actual APK integration audit, pinned candidate parity and `git diff --check`. All passed.
- Real source-data check: `VL80S_EXECUTABLE_DIAGNOSTIC_RUNTIME_PASS 103 318 954` (103 runtime scenarios, 318 questions, 954 response edges); `POST15_GROUP2_REFERENCE_PARITY_PASS read_only_candidates=44 runtime_scenarios=103 registry_entries=44 executable_candidates=0`. **44** STANDARD/CANDIDATE donor scenarios have eligible summary entries; **59** other runtime scenarios are **not** claimed to be restored by this read-only bridge. The 44 are *descriptions*, not 44 validated crew procedures.
- Actual Debug APK gate: `STAGE15_APK_INTEGRATION_PASS vl80s_core_packs=28 common_references=66 family_previews=84 forbidden_assets=0`. This confirms packaged resources and quarantines, **not** end-to-end device UI behavior.
- New unit tests cover candidate visibility, search, exact-model and variant separation, rejection of wrong layer/type/owner/status and exclusion of unverified actions, source claims and contraindication instructions from the read-only preview.

## Open group 2 blockers (do not close)

1. **Source-backed crew actions and contraindications are not complete.** The 44 candidate cards deliberately do **not** present an executable procedure or unverified prohibitions. The UI for `prohibited/stopConditions/reportFields` is wired for *published* scenarios, but no newly source-approved real crew scenario was published this run. Verify per-scenario source, exact model/variant, role, conditions, contraindications, stop points and escalation before enabling actions.
2. The remaining **59 of 103** VL80S runtime scenarios lack eligible STANDARD/CANDIDATE summaries in this particular registry intersection; assess recommended/extended/other statuses and preserve legitimate knowledge with correct mode-specific labeling rather than mass-promoting or mass-hiding.
3. Golden reference `vl80s.diag.pantograph-no-rise` requires full graph walk, verified source links, crew-only actions, explicit roof-access contraindications and acceptance tests. Current text-only preview does not replace it.
4. ER-DIAG-136, CHME3 and TEM2 source/profile/graph integration remain unapproved; family catalogs are still excluded from APK. Group 1 full family parity remains open. No depot-only work may appear as a locomotive-crew step.
5. Exact execution profiles, SOURCE links, standard vs explicitly opted-in extended material, warning acknowledgement, unsafe negative cases and real device navigation need further acceptance.
6. **Do not launch the parked comprehensive permissions/normative audit** from `docs/backlog/FUTURE_PERFORMANCE_AND_CREW_ACCESS_AUDIT.md` without a separate user instruction. Existing source-bound review needed for migration remains in scope.

## Next scheduled work

Proceed to **post-15 group 3/8: common knowledge, first aid, safety sources and content rights**, keeping group 2 `PARTIAL`. Return to all unresolved group 1/2 items after the first pass of the 7+1 queue. No physical-device tests or production release until final acceptance. The initial chat may not accept automation replies; Issue #4 and this checkpoint remain the durable record.
