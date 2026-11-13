# Stage 11/15: Sherpa-ONNX provenance and deferred integration (10.11.2026)

**Decision: REQUIRED_FOR_IMPLEMENTATION / DEFERRED.** Stage 11 remains incomplete. The Android 12+ on-device SpeechRecognizer fallback from `daf89094c42c404600c1f2ab583a4b562326e327` remains available, source/profile/safety-gated, and does not use network recognition. The next hourly run must proceed to stage 12, not repeat this search.

## Verified discovery, 10 November 2026

- Donor read-only branch `Test-:feature/offline-assistant-v0.9` @ `c3c2613d72ff2d520bb290aa473d0be1ca126f1a` contains `AssistantVoiceInput.kt`, `AssistantVoicePolicy.kt`, tests and Gradle `implementation(files("libs/sherpa-onnx.aar"))`. It does **not** contain the referenced AAR or ONNX files.
- Sherpa official release v1.13.4: https://github.com/k2-fsa/sherpa-onnx/releases/tag/v1.13.4 . `sherpa-onnx-1.13.4.aar`, 48,847,529 bytes, SHA256 `03f9c4df965f21c71269365a7951a7f23b5696fddd093fa318c80d65550ab780`.
- Sherpa official `asr-models` release: https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models . `silero_vad.onnx`, 643,854 bytes, SHA256 `9e2449e1087496d8d4caba907f23e0bd3f78d91fa552479bb9c23ac09cbb1fd6`.
- Same release: `sherpa-onnx-zipformer-ru-int8-2025-04-20.tar.bz2`, 60,239,942 bytes, SHA256 `d6a651569aacc9a177259fa54705dd76acae23f6a4d62ea6797bd220d4b57163` (computed on downloaded official release archive). Four required model files inside:
  - `encoder.int8.onnx` SHA256 `eb6c12fbad810d5bc3e427802e604604c69b5943a91feebc43424dd09d9ec407`;
  - `decoder.onnx` SHA256 `dcbe1ffa0211e77ca6d3a80164df13fbda3ec00e47d12b9f449f89572df12136`;
  - `joiner.int8.onnx` SHA256 `93f2e1d12b78d53e7802f1606488c14bb3d764b15fadf5ef6c022f6ba1fa40f7`;
  - `tokens.txt` SHA256 `93bbbc0bae6b78c0bbb743d4aa9fded3bb5ff3aac5f0200e3a769a5a05e0fdf6`.
- Publisher's model copy: https://huggingface.co/csukuangfj/sherpa-onnx-zipformer-ru-int8-2025-04-20/tree/main . The three ONNX file SHA256 values match the publisher's displayed file digests. Source model: https://huggingface.co/alphacep/vosk-model-ru , metadata `license: apache-2.0`. **The derived model's own model card has no license metadata**; origin alone is not a definitive redistributable-weights license grant.
- Silero VAD repository: https://github.com/snakers4/silero-vad (MIT). Sherpa library: https://github.com/k2-fsa/sherpa-onnx (Apache-2.0).

## CI evidence

The workflow `.github/workflows/stage11-sherpa-provenance.yml` actually downloaded all three official release assets on a GitHub runner, checked pinned SHA256 for the AAR, VAD, model archive and individual model files, rejected unsafe archive entries, and verified Android native ABIs. It does **not** publish binary assets or add them to the APK.

- Initial discovery and hashes: https://github.com/DomEnota-hub/Beta/actions/runs/42866530843 (terminal SUCCESS).
- Pinned per-file verification: https://github.com/DomEnota-hub/Beta/actions/runs/42866691687 (terminal SUCCESS).
- A subsequent run verifies the exact donor-required AAR Java API classes.

## Unfinished, mandatory before claiming Sherpa integration

- [ ] Confirm derivative model redistribution license and required attribution/NOTICE from model publisher or documented upstream conversion/license chain.
- [ ] Integrate pinned AAR and ONNX assets into Beta with a reproducible, size-aware Gradle build; confirm API compatibility, Android 26–30 support, memory use and offline-only execution.
- [ ] Connect donor `AssistantVoiceInput` to existing guarded assistant draft UI, preserving explicit user confirmation and no automatic action.
- [ ] Complete unit/lint/assembleDebug/instrumentation CI and final on-device tests: permissions, silence, cancellation, 20-second bound, Russian recognition, no network and safety-gated search.

**Do not mark stage 11 complete, do not claim full voice parity, and do not block independent stages 12–15.** This TODO remains part of Issue #4 until closed with evidence.
