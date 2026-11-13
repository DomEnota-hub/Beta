# Post-15 remediation, second pass group 2/8 — donor cautions and stop signals remain visible as knowledge

**11.11.2026. Status: PARTIAL / CODE + CI VERIFIED; DEBUG/QA APK DELIVERED AND RE-DOWNLOADED.** This is not completion of group 2, Stage 13, Stage 15 or Issue #4. Main migration stages fully accepted remain **11/15**. Test- donor pinned at `3176d6ee228f0ed4b78371f45209e10c1c724eff` was read-only. This run works only group 2.

## User-visible implementation in Beta

- `31ae8e018c6e8513b5c673ebaa94b3ec270bc2e7`: candidate-only STANDARD diagnostic reference preview now retains separate **observed signs**, **donor cautions**, and **donor stop signals**, instead of hiding the last two fields. They are *source-unverified donor evidence*, never a normative approval or executable crew procedure. Search can find a candidate by these reference-only phrases, but not by hidden immediate actions, question graph, unsafe checks, sourceNote, or other executable fields.
- `b03dc4fd591492f1654b07df6e3bd397698bcb9a`: real Compose reference card renders three clearly labelled blocks, with explicit edition/variant/role uncertainty, including an error-colored caution and stop section. Published/authorized diagnostic flow remains separate. The user can read contraindication-like information without the application falsely asserting its legal validity.
- `9a38c9f18199c5e73aa13e6a10e52256f2e8b88f`, `5e1bc7e2d26f69e728ce6ed0d6f2f3bb7edcf7d9`: JUnit positive and negative regression checks for text visibility, searchable cautions/stop signs, and continued non-exposure of actions/graph/danger/source claims.
- `817c008de29fb5daed05c10f3576482ac62442d2`: pinned-runtime parity check asserts no silent loss of the reference-only warning evidence.
- `ea6ae1306e6d77ac2fbb400a55b9612a2ac6c891`, `2912b8dcde3c98d088c27e9a86a4170558664e68`: Stage 15 now runs on diagnostic Kotlin changes and checks real APK integrity, SHA256, size and the diagnostic evidence parity before uploading the unapproved QA artifact.

## Measured scope and safety

The **44** previously eligible VL80S STANDARD/CANDIDATE diagnostic summaries are still the only read-only candidates. From the already packaged pinned donor-derived runtime, **32** of those 44 have **81 observable-sign lines**, and the 44 have **138 donor caution lines** and **133 donor stop-signal lines**. These were present in the donor-derived data but not shown by the previous read-only reference UI. **No new diagnostic candidates approved, no new crew action permitted, no execution graph exposed.** Actual normative prohibitions newly verified: **0**. Published scenario contraindications and stop conditions continue to be rendered separately by the existing approved-scenario route.

The Test- `DiagnosticRepository.kt` at the pinned commit was checked for the `prohibited`, `stopConditions`, `observableSigns` fields and the `pantograph-no-rise` entry. No donor files were edited. No full external permissions audit was started; `docs/backlog/FUTURE_PERFORMANCE_AND_CREW_ACCESS_AUDIT.md` remains PARKED.

## Verification and delivery

**CI verified terminal:** at final Kotlin/Compose/test SHA `5e1bc7e2d26f69e728ce6ed0d6f2f3bb7edcf7d9`, **17/17 workflows SUCCESS**, including dedicated [group 2 #42996404937](https://github.com/DomEnota-hub/Beta/actions/runs/42996404937): `:feature-diagnostics:testDebugUnitTest`, `:app-shell:testDebugUnitTest`, lint, `:app-shell:assembleDebug`, `:app-shell:assembleDebugAndroidTest` and the pinned runtime, evidence parity and actual APK integration gates. The job log reports `BUILD SUCCESSFUL in 3m 51s`, `POST15_GROUP2_REFERENCE_PARITY_PASS read_only_candidates=44 runtime_scenarios=103 registry_entries=44 observed_cards=32 observable_signs=81 donor_cautions=138 donor_stop_signals=133 executable_candidates=0` and `STAGE15_APK_INTEGRATION_PASS vl80s_core_packs=28 common_references=66 family_previews=84 forbidden_assets=0`.

At CI workflow update SHA `2912b8dcde3c98d088c27e9a86a4170558664e68`, **17/17 workflows SUCCESS terminal**, including [Stage 15 #42996643758](https://github.com/DomEnota-hub/Beta/actions/runs/42996643758) and [modular bootstrap #42996654538](https://github.com/DomEnota-hub/Beta/actions/runs/42996654538). Stage 15 ran JVM tests, lint, Debug APK, AndroidTest **compilation only**, negative integration fixtures, real APK/source/profile gates, and APK ZIP integrity. The final Stage 15 job reports `BUILD SUCCESSFUL in 3m 34s`.

**Verified unapproved Debug/QA APK delivered to Google Drive Rail** (folder `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`): [`RailBrake_Beta_1.2.2-modular-alpha01_post15-group2-second-pass_debugQA_2912b8dc.apk`](https://drive.google.com/file/d/1Uk35-a5ugjvIz3aZ8hyVG1PNuoBMJ0Nv/view), **9,653,013 bytes**, SHA256 **`2da49d56453273ed697ce2601928027f081ceff8fdc33645dad3a6f2887c03cf`**. GitHub artifact ID `13844895606` ZIP size 9,270,030 bytes and SHA256 `379b7c2b23a8b9cc57611a2d4b8d866c5973084a7b8d5386b761985ca307cda8`; ZIP and APK integrity PASS. Google Drive upload was independently verified with metadata for exact name, size, and parent folder, then **re-downloaded and SHA256-matched** against the CI original. Under 100 MB, delivered as one APK. **Not production; no device execution claimed.**

## Remaining group 2 acceptance

1. Confirm exact edition, applicability, crew role and conditions for the 138 donor caution and 133 stop-signal lines. **Displaying them with uncertainty is not legal/technical verification.** Check pantograph roof access and crew/depot boundary against authoritative source before approving procedures.
2. Restore legitimate reference visibility for remaining 59/103 VL80S runtime scenarios after status/layer/rights classification. Do not leak extended/restricted research content into STANDARD.
3. Restore family diagnostics and verified crew paths for Ermak, CHME3 and TEM2; full packs are still excluded from APK. Group 1 source/rights blockers remain.
4. Verify UI search, card navigation, variant notices, standard/extended consent, warnings, offline, lifecycle, and negative cases on the final QA device.
5. Do not close the overall issue or publish production. Continue the unresolved groups sequentially after this run; next scheduled position is group 3/8 second pass.

**Next immediate action:** on the next hourly position work group 3/8 second pass, source-backed common reference/first-aid visibility without authorizing unverified actions. Group 2 remains PARTIAL pending individual source/role/variant review and final manual device QA. Return to unresolved group 2 after this queue pass; do not start the parked full permissions audit.
