# Stage 13/15 — packaged family quarantine, verified (2026-11-10)

**Status: PARTIAL, NOT CLOSED.** Fully completed main stages: 11/15 (1–10, 12).
Stage 11 Sherpa-ONNX and Stage 13 family runtime remain open. Do not start Stage 14 on this checkpoint.
Pinned donor `Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` was not modified.

## Why this code change was necessary

The prior Stage 13 Kotlin source/profile gate hid CANDIDATE/UNKNOWN entries in UI, but
`app-shell` still included the entire `content-packs` tree as APK assets.
Real family files such as `chme3-family/technical-data/catalog/catalog-01.pack.json`,
`tem2-family/technical-data/catalog/catalog-01.pack.json` and
`ermak/technical-data/knowledge/knowledge-01.pack.json` contain candidate
entries despite their neutral `.pack.json` filenames. UI filtering is not APK quarantine.

## Actual changes

- `app-shell/build.gradle.kts`: aapt asset ignore rules now exclude complete
  `electric/ermak`, `diesel/chme3-family`, `diesel/tem2-family`, and
  `locomotive-migration` directories until an independently reviewed published
  runtime is available. Existing VL80S published assets are preserved.
- `qa/check_stage13_apk_quarantine.py`: opens the **assembled APK**, fails on
  family/research/migration asset leaks, and requires the published
  `assets/electric/vl80s/runtime-index.json` to remain present.
- The Stage 13 dedicated workflow and full modular workflow both invoke this
  packaged-APK check after `assembleDebug`.

**User-visible effect:** no unreviewed Ermak/CHME3/TEM2 material can be extracted
from the APK as shipped data. The family execution-selection screens remain
available, but they correctly show that no verified published family cards exist.
This is a safety correction, **not** completion of family Atlas/Acceptance/Diagnostics.

## Commits and terminal CI

- `936db45e730dad46da663a2c2f52513712b4db86` — Gradle quarantine and APK guard.
- `09ddbd0234255e1844ae64f607af30ad4f39f9e5` — full modular CI regression guard.
- Full modular CI: https://github.com/DomEnota-hub/Beta/actions/runs/42896647856
  **SUCCESS terminal**, job `validate` 130111389892. Steps 259 contract/runtime
  tests, 260 Android lint, 261 Debug APK, 262 indexed VL80S APK assets, 263 Stage 50
  research boundary, 264 Stage 13 packaged-family quarantine, 265 Stage 51 research
  corpus, and 266 Stage 51 debug APK evidence all **SUCCESS**.
- Stage 13 guard output: `STAGE13_APK_QUARANTINE_PASS app-shell-debug.apk assets=86`.
  Gradle log includes `BUILD SUCCESSFUL` for Android compilation.
- Device testing remains reserved for final manual QA. No production release.

## Remaining blockers / next concrete action

1. Family cards are still `CANDIDATE/UNKNOWN`. Confirm real manufacturer or current
   official sources, exact edition, sourceRefs and model/execution applicability
   **per object**, including MSUD-N/MSUD-015, CHME3T #6245 boundary, TEM2/TEM2U.
2. After independently approving at least one real information card and its source
   per family, introduce a **narrow allowlist** of published family assets rather
   than re-enabling the whole directory. Add APK-content positive and negative QA.
3. Implement actual verified family Atlas/Acceptance routes, and only separately
   source/safety-authorized diagnostic graphs. Do not promote research candidates.
4. Stage 11 Sherpa-ONNX license/packaging/integration remains a separate open TODO.

**Next run: continue Stage 13** with source/profile-specific published vertical slices
and full tests. If no authoritative source can be established, retain fail-closed
and record the exact blocker rather than marking the stage complete.
