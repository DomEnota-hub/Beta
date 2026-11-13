# RailBrakeCalculator — post-15 remediation group 1: donor family reference recovery (11.11.2026)

**Status: PARTIAL.** This is a verified functional Kotlin/Compose change, **not** completion of group 1, Stage 13, or the full migration. Full main-stage completion remains **11/15** (stages 1–10, 12). The full crew-permissions normative audit remains **FUTURE/PARKED**.

## Scope and commits

- Working Beta branch: `audit/information-block-gaps-20261014`.
- **Code and test commit:** [`73abd57bc558b19fed62e50ffb7ceb04e665008f`](https://github.com/DomEnota-hub/Beta/commit/73abd57bc558b19fed62e50ffb7ceb04e665008f).
- Immutable read-only Test- donor: `3176d6ee228f0ed4b78371f45209e10c1c724eff`.
- This run worked **only post-15 group 1**. No change to calculation publication, safety gates, diagnostics, source status, model profile IDs, or full-family APK exclusions.

## Concrete user-facing changes

1. Expanded the **curated, non-actionable** Atlas knowledge bridge from **7 to 84** source-traceable equipment/system descriptions: **12 per model** for 2ЭС5К, 3ЭС5К, ЧМЭ3, ЧМЭ3Т, ЧМЭ3Э, ТЭМ2 and ТЭМ2У. **77 new** summary-only references. The seven previous entries remain.
2. Every record includes donor path, donor Git blob SHA, original donor object ID, migrated target pack and target object ID. Six distinct donor blob SHAs were independently checked against the pinned Test- Git tree; each of the 84 records was cross-checked in CI against the migrated target object fields and provenance. **This is source lineage, not independent normative/current-edition approval.**
3. Added a searchable Atlas list scoped **first** by exact working model, explicit execution and Atlas destination. Search matches title and description, not an unrelated locomotive. Added an individual **read-only description screen** with explicit provenance and execution uncertainty, plus a back route.
4. 2ЭС5К/3ЭС5К entries remain `EXECUTION_UNVERIFIED` for МСУД-Н vs МСУД-015. ЧМЭ3Т remains `EXECUTION_UNVERIFIED` for pre/from №6245. ЧМЭ3, ЧМЭ3Э, ТЭМ2, ТЭМ2У are marked `DONOR_VARIANT` only when the exact donor variant matches; **this does not establish normative permission**.
5. Parser now rejects unknown JSON fields, duplicate reference IDs and wrong pinned donor commit. The UI does not expose internal IDs, executable steps, depot repair instructions, checklists or diagnostic graphs.
6. Curated asset remains separate from the unreviewed full family directories. No blind `ACTIVE` promotion and no relaxation of `FamilyPublicationGate`.

## CI and automated tests: terminal

**All 27/27 GitHub Actions workflow runs on code SHA `73abd57b` finished `SUCCESS` (terminal).** Relevant independent gates:

- [Stage 13 family profiles and publication gates #42940530437](https://github.com/DomEnota-hub/Beta/actions/runs/42940530437): `:app-shell:testDebugUnitTest`, Android lint, Debug APK, family-source validators, actual APK quarantine and 84-item donor-object parity — **SUCCESS**.
- [Stage 15 cross-feature integration QA #42940530487](https://github.com/DomEnota-hub/Beta/actions/runs/42940530487): Android/JVM tests, lint, AndroidTest **compilation**, actual APK audit, negative fixture tests, Debug QA artifact — **SUCCESS**.
- [Modular architecture bootstrap #42940537106](https://github.com/DomEnota-hub/Beta/actions/runs/42940537106): source/profile/runtime boundaries, packaged-family quarantine and additional independent checks — **SUCCESS**.
- Added a Kotlin unit test that search cannot leak another model, execution or non-Atlas route.
- Added two Python negative tests for duplicate preview IDs and incorrect per-model distribution. The pinned reference validator now requires exactly 12 entries per model and matching donor/target provenance.

**Limitations:** CI compiled Android instrumentation tests, but no physical-device/emulator execution was performed. No production release. No independent legal/normative approval of the 84 technical descriptions.

## Unresolved group 1 backlog (explicitly not completed)

- Full Ermak/CHME3/TEM2 family catalogs are still excluded from APK by `ignoreAssetsPattern`; the 84 curated descriptions do **not** restore complete donor knowledge or feature parity.
- No restored family acceptance workflows, interactive schemes, source-backed diagnostic graphs or executable crew actions.
- Source and variant review remains open: 548 Ermak references, 610 CHME3 links, CHME3T №6245 boundary, ER-DIAG-136, version/current-edition confirmation and lawful source use.
- Standard/extended modes are not yet functionally equivalent to Test-. The 84 summaries are Atlas-only; global assistant search does not index them. These remain required parts of group 1.
- Do not use a mass `ACTIVE` flag, unsafe gate bypass or unreviewed family pack inclusion as a shortcut. Keep information readable where verified safe to present, separate from permission to perform work.

## Next action and sequencing

**At the next hourly run: post-15 group 2**, diagnostic flows, locomotive-crew contraindications and source/role/condition separation, **without launching the separately parked full permissions audit**. Keep group 1 `PARTIAL` and return to its open subitems after the first 7+1 remediation pass. Do not report the overall migration complete.

**Manual device testing remains reserved for final acceptance. Test- was not changed.**
