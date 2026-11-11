# RailBrakeCalculator — Stage 15/15 integration QA checkpoint (11.11.2026)

**Status: PARTIAL / CI-verified QA baseline, NOT completed full migration or device acceptance.**
**Fully completed earlier stages: 11/15 (1–10, 12).** Stage 11 (Sherpa-ONNX), Stage 13 (Ermak/CHME3/TEM2), Stage 14 (common normative completeness), and Stage 15 (device/end-to-end acceptance) remain incomplete. Do not close Issue #4 or claim a production-ready application.

## Immutable scope

- Beta branch: `audit/information-block-gaps-20261014`.
- Final **code/test/CI HEAD**: `10c4b3925a55f3f8ca4e9fed11d49a64462257b1`.
- Donor Test- **read-only** @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`.
- This run performed **only Stage 15**. Full normative audit of crew permissions remains explicitly **FUTURE/PARKED** in `docs/backlog/FUTURE_PERFORMANCE_AND_CREW_ACCESS_AUDIT.md`.

## Concrete engineering work (not just Markdown)

1. Updated `app-shell/src/androidTest/.../ShellHomeInstrumentationTest.kt`: removed obsolete expectation that assistant and occupational-safety routes lead to placeholders; verifies the actual common reference list of 22 and real assistant search.
2. Updated `WorkingModelSelectionInstrumentationTest.kt`: 2ЭС5К Atlas now requires explicit МСУД-Н/015 selection, displays an explicitly unverified donor summary only after selection, never borrows VL80S published content, and allows returning to VL80S.
3. Added `Stage15CommonReferenceNavigationTest.kt`: navigation across all four model-neutral common sections from a non-published locomotive (13+13+22+18), back navigation, first-aid summary with warning and **no unreviewed step-by-step procedure**.
4. Added `qa/check_stage15_integration_apk.py`: verifies the **actual built Debug APK** includes 28 required published VL80S core packs and their index/profile/feature indexes, 66 unique common references with source IDs and CANDIDATE/INFORMATION_ONLY status, and seven exact-model non-actionable donor previews. Rejects missing core assets, foreign-model source assertions, candidate/research directories, entire unreviewed family catalogs, unverified ONNX/Sherpa assets, executable steps in preview and accidental status promotion.
5. Added six `qa/test_stage15_integration_apk.py` tests including negative APK fixtures for missing published pack, leaked voice model, procedural preview, common source status promotion and unverified execution.
6. Added `.github/workflows/stage15-integration-qa.yml`: Kotlin/JVM tests, Android lint, Debug APK and AndroidTest APK **compilation**, six Python tests, actual-APK checks, Stage 13/14 source gates and an **unapproved Debug QA APK** GitHub Actions artifact for later manual device acceptance.

**Production Kotlin/Compose behavior is unchanged by Stage 15**: this stage repairs and extends regression tests and produces an independently audited QA artifact. No content is promoted to `ACTIVE`; no safety gate or variant check is bypassed.

## Verified terminal CI

- Initial run on intermediate SHA `1a73fbe0`: [Stage 15 #42933028810](https://github.com/DomEnota-hub/Beta/actions/runs/42933028810) **FAILED**. AndroidTest Kotlin compiler rejected invalid top-level imports `assertExists`/`assertDoesNotExist`. Fixed in commits `17837494`, `df5b9062`, `10c4b392`; these assertions are member functions of Compose SemanticsNodeInteraction.
- **Final Stage 15**: [#42933436649](https://github.com/DomEnota-hub/Beta/actions/runs/42933436649) **SUCCESS (terminal)**, `BUILD SUCCESSFUL in 3m 30s`, `:app-shell:testDebugUnitTest`, `:feature-safety:testDebugUnitTest`, `:app-shell:lintDebug`, `:app-shell:assembleDebug`, `:app-shell:assembleDebugAndroidTest`. The instrumentation APK **was built, not executed on an Android device**.
- Six Python integration-gate tests: `Ran 6 tests ... OK`.
- Actual APK checks: `STAGE15_APK_INTEGRATION_PASS vl80s_core_packs=28 common_references=66 family_previews=7 forbidden_assets=0`; `STAGE13_APK_QUARANTINE_PASS ... assets=87`; `STAGE14_COMMON_REFERENCE_PASS ... executable=0`; `STAGE13_DONOR_SUMMARY_PARITY_PASS entries=7 models=7 executable=0`.
- On the **final code HEAD `10c4b392`: 26/26 GitHub Actions workflow runs completed SUCCESS (terminal)**, including modular bootstrap, stage-specific CI and source parity. This proves only the automated gates, not functional parity or device behavior.
- QA artifact: [railbrake-stage15-debug-qa-unapproved](https://github.com/DomEnota-hub/Beta/actions/runs/42933436649/artifacts/13816793551), artifact ID `13816793551`, compressed ZIP size `9,204,463` bytes, uploaded 11.11.2026. Workflow log reports artifact ZIP SHA256 `2ba903a05fe6a6f71364394fe8fc627e0c05ca9bdf86b84cf1a659ca53fc0755`. **This is a Debug APK for testing, NOT signed production and NOT approved for operation.** Artifact retention: seven days.

## Important blockers and user-visible functional gaps

1. **Stage 11:** Sherpa-ONNX native offline recognizer not integrated; AAR, Silero and Zipformer files/hashes were located and checked in Stage 11, but derived-model redistribution rights/NOTICE and integration/device tests remain unresolved. Android on-device SpeechRecognizer fallback is only partial voice functionality.
2. **Stage 13:** Ermak, CHME3/Т/Э and TEM2/У still lack full published Atlas/Acceptance/Diagnostics routes. Whole family directories remain excluded from APK; seven summary-only previews are not a replacement. 548 Ermak reference occurrences, 610 CHME3 links, CHME3T №6245 split and ER-DIAG-136 remain source-review backlog. A migrated CANDIDATE status does **not** prove original donor information was forbidden to read.
3. **Stage 14:** 66 common summaries are visible, but 21 source records have not been independently checked for current editions; first-aid stepwise procedures and internal cross-links are not published. 329 exam questions require provenance/rights checks.
4. **Calculations:** VU-45 and securing screens have arithmetic preview and tests, but 2026 normative/TRA confirmation and operational approval remain incomplete.
5. **History:** no signed installed-app upgrade / real-device SharedPreferences migration test, no recovery QA for all other donor stores.
6. **Assistant:** text corpus tests pass, but the searchable published runtime remains VL80S-centered; source-backed family links, all legacy query variants and end-to-end device search need follow-up.
7. **Device QA:** no instrumentation tests were run on a phone/emulator in this stage; no accessibility, performance, battery, offline, lifecycle, app-upgrade, dark-mode or production-signature acceptance. No production release.

**Safety principle:** preserve readable technical knowledge with accurate source/variant/role/mode markings. Do not equate `CANDIDATE/UNKNOWN` with a universal prohibition on reading; do not equate a readable reference with permission to perform an action. Show confirmed crew-appropriate checks and contraindications, not depot repair procedures as crew instructions. Full comprehensive crew-permissions audit is a separate future decision.

## After Stage 15: exactly seven remediation groups + independent Sherpa group

These are **eight open backlog positions, not eight completed stages**. Use one future hourly run for one entire group when eligible; carry unresolved subissues forward without fake closure. Each must have a separate test/CI checkpoint and explicit acceptance criteria. Do not start group work during this Stage 15 run.

### 1. Family content, profile isolation and readable donor parity
**Includes:** blanket family asset exclusion; seven-only summary previews; missing Ermak/CHME3/TEM2 Atlas/Acceptance routes; 548/610 source-link gaps; CHME3T serial boundary; sourceRefs; exact MСУД-Н vs МСУД-015 applicability. **Owner:** family-runtime + source-review. **Depends on:** per-object Test- → Beta crosswalk, lawful content and source/variant evidence. **Done when:** previously readable legitimate knowledge is restored in APK/search/cards under correct standard/extended presentation, explicit execution and source labels, with positive/negative per-model tests; unreviewed actions never silently become executable.

### 2. Diagnostic flows, crew safety and contraindications
**Includes:** VL80S diagnostic graph coverage; ER-DIAG-136; family diagnostic routes; symptom branching; links; explicit contraindications, role/conditions/stop points and safe separation of reference vs action. **Owner:** diagnostic-review + safety-review. **Depends on:** verified scenario-specific sources and exact profiles. **Done when:** each accepted crew scenario has tested graph, source, applicability, permitted crew steps and contraindications, and unsafe/depot-only operations are not presented as crew instructions. **Do not initiate the separately parked full normative permissions audit without user approval.**

### 3. Common knowledge, first aid, safety sources and content rights
**Includes:** 66 summary cards, 21 source records, missing links, first-aid procedural validation, ОПП/ОТ/traffic-safety coverage, 329 exam-question rights. **Owner:** common-content + source-review + content-rights. **Depends on:** current documents and lawful reuse. **Done when:** source versions and provenance verified, accurate reference navigation restored, first-aid action cards released only when approved with warnings and safe instructions, rights unresolved content not copied unlawfully.

### 4. Calculations, VU-45 and securing normative acceptance
**Includes:** 2026-07-01 brake rules, VU-45 form fields and arithmetic checks, separate securing by mass vs Appendix 12, local TRA/conditions, rounding and edge cases. **Owner:** calculations + normative-review. **Depends on:** applicable current primary rules and local context. **Done when:** verified formula/field matrix and boundary tests exist; no operationally authoritative answer is shown without all required conditions.

### 5. History, working notes and installed-app migration
**Includes:** signed Test- → Beta upgrade, legacy StringSet records, malformed/collision handling, backups, model-scoped notes, diagnostic/acceptance/recent/settings stores. **Owner:** storage-migration. **Depends on:** signed test builds and real upgrade data. **Done when:** no data loss or silent cross-model leakage in upgrade, corruption, rollback and deletion tests on device.

### 6. Text assistant: corpus coverage, search and links
**Includes:** source-backed multi-family search, parser/lexicon and spoken query parity, ambiguous model resolution, exact card/source navigation, false positives and stale links. **Owner:** assistant-text. **Depends on:** family/common published reference routes. **Done when:** fixed corpus `query → intent → profile → canonical card → link → source` passes with no cross-model or unsafe action leakage and acceptable latency.

### 7. Whole-app integration, startup/performance, accessibility and release acceptance
**Includes:** synchronous VL80S startup bootstrap, memory/cache/index optimization, navigation back stack, accessibility, offline/lifecycle, instrumentation execution, signed QA, full APK content, performance baselines and final device manual acceptance. **Owner:** Android QA + release. **Depends on:** groups 1–6 for full functional parity; independent measurement can precede. **Done when:** release-like CI, device test matrix, memory/performance evidence, signing and explicit user acceptance pass. **No production release from CI alone.**

### 8. Sherpa-ONNX offline voice — separate mandatory TODO
**Includes:** derivative Zipformer license/attribution, pinned AAR/Silero/encoder/decoder/joiner/tokens, reproducible ABI/API packaging, microphone permission and cancellation, real Russian offline ASR, latency, no-network and safety-gated transcript routing. **Owner:** assistant-voice + model-license. **Depends on:** publisher's redistribution confirmation and verified model build. **Done when:** verified assets ship legally, voice works fully offline on supported Android devices and all CI/device/negative tests pass. **Keep TODO / REQUIRED_FOR_IMPLEMENTATION open.**

## Next concrete action

The next run should begin **post-15 group 1**, restoring safe, non-actionable previously readable family content via precise donor object mapping and separate source/variant/role gates; do not mass-promote `CANDIDATE` or disable existing safety checks. If the automation's own current-stage rule requires explicit state transition, use this checkpoint as the post-15 handoff; never report Stage 11/13/14/15 as fully completed.

**No physical-device testing performed; no donor modification; no normative permissions overhaul; no production APK release.**
