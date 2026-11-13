# RailBrake Beta — group 2/8, third pass: executable diagnostic authority gate

Date: 2026-11-11. **Status: IN_PROGRESS / DEVICE_QA_PENDING**. Donor Test- @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` READ-ONLY. Main stages: **11/15**; epic #4 remains open.

## Actual Kotlin change, not a publication claim

Code SHA: [`b429bb5104f2d7443aa11d5a031d5c452e88c799`](https://github.com/DomEnota-hub/Beta/commit/b429bb5104f2d7443aa11d5a031d5c452e88c799).

Files:
- `feature-diagnostics/src/main/kotlin/ru/railbrake/calculator/diagnostics/PublishedDiagnosticCatalog.kt`
- `feature-diagnostics/src/main/kotlin/ru/railbrake/calculator/diagnostics/DiagnosticReferenceCatalog.kt`
- `feature-diagnostics/src/test/kotlin/ru/railbrake/calculator/diagnostics/ExecutableDiagnosticFlowTest.kt`

**Defect fixed:** `PublishedDiagnosticCatalog` previously treated `ContentRegistry.resolve(...)=Found` (ACTIVE + layer + registry applicability) as sufficient to expose a full executable donor graph. It did **not** independently enforce source edition, provenance, action disposition, exact runtime variant or crew/equipment evidence. An ACTIVE informational/archival record could therefore become an interactive questionnaire in a future content update.

Now an executable graph additionally requires: STANDARD layer, CONDITIONAL_ACTION, CURRENT source, CURRENT_OFFICIAL/MANUFACTURER provenance, non-empty source references, runtime model and explicit scenario variant matching, and **per-scenario** `DiagnosticActionInputs` with independently verified source, profile and installed equipment. Missing evidence defaults to **no executable graphs**, not to implied permission. MainActivity deliberately supplies no fabricated evidence. The separate `DiagnosticReferenceCatalog` also allows ACTIVE + INFORMATION_ONLY entries to remain **readable as non-executable reference**, instead of disappearing merely because they are ACTIVE. Candidate warning and stop evidence remains visible only as unverified donor knowledge.

Unit regressions cover explicit positive synthetic evidence, missing evidence, wrong action disposition, source status, provenance, source refs, variant, profile and installed equipment; restricted layers remain non-executable. A synthetic positive test is **not** a newly approved real scenario. Existing 44 VL80S STANDARD/CANDIDATE reference descriptions, 138 donor cautions and 133 donor stop signals remain separate from execution.

**User-visible scope:** no new source-approved real crew graph, no new crew action, no new family diagnostic asset; this change closes a real execution-permission bypass and enables read-only presentation of eligible ACTIVE informational records. Count of newly published real executable scenarios: **0**. Count of newly approved crew actions: **0**. Do not confuse test fixture with normative approval.

## Verified CI and APK

Code SHA `b429bb51`: **19/19 GitHub Actions workflow runs terminal SUCCESS**, including:
- [Group 2 diagnostic reference + crew safety #43070317410](https://github.com/DomEnota-hub/Beta/actions/runs/43070317410)
- [Stage 15 integration QA #43070317417](https://github.com/DomEnota-hub/Beta/actions/runs/43070317417)
- [Modular bootstrap/Stage 51 #43070333348](https://github.com/DomEnota-hub/Beta/actions/runs/43070333348)

JUnit, lint, assembleDebug, AndroidTest **compilation only**, pinned donor parity, APK checks and negative fixtures passed. No AndroidTest execution on a phone. APK archives ZIP integrity PASS.

Both unique Debug/QA APKs version `1.2.2-modular-alpha01` were uploaded to Google Drive `Rail` (folder `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`), Drive metadata/parent/size checked and re-downloaded byte-for-byte with matching SHA256:

1. [Stage 15 APK](https://drive.google.com/file/d/1dvhS7WrJ2rQ7tRXfG6ERweP_iNWC7Ykf/view): `RailBrake_Beta_1.2.2-modular-alpha01_group2-third-pass_stage15_b429bb51_debugQA.apk`, **9,663,477 bytes**, SHA256 `46a91c56092d2165800dd1e99f9c0cc19e3832ebba8dc05d07e516ecccbc97d9`; artifact `13876879012`.
2. [Stage 51 APK](https://drive.google.com/file/d/1d59Euz7Z5mcQasFVO1wGkARax6_yUR2T/view): `RailBrake_Beta_1.2.2-modular-alpha01_group2-third-pass_stage51_b429bb51_debugQA.apk`, **9,663,517 bytes**, SHA256 `f98c89c40fb80d4f808f8d82ae3c433259926845e655d434e68e2c5f84cb01ab`; artifact `13877587581`.

Both under 100 MB, no split ZIP needed. No production release.

## Named blockers and exact resume

- **SOURCE_BLOCKED:** `vl80s.diag.pantograph-no-rise` and other donor candidates still require source-edition-specific crew-role, equipment, contraindication and stop-condition verification before the per-scenario authorization map can be populated. Donor text alone is not current normative clearance. Owner: content/source integration; unblock on exact authoritative source + variant/role matrix + full YES/NO/UNKNOWN graph and negative tests.
- **IN_PROGRESS:** 59/103 VL80S runtime scenarios not in current 44 STANDARD/CANDIDATE registry intersection; family Ermak/CHME3/TEM2 graph/rights/profile parity missing. No mass promotion or extended-mode bypass.
- **DEVICE_QA_PENDING:** real-device lifecycle, interactive graph, UI, offline, permission and signed-upgrade acceptance at final QA.

**Next hourly group:** 3/8 common materials and first aid. Do not repeat group 2 CI or source research without new evidence. Return to unresolved group 2 on the next queue pass. Full parked permissions audit remains PARKED. The automation source chat cannot be confirmed as writable; Issue #4 and this checkpoint are the durable records.
