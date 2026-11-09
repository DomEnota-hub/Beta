# Data-level inventory, pass 1 — 2026-11-09

Read-only donor: `DomEnota-hub/Test-` at `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Target: `DomEnota-hub/Beta` at `f41aaa10c4fac587058ddec2b8beba42f3cd0834`.

## Reproducible repository-tree count
Source: GitHub Git Trees recursive endpoint; count **blob files** below each `content-packs/<electric|diesel>/<model>/` prefix. These are **file counts, not equipment objects or verified migrated records**. Directory placeholders and research files count as files.

| Model block | Files | Acceptance | Atlas | Diagnostics | Technical data | Other | Bytes (all files) |
|---|---:|---:|---:|---:|---:|---:|---:|
| VL80S | 108 | 5 | 25 | 46 | 16 | 16 | 5,327,298 |
| Ermak | 77 | 2 | 10 | 13 | 13 | 39 | 6,905,343 |
| CHME3 family | 128 | 1 | 2 | 80 | 35 | 10 | 7,049,150 |
| TEM2 family | 62 | 3 | 4 | 34 | 14 | 7 | 2,423,792 |
| **Total** | **375** | **11** | **41** | **173** | **78** | **72** | **21,706,583** |

**Interpretation:** source material exists for every family, but counts cannot establish completeness against the Test donor because Test stores technical assets under `app/src/main/assets/technical/` and other locations, while Beta splits and transforms them. A file-by-file name comparison would be invalid. Next pass must parse and compare *semantic records* by stable IDs, profiles and source provenance.

## Critical integration finding
- `app-shell/build.gradle.kts` depends on `assistant-core`, `feature-acceptance`, `feature-atlas`, `feature-diagnostics`, `feature-safety`, etc.
- It does **not** depend on `feature-calculations` or `feature-history`. Even their existing code is currently not wired into the shipped application.
- `app-shell/src/main/java/ru/railbrake/calculator/shell/MainActivity.kt` loads VL80S-only vertical slice.
- `assistant-core` has a model-scoping contract but not donor's text/voice engine.

## Gate before implementation
1. Expand semantic record parity per model and category using stable IDs and profile-aware applicability; distinguish `published`, `candidate`, `research`, `missing`, `duplicate`, `unknown provenance`.
2. Establish shell navigation/working-model contract with **no implicit VL80S selection** and no cross-model leakage. Verify existing profile loader and runtime index before wiring UI.
3. Add calculation/history module dependencies only together with a real user route and tests; don't advertise functionality from Gradle inclusion alone.
4. Do not promote research diagnostics to APK. Verify source, variant and role/safety gates separately.
5. Physical-device QA remains outstanding.

## Verification limits
This is a **Git-tree and selected source-code audit**. It does not certify record-level donor parity, Android UI completeness, numeric regulatory correctness, or successful on-device voice inference. Do not use 375 as a percentage denominator.
