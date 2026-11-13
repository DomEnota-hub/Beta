# Post-15 remediation — second pass, group 8/8: voice lifecycle safety (11.11.2026)

**Group: IN_PROGRESS / SOURCE_BLOCKED (Sherpa model redistribution) / DEVICE_QA_PENDING.** Only group 8 worked this run. Main original stages fully completed remain **11/15**. Issue #4 stays OPEN. Donor Test- @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` untouched.

## Real user-visible Android correction

Code/test commit **`3dfbe53122709b531f4c3a15f29da367499cb0d8`**, corrected Android API lint guard in **`93ccbb8d433800eac3cab0bf164adc75d2d33af6`**.

Previously, if the user requested microphone permission and navigated away before answering, the permission callback could still call `start()` on the disposed Compose screen. Similarly, disposed recognition-support/recognition callbacks were not invalidated at the session layer. A late callback could restart the microphone or deliver text to a stale draft.

- `app-shell/src/main/java/ru/railbrake/calculator/shell/AssistantVoiceButton.kt`: each permission/recognition session receives a generation token. Cancelling, replacing a session or disposing the screen invalidates callbacks and prevents a late permission grant from starting the microphone. Explicit API31 guard is retained for minSdk26 lint. Offline-only recognizer availability probe now handles faulty service exceptions. Button can cancel a pending permission request; recognizer and watchdog are disposed.
- `assistant-core/src/main/kotlin/ru/railbrake/calculator/assistant/AssistantVoicePolicy.kt`: new pure Kotlin `AssistantVoiceSessionGate` generation/attach guard, no new voice permissions or recognition backend.
- `assistant-core/src/test/kotlin/ru/railbrake/calculator/assistant/AssistantVoicePolicyTest.kt`: two new regression tests for permission result after disposal and superseded/cancelled callbacks.
- No Sherpa binary assets added, no automatic recognition execution, no change to model/source/role/action safety gates.

## Verification and corrected failure

Initial commit `3dfbe531` **FAILED Android lint**: `createOnDeviceSpeechRecognizer` requires API31 and lint could not infer the SDK check hidden in a helper. This was corrected by explicit `Build.VERSION.SDK_INT < MIN_ON_DEVICE_API` check in `start()` in commit `93ccbb8d`. The first commit is **not** claimed green.

Final code SHA `93ccbb8d`: **29/29 GitHub Actions workflow runs terminal SUCCESS**. Notable runs:
- [Stage 11 voice tests, lint, AndroidTest compile, APK #43051149344](https://github.com/DomEnota-hub/Beta/actions/runs/43051149344): SUCCESS.
- [Stage 15 integration, APK gates #43051149273](https://github.com/DomEnota-hub/Beta/actions/runs/43051149273): SUCCESS.
- [Modular/Stage 51 #43051161802](https://github.com/DomEnota-hub/Beta/actions/runs/43051161802): SUCCESS.
- `assistant-core:test`, `app-shell:lintDebug`, `app-shell:assembleDebugAndroidTest`, `app-shell:assembleDebug` verified by CI. Android instrumentation **compiled but not executed on a phone**.
- Both APK ZIPs pass integrity; inspected final APK ZIP entries: **0 Sherpa/assistant_voice/ONNX files**.

## QA delivery (Google Drive Rail)

Drive folder ID `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`. Both APKs are **unapproved Debug/QA** version `1.2.2-modular-alpha01`, uploaded individually (<100 MB), Google Drive metadata confirms exact parent/name/size; Drive raw re-download SHA256 matches extracted CI artifact.

1. [Stage 15 Debug APK](https://drive.google.com/file/d/1_3BaYcf-coW2XhXpjxtfIIxaGqIjZKeQ/view): `RailBrake_Beta_1.2.2-modular-alpha01_group8-second-pass_stage15_93ccbb8d.apk`, **9,662,745 bytes**, SHA256 `66b55e28dfcff552cf2645bf121485a14ae5c317ce72528a66884e87fd76a575`. CI artifact `13869700661`, ZIP SHA256 `e1b81afc269d63145c98ecc696d4768d8b07bb885a4f02546ae858fdb48e4b22`.
2. [Stage 51 Debug APK](https://drive.google.com/file/d/15S2rTGP9RCA557LlliAIxfqrtVNnvlP4/view): `RailBrake_Beta_1.2.2-modular-alpha01_group8-second-pass_stage51_93ccbb8d.apk`, **9,662,905 bytes**, SHA256 `f05ffca6c3bfe3c029a2a6ee14114001e568aafb581af7013c3c0ae172e39e66`. CI artifact `13870810070`, ZIP SHA256 `52a933bac3ee3f06e7d506c2b7aaf5adb6ac6f326ed3068e94c619a5a9a3f18c`.

## Source/rights and exact next work

Targeted new review of the official [Sherpa Russian export workflow](https://github.com/k2-fsa/sherpa-onnx/blob/master/.github/workflows/export-russian-onnx-models.yaml) demonstrates direct sourcing from licensed `alphacep/vosk-model-ru` for the **2024** export, not a definitive redistribution grant for the **2025-04-20 derived** weights. The upstream [Alphacep model](https://huggingface.co/alphacep/vosk-model-ru) declares Apache-2.0; the [derived 2025 model](https://huggingface.co/csukuangfj/sherpa-onnx-zipformer-ru-int8-2025-04-20) still lacks an explicit license/NOTICE. Third-party classification is not authoritative evidence. **Sherpa TODO remains SOURCE_BLOCKED** until exact 2025 conversion/provenance and redistribution license/NOTICE are verified. Do not repeat artifact downloads without new evidence. No binary integration or API26–30 voice parity is claimed.

Device QA remains: permission grant after navigation, denied/allowed microphone, Russian pack installed/missing, API31–32/33+, cancellation, timeout, offline airplane mode, editable transcript and no automatic action.

**Next scheduled group 1/8 (third pass):** inspect `app-shell/build.gradle.kts` family asset exclusions, `qa/check_stage13_apk_quarantine.py`, `FamilyPublicationGate.kt` and pinned Test- assets; restore one source/right/profile-verified full reference path to actual APK and Atlas UI with positive/negative tests, without mass ACTIVE or unsafe action publication. Continue other independent group 1 work if a specific external source is blocked. Group 8 remains open for the next unresolved pass.
