# Functional migration parity manifest — pass 1 (2026-11-09)

Source snapshot: `DomEnota-hub/Test-` at `3176d6ee228f0ed4b78371f45209e10c1c724eff` (read-only). Target snapshot: `DomEnota-hub/Beta` at `f170715c85a028c3994787a3a7c622a3ce7e15ae`, branch `audit/information-block-gaps-20261014`.

This inventory maps **functional source units**, not every JSON entry. Statuses: `MIGRATED` (implemented and integrated with evidence), `PARTIAL` (some implementation, not full user journey), `CONTRACT_ONLY` (API/shape, no complete feature), `NOT_MIGRATED`, `REQUIRES_VERIFICATION`. No module is promoted to `MIGRATED` merely because a file exists.

| ID | Donor source (relative to Test-) | Beta target/evidence | Status | Acceptance blocker |
|---|---|---|---|---|
| UI-01 | `app/src/main/java/ru/railbrake/calculator/ui/HomeScreen.kt` | `app-shell/src/main/java/ru/railbrake/calculator/shell/MainActivity.kt` | PARTIAL | Shell currently boots VL80S vertical slice; add agreed multi-model home and drawer |
| UI-02 | `app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt` | `app-shell/.../MainActivity.kt` | PARTIAL | Cross-feature routes, calculations, history, assistant, settings not connected |
| AS-01 | `app/src/main/java/ru/railbrake/calculator/core/assistant/AssistantEngine.kt` | `assistant-core/.../AssistantScope.kt` | CONTRACT_ONLY | Port engine and safety/clarification regression |
| AS-02 | `app/src/main/java/ru/railbrake/calculator/core/assistant/AssistantIndex.kt` | No equivalent implementation identified | NOT_MIGRATED | Port indexed retrieval with scoped data |
| AS-03 | `app/src/main/java/ru/railbrake/calculator/core/assistant/AssistantQueryParser.kt` | No equivalent identified | NOT_MIGRATED | Query intent, series/variant and ambiguity tests |
| AS-04 | `app/src/main/java/ru/railbrake/calculator/core/assistant/AssistantContentLoader.kt` | `content-runtime/` generic loaders only | PARTIAL | Build assistant-specific source-grounded document adapter |
| AS-05 | `app/src/main/java/ru/railbrake/calculator/core/assistant/AssistantRuntime.kt` | `AssistantScope.kt` only | CONTRACT_ONLY | Lifecycle, index invalidation, model switching |
| AS-06 | `app/src/main/java/ru/railbrake/calculator/core/assistant/AssistantConversation.kt` | No equivalent identified | NOT_MIGRATED | Session context and no cross-model leakage |
| AS-07 | `app/src/main/java/ru/railbrake/calculator/core/assistant/AssistantVoiceInput.kt` and `AssistantVoicePolicy.kt` | No equivalent identified | NOT_MIGRATED | Verify Sherpa-ONNX AAR, offline model asset packaging, VAD, mic permissions, lifecycle |
| AS-08 | `app/src/main/java/ru/railbrake/calculator/ui/AssistantHomePanel.kt`, `AssistantResultActivity.kt` | No assistant UI in shell | NOT_MIGRATED | Agreed 3–5 results, show more, preserved query, source cards |
| CAL-01 | `app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt` (MassScreen, AppendixScreen) | `feature-calculations/.../BrakeCalculator.kt` | PARTIAL | Calculation engine present, UI not integrated; independent modes and numerical parity |
| CAL-02 | Agreed redesigned VU-45 specification (not proven to exist as donor code) | No dedicated VU-45 implementation identified | NOT_MIGRATED / DESIGN | Establish normative field and formula matrix; do not mistake mass calculator for VU-45 |
| HIS-01 | `app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt` (HistoryScreen) | `feature-history/.../HistoryContracts.kt` | CONTRACT_ONLY | Storage implementation and UI |
| HIS-02 | Legacy `HistoryRepository` referenced by donor `BrakeCalculatorApp.kt` | `HistoryStorageMigrationGate.legacyFormatVerified=false` | REQUIRES_VERIFICATION | Identify exact legacy storage, migration/rollback tests |
| PREF-01 | `app/src/main/java/ru/railbrake/calculator/data/WorkingLocomotiveRepository.kt` | `AssistantScope.kt` (context only) | CONTRACT_ONLY | Persist working model, maintain explicit-other-model query without mutation |
| ACC-01 | `app/src/main/java/ru/railbrake/calculator/data/AcceptanceStateRepository.kt` | `feature-acceptance/.../AcceptanceState.kt` | PARTIAL | Persistence parity and all models' routes |
| ATLAS-01 | `app/src/main/java/ru/railbrake/calculator/ui/StepwiseSchemeViewer.kt` | `feature-atlas/` flow and scheme classes | PARTIAL | Tap-target and variant-gated Android visual regression |
| KNOW-01 | `app/src/main/java/ru/railbrake/calculator/ui/KnowledgeBaseScreen.kt` | `content-packs/common/knowledge/` | PARTIAL | User entry, search, links, source/version audit |
| SAFE-01 | `app/src/main/java/ru/railbrake/calculator/ui/SafetyScreen.kt`, `FirstAidScreen.kt` | `feature-safety/`, `content-packs/common/first-aid/` | PARTIAL | First-aid UI entry and verified sources |
| DIAG-01 | `app/src/main/java/ru/railbrake/calculator/ui/LocomotiveDiagnosticsScreen.kt` | `feature-diagnostics/` + authoring packs | PARTIAL | Research candidates stay non-executable; runtime promotion by provenance/profile/safety gate |

## Implementation gates
1. Before UI changes: inspect target `settings.gradle.kts`, `app-shell/build.gradle.kts`, navigation and model/profile contracts. Make a minimal multi-model entry with **no fallback to VL80S** on unknown selection.
2. Before calculation changes: compare legacy `BrakeCalculator` against Beta and test numeric boundaries. Treat redesigned VU-45 as **new feature**, not an existing donor migration.
3. Before history changes: find legacy `HistoryRepository` implementation and exact preference keys/JSON shape; write migration tests before persistence.
4. Before voice changes: verify availability/licensing of required model files and AAR; do not claim speech recognition works from source code alone.
5. Before claiming complete: entry point + model/variant gate + data provenance + test + device QA for every row.

## Next pass
Expand each of the above into data-level counts and source-to-target hashes for VL80S, Ermak, CHME3/T/E and TEM2/U; classify duplicates, unknown profiles, unresolved links, missing UI and non-executable candidate packs separately. This first pass intentionally makes **no fabricated completeness percentage**.
