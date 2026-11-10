# RailBrakeCalculator — functional migration baseline (2026-11-09)

## Scope and immutable references
- Donor (read-only): `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`.
- Target: `DomEnota-hub/Beta` branch `audit/information-block-gaps-20261014`, baseline `4ab6e35a021d089cae5ad90ffb8ce3ec5f8abec5`.
- This is a **functional readiness baseline**, not a runtime approval or device-QA certificate.
- Diagnostic research stage 51/51 is a separate completed scope. Its 331 research candidates remain non-executable until source/profile/safety review and explicit promotion.

## Evidence-based gap register
| ID | Function | Donor evidence | Beta evidence | Status / next acceptance gate |
|---|---|---|---|---|
| MIG-01 | Multi-model home and navigation | `app/.../ui/HomeScreen.kt`, `BrakeCalculatorApp.kt` | `app-shell/.../MainActivity.kt` loads a VL80S-only vertical slice | PARTIAL: implement agreed home, working-model selection, drawer, settings and model-specific routes; instrument navigation |
| MIG-02 | Text assistant | `core/assistant/AssistantEngine.kt`, `AssistantQueryParser.kt`, `AssistantIndex.kt`, `AssistantRuntime.kt`, tests | `assistant-core/.../AssistantScope.kt` only | CONTRACT ONLY: migrate index, query/clarification/routing, source-backed cards and tests; fail closed on missing/unknown model |
| MIG-03 | Voice assistant | `core/assistant/AssistantVoiceInput.kt`, `AssistantVoicePolicy.kt`; Sherpa-ONNX + Silero VAD | No voice implementation found in `assistant-core` | NOT MIGRATED: verify legal model binaries/dependencies, permissions, offline ASR, lifecycle, cancellation, device latency, failure modes |
| MIG-04 | VU-45 verification | Agreed redesigned specification, not equivalent to legacy mass calculation | `feature-calculations/.../BrakeCalculator.kt` supports mass/Appendix 12; no VU-45 verification UI identified | PLANNED: freeze field/rule matrix, independently persisted axes/wagons drafts, disabled rows, complete results; validate against effective 2026-07-01 regulations |
| MIG-05 | Train securing | Donor calculator engine and UI | Mass/Appendix 12 engine in `feature-calculations`, no integrated screen in shell | ENGINE ONLY: distinct «По массе» and «ИДП №12» flows, source matrix, boundary/rounding regression |
| MIG-06 | Calculation history and working notes | Verified `HistoryRepository.kt` inside pinned `RailBrakeCalculator.zip` (Git blob `d95a2ce465e2f09bb96d74b8318f36b16d21afd0`), absent from donor tree | `docs/data-migration/legacy-zip-member-manifest.json`; draft PR #2 read-only codec; `feature-history/.../HistoryContracts.kt`, `legacyFormatVerified=false` | FORMAT OBSERVED, MIGRATION NOT IMPLEMENTED: SharedPreferences `calculation_history` / StringSet `records`, max 30, Base64 URL-safe five-field rows; implement backup, reader/writer, collision/malformed policy, signed upgrade tests and UI |
| MIG-07 | VL80S atlas/acceptance/diagnostics | Donor technical assets and screens | VL80S shell slice, feature modules, content packs | PARTIAL: compare individual donor objects, references, links, variants and user journeys |
| MIG-08 | Ermak, CHME3/T/E, TEM2/U feature UI | Donor content, variant profiles, screens | Content packs and research candidates | CONTENT EXISTS / UI UNPROVEN: build cross-model navigation and variant-gated acceptance/atlas/diagnostics journeys |
| MIG-09 | Common knowledge, safety, first aid | Donor common screens/assets | Common content packs, safety feature | PARTIAL: verify parity, provenance, internal links, user entry points |
| MIG-10 | Final Android QA | Donor tests and existing UI | CI + `assembleDebug` and final diagnostic handoff | DEFERRED: full physical-device QA, usability, storage migration, performance, ASR offline and accessibility |

## Next implementation sequence (do not conflate with diagnostic stages)
1. **Inventory parity:** produce source-to-target manifest for each user-visible function and data object, with source path/hash, target path, status `MIGRATED/PARTIAL/CANDIDATE/PLANNED/BLOCKED`, test evidence and owner. Count objects only after exact matching. No code changes to donor.
2. **App shell:** replace VL80S-only entry with working-model selection and agreed home/navigation; connect existing feature modules with fail-closed model/variant checks. Add instrumentation smoke tests.
3. **Calculations:** independently implement VU-45 verification and securing UI; confirm normative source and execution rules before publishing numerical guidance.
4. **History:** use the verified pinned donor ZIP `HistoryRepository.kt` format, implement safe migration without losing existing user data, and implement working notes; do not treat the draft read-only codec as a complete migration.
5. **Assistant:** port text/index first, then offline voice ASR with verified model packaging. No generative language model is established by the inspected code; do not label rule-based retrieval as an LLM.
6. **Cross-model completion:** acceptance, atlas, schemes, knowledge, safety, diagnostics runtime promotion only after provenance/safety gates.
7. **Release acceptance:** full CI, negative tests, device QA and a signed QA APK; no production approval by build success alone.

## Non-negotiable acceptance
- Unknown execution/profile/variant: fail closed, no unsafe instructions or inferred applicability.
- Historical/field-practice and research content never silently becomes executable.
- For every function: demonstrate actual app entry, data load, navigation, persistence where applicable, error state, automated test, and device QA status.
- Keep diagnostic research 51/51 separate from **whole-app functional completion**. Do not report an overall readiness percentage without an agreed denominator and evidence.
