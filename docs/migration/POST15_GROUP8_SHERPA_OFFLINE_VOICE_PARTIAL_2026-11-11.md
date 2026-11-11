# Post-15 remediation group 8/8 — Sherpa-ONNX offline voice (11.11.2026)

**Status: PARTIAL / NOT COMPLETE.** This run worked only the eighth independent group. Main migration stages fully completed remain **11/15**. This group does **not** close Stage 11, the Sherpa TODO, or Issue #4. Pinned Test- @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` was read-only.

## Source-to-source and provenance

- Donor branch `feature/offline-assistant-v0.9` @ `c3c2613d72ff2d520bb290aa473d0be1ca126f1a` contains `AssistantVoiceInput.kt`, `AssistantVoicePolicy.kt`, tests and references to Sherpa AAR, Silero VAD and Zipformer Russian int8 assets. Its Git tree contains **no AAR/ONNX binaries**.
- Existing `docs/migration/STAGE11_SHERPA_PROVENANCE_DEFERRED_2026-11-10.md` and CI `stage11-sherpa-provenance.yml` have already verified official Sherpa v1.13.4 AAR, VAD, model archive and four internal model SHA256 values and native arm64 ABI/API. **No repeat download or false claim of missing source code.**
- Publisher's derived Russian model card at https://huggingface.co/csukuangfj/sherpa-onnx-zipformer-ru-int8-2025-04-20 states origin at https://huggingface.co/alphacep/vosk-model-ru (Apache-2.0), but **does not itself declare redistribution license metadata**. Do not infer that the library license alone grants redistribution of model weights. Need a verified upstream conversion/license chain or permission/NOTICE evidence before packaging.

## Actual Kotlin/Compose/Gradle changes (Beta only)

**Implementation/test SHA `c788f2d30b0c6005e32325e509e2d195541fd683`** (initial `aa3d3ab8492aba8e15c31aaf59186dd6aa2ec9f1` was corrected before acceptance).

1. `AssistantVoiceButton.kt`: on Android **API 33+**, use the official `SpeechRecognizer.checkRecognitionSupport` API on the strictly **on-device** recognizer before recording. Start only when a **Russian language pack is already installed**. Pending/downloadable/unsupported packs and failed support checks show a precise text-input fallback; never auto-download or switch to a remote recognizer. Stale callbacks cannot restart a cancelled/destroyed session; the existing 20-second watchdog covers support checks too.
2. Android **API 31–32** retains the on-device-only SpeechRecognizer path, without an unavailable support-query API. API 26–30 remains text-only until licensed Sherpa binaries can be integrated. The transcript only fills the editable draft, never executes an action or bypasses assistant source/profile/safety gates.
3. `AssistantVoicePolicy.kt` adds a typed Russian pack decision `INSTALLED / NEEDS_DOWNLOAD / UNAVAILABLE` and locale normalization. New JUnit test covers six positive/negative pack cases including misleading language tags.
4. `app-shell/build.gradle.kts` adds `verifyNoUnlicensedSherpaAssets` as a `preBuild` dependency: accidental Sherpa AAR/model asset packaging fails until the separate license and pinned-manifest task is completed. This is **only a binary redistribution gate**, not a reference-knowledge visibility filter. No changes to locomotive family publication policies or to Test-.

## Verified checks

- Initial SHA `aa3d3ab8` had a real Kotlin test compilation failure (nested enum referenced via instance); fixed in final SHA `c788f2d3`. Do not report the initial run as green.
- Final **29/29 GitHub Actions workflow runs SUCCESS, terminal** at `c788f2d3`. Includes [Stage 11 voice #42982841604](https://github.com/DomEnota-hub/Beta/actions/runs/42982841604) (assistant-core tests, lint, AndroidTest compile, Debug APK), [Stage 15 #42982841821](https://github.com/DomEnota-hub/Beta/actions/runs/42982841821) (integration QA, Debug APK, negative checks) and [Modular bootstrap #42982850203](https://github.com/DomEnota-hub/Beta/actions/runs/42982850203).
- Stage 15 artifact `13837864567`: ZIP 9,264,717 bytes, SHA256 `9a37ef18b48f98edfa92eaca497cd0a1ec1284d7980b2eae9fccaecc82919e54`, integrity PASS. Extracted APK 9,647,965 bytes, SHA256 `2770078771a11b6c5ca99c83a2d135555b7be9f8aa1bd843219903a6fdc237e0`, APK ZIP integrity PASS, **zero Sherpa/assistant_voice files**. Manifest has RECORD_AUDIO and recognition-service query, **no INTERNET permission**.
- **Verified Google Drive delivery** (file metadata re-read): `RailBrake_Beta_1.2.2-modular-alpha01_post15-group8_debugQA_c788f2d3.apk`, size 9,647,965 bytes, parent `Rail` folder ID `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`, file ID `1v31RnKDU5JbnMyLmt2vr0LhIK2AgrNkj`: https://drive.google.com/file/d/1v31RnKDU5JbnMyLmt2vr0LhIK2AgrNkj/view . Under 100 MB, delivered as one APK; no split archive necessary.
- Previous group 7 CI is also now **28/28 SUCCESS** at `35aa5dcd`; its APK is independently present in Rail (ID `1MVX1DU99fYwqXP0lQOxSqZkHRhye7VAt`, 9,645,805 bytes). Previous group 6 APK is also now in Rail (ID `1b2FS391tVdbHMBUVv0jeiLECo6v8DqW7`, 9,642,701 bytes), superseding the earlier upload-failure checkpoint. These are **carry-over delivery corrections**, not closure of those groups.

## Mandatory open blockers

1. **TODO / REQUIRED_FOR_IMPLEMENTATION: Sherpa-ONNX offline voice.** Confirm the derived Russian model redistribution license/NOTICE and compatible pinned binary manifest; only then integrate official AAR + Silero + Zipformer assets, donor capture/VAD and API26–30. Maintain 20-second bound, cancellation, permission and source/role/profile/safety controls. Do not publish binaries until all evidence is verified.
2. Android device QA remains unperformed by agreement: microphone grant/deny, Russian installed/missing pack, API31–32/33+, offline/no network, cancellation, silence, timeout, ASR accuracy, app lifecycle and actual voice-to-editable-draft behavior.
3. Groups 1–7 remain PARTIAL with their separate unresolved source, feature parity, normative and device QA issues. Main stages 11, 13, 14, 15 still not fully accepted. The future full crew-permissions audit remains parked and must not be started here.

**Next hourly position:** return to the first unresolved remediation group **1/8**, apply concrete independent Kotlin/Compose/source-safe changes and checks. Sherpa remains open as group 8 for the next unresolved-position pass; do not repeat already completed artifact downloads without reason. No production release, no claim of complete migration. Original automation chat publication is not technically confirmed; the Issue #4 comment and this repository checkpoint are durable records.
