# Post-15 remediation group 5/8, second pass: read-only legacy history recovery

Date: 2026-11-11. **Status: IN_PROGRESS; implementation verified in CI, device QA deferred.** Only group 5 was worked. Main stages remain **11/15** fully verified in their previously accepted scope. Issue #4 remains OPEN. Pinned Test- `3176d6ee228f0ed4b78371f45209e10c1c724eff` was READ-ONLY.

## Actual user-visible implementation

Code/test SHA: [`c942449dfc5b5c2acafa8aa538acc077b53e36d0`](https://github.com/DomEnota-hub/Beta/commit/c942449dfc5b5c2acafa8aa538acc077b53e36d0).

- In **История и рабочие записи → История расчётов**, if the modern `railbrake_history_v2/records_v2` store cannot be read, the screen no longer shows only an empty history. It attempts a **read-only preview** of the original Test- `calculation_history/records` StringSet, if that original backup is readable. Neither the corrupt modern store nor the original donor store is modified.
- The UI clearly labels the recovery preview, shows counts of malformed donor entries and valid entries beyond the normal 30-record display limit, and **disables destructive history clearing** while recovery is active. This is not a destructive repair and does not claim recovery of records created only in the damaged v2 store.
- Switching to the notes or diagnostic tab clears stale cross-tab errors and does not show stale records after a failed read. A corrupted notes store still blocks note writes; no profile/action gates changed.
- New typed `LegacyHistoryBackup` and `LegacyHistoryRecovery` contract, `HistoryCodec.inspectLegacy`, Android implementation, Compose recovery view, **two new JUnit cases** for corrupt/overflow reporting, unchanged source and same-timestamp records.
- Five changed source/test files: `HistoryContracts.kt`, `HistoryCodec.kt`, `AndroidHistoryStores.kt`, `HistoryAndNotesScreen.kt`, `HistoryCodecTest.kt`.
- **No data copied to repository; 0 new operationally authorized actions.** All history remains local. No production release.

## CI, APK and delivery evidence

On code/test SHA `c942449d`, **29/29 GitHub Actions workflow runs terminal SUCCESS**. [Stage 7 #43021280724](https://github.com/DomEnota-hub/Beta/actions/runs/43021280724): `:feature-history:test`, `:app-shell:assembleDebugAndroidTest`, `:app-shell:lintDebug`, `:app-shell:assembleDebug`; `BUILD SUCCESSFUL in 3m 52s`. [Stage 15 #43021280838](https://github.com/DomEnota-hub/Beta/actions/runs/43021280838) SUCCESS; [Modular #43021291380](https://github.com/DomEnota-hub/Beta/actions/runs/43021291380) SUCCESS. AndroidTest **compiled, not executed** on a device.

Two distinct, integrity-checked **unapproved Debug/QA APKs**, version `1.2.2-modular-alpha01`, were uploaded to Google Drive folder `Rail` (ID `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`). The original GitHub artifact ZIP and extracted APK passed ZIP integrity checks; Drive metadata confirmed exact name, size, folder; both Drive copies were re-materialized and SHA256 matched the local extracted APK.

1. Stage 15 artifact `13854104963`: [`RailBrake_Beta_1.2.2-modular-alpha01_post15-group5-second-pass_stage15_c942449d.apk`](https://drive.google.com/file/d/1PPMhxXxUEO302KC-o80ctZUSo518MqaE/view), **9,659,665 bytes**, SHA256 `d48a91d2034bc31e5e7693f768cb6c73f1a09f90c0ad97b26fb98fa95109b3f9`.
2. Stage 51 artifact `13854893421`: [`RailBrake_Beta_1.2.2-modular-alpha01_post15-group5-second-pass_stage51_c942449d.apk`](https://drive.google.com/file/d/1Qy_-yioG-JyHbWhldb_1QT5ozP9MRP5W/view), **9,659,581 bytes**, SHA256 `84108774576b7487c586b639d7e1cda70853215dd8978dba9dd9c9dbf3b90850`.

## Unfinished group 5 acceptance

- Signed in-place Test-→Beta upgrade with actual original SharedPreferences and compatible signing identity; backup, restart, rollback, low-storage and corrupted-type device tests. **Owner:** Android/release QA. No device verification claimed.
- Per-execution legacy acceptance state mapping `technical_acceptance_states`, recent-material IDs `technical_recent_materials`, display settings `knowledge_display_v2`, extended-mode opt-in. **Owner:** shell/content/profile migration; require exact source IDs, profile isolation and negative tests. Do not infer mappings.
- Ermak/CHME3/TEM2 diagnostic archive profile aliases remain intentionally unresolved; no guessed cross-family mapping. **Owner:** family source/profile review.
- Work-note storage policy for the `Рабочий` profile and real-device failure/restore testing remain pending. No silent repair of damaged v2 storage is attempted.
- Group 5 remains **IN_PROGRESS / DEVICE_QA_PENDING** for full acceptance. No source/action status promoted. Comprehensive deferred permissions audit remains PARKED.

## Exact next action

Next scheduled position **group 6/8 (second pass):** pick one currently failing assistant query→intent→model→card→source route or false-positive from the existing corpus, fix actual Kotlin/Compose runtime, add positive/negative regression tests, run CI to terminal and deliver unique APK(s) to Rail. Return to group 5 after the queue pass; do not close Issue #4.
