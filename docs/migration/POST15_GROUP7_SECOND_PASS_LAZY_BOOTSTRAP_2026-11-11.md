# Post-15 group 7/8, second pass: lazy VL80S runtime and model-safe navigation

Date: 2026-11-11. **GROUP 7 IN_PROGRESS / DEVICE_QA_PENDING**, not accepted. Main stages previously verified **11/15**, epic #4 remains OPEN. Exactly one group worked. Test- pinned donor `3176d6ee228f0ed4b78371f45209e10c1c724eff` was not changed.

## Verified user-facing implementation

**Observed defect in Beta source:** selecting VL80S on the home screen immediately started the full VL80S runtime bootstrap, even when opening only calculations, common knowledge, first aid, notes or settings. This did not respect feature-level demand and could delay independent sections.

- [`a8524ff5`](https://github.com/DomEnota-hub/Beta/commit/a8524ff52648e1f52249952baf0fabc89cea7708): `Vl80sBootstrapPolicy.shouldRequest` explicitly allows bootstrap only for **Assistant, Atlas, Diagnostics, Acceptance** on published exact VL80S. Home and independent sections do not request it. Other models and unknown model IDs never request VL80S.
- [`7fb2c346`](https://github.com/DomEnota-hub/Beta/commit/7fb2c3467ff67d44727161eca9b74049d07ef4ff): `MainActivity` lazily starts the IO bootstrap on the first relevant destination, retains its result across navigation for the same model, and keys the state by model ID to prevent old-profile runtime visibility. Restored navigation can request it again. No runtime or safety gate was relaxed.
- **Final code/test SHA [`1c91164b`](https://github.com/DomEnota-hub/Beta/commit/1c91164b845406d3e7f02d094c608533f37bf2d9)**: two additional JUnit tests cover all four requesting destinations, ten independent destinations, all seven other models, unknown IDs and no model.

This is **deferred loading, not a measured speedup**. No device startup timings were collected. **0** new content cards, **0** new diagnostic graphs, **0** new crew-action permissions. Existing published-content and fail-closed boundaries unchanged.

## CI, APK and delivery

**28/28 GitHub Actions runs at code SHA `1c91164b` terminal SUCCESS**, including:
- [Stage 2 navigation #43039375508](https://github.com/DomEnota-hub/Beta/actions/runs/43039375508): `navigation-contracts:test`, AndroidTest compilation, `lintDebug`, `assembleDebug`; BUILD SUCCESSFUL in 3m40s.
- [Stage 15 integration #43039375737](https://github.com/DomEnota-hub/Beta/actions/runs/43039375737): `:app-shell:testDebugUnitTest` (includes new bootstrap tests), lint, assembleDebug, AndroidTest compilation, real APK content gate; `STAGE15_APK_INTEGRATION_PASS vl80s_core_packs=28 common_references=66 family_previews=84 forbidden_assets=0`. This is **not** full family parity.
- [Modular / Stage 51 #43039388480](https://github.com/DomEnota-hub/Beta/actions/runs/43039388480): terminal SUCCESS; research candidates remain isolated and production unapproved. AndroidTest compiled, **not run on phone**.

Both unique **unapproved Debug/QA APKs**, version `1.2.2-modular-alpha01`, delivered individually (<100 MB) to the existing Google Drive **Rail** folder `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`, Drive parent/name/size verified and re-downloaded with matching SHA256:
1. [Stage 15 APK](https://drive.google.com/file/d/1atOyZbH6F9S89RGLouXU0BJlQ8ebQLcD/view) `RailBrake_Beta_1.2.2-modular-alpha01_post15-group7-second-pass_stage15_1c91164b.apk`; **9,660,873 bytes**; SHA256 `2e74e2bffdf199ec105b0c00ab2a89c298a634ad811180647b6779d22ab9d31c`; artifact `13864723191`.
2. [Stage 51 APK](https://drive.google.com/file/d/12P0TYi92CXWec3Yj5m6n1CrUjtKgrfPv/view) `RailBrake_Beta_1.2.2-modular-alpha01_post15-group7-second-pass_stage51_1c91164b.apk`; **9,660,973 bytes**; SHA256 `ddf0810ee4cb9cc43fdcc96fa2535f91e6143eaebfdc48630b0077d6f31f08fa`; artifact `13863979997`. ZIP and extracted APK integrity PASS.

## Remaining and next exact action

Group 7 still requires **measured** cold/warm load timing and memory profiling on real device, actual lifecycle recreation/model switching, full offline search, navigation/backstack and real-world UI QA; no measured speed claim. Stage 15 and full family content parity remain open. No production release. Do not trigger the parked full permissions audit.

**Next scheduled position: group 8/8 Sherpa-ONNX.** Read existing pinned model/ABI/license research; do not redo it without new evidence. Check exact remaining redistribution rights, NOTICE and API26–30 integration; if still blocked, record specific SOURCE_BLOCKED items and proceed to next group-1 cycle without publishing unlicensed binaries. Source automation chat cannot be written to from this run; this checkpoint and Issue #4 comment are the durable report.
