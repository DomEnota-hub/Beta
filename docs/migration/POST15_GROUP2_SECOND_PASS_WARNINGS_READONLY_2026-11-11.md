# Post-15 remediation, second pass group 2/8 — donor cautions and stop signals remain visible as knowledge

**11.11.2026. Status: PARTIAL / IMPLEMENTED; CI VERIFICATION IN PROGRESS.** This is not completion of group 2, Stage 13, Stage 15 or Issue #4. Main migration stages fully accepted remain **11/15**. Test- donor pinned at `3176d6ee228f0ed4b78371f45209e10c1c724eff` was read-only. This run works only group 2.

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

**At creation: CI pending.** Dedicated post-15 group 2 run at `5e1bc7e2`: [#42996404937](https://github.com/DomEnota-hub/Beta/actions/runs/42996404937); Stage 15 at `2912b8dc`: [#42996643758](https://github.com/DomEnota-hub/Beta/actions/runs/42996643758). Do not claim success, a validated APK or Google Drive delivery until terminal results and verified Drive metadata. Android instrumentation compilation is required; execution on a device is reserved for final manual acceptance.

## Remaining group 2 acceptance

1. Confirm exact edition, applicability, crew role and conditions for the 138 donor caution and 133 stop-signal lines. **Displaying them with uncertainty is not legal/technical verification.** Check pantograph roof access and crew/depot boundary against authoritative source before approving procedures.
2. Restore legitimate reference visibility for remaining 59/103 VL80S runtime scenarios after status/layer/rights classification. Do not leak extended/restricted research content into STANDARD.
3. Restore family diagnostics and verified crew paths for Ermak, CHME3 and TEM2; full packs are still excluded from APK. Group 1 source/rights blockers remain.
4. Verify UI search, card navigation, variant notices, standard/extended consent, warnings, offline, lifecycle, and negative cases on the final QA device.
5. Do not close the overall issue or publish production. Continue the unresolved groups sequentially after this run; next scheduled position is group 3/8 second pass.

**Next immediate action:** await terminal JUnit/lint/assembleDebug/AndroidTest compile and APK gate; fix failures; download and verify Stage 15 artifact; upload APK to Google Drive `Rail` (folder `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`) and verify metadata; update this checkpoint and Issue #4 with exact SHA, size, CI and delivery status.
