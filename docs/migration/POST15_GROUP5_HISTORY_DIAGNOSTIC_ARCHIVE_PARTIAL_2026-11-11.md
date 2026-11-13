# RailBrakeCalculator — post-15 remediation group 5/8: local history, notes, legacy diagnostic archive

**11.11.2026. Status: PARTIAL / verified implementation, not a signed installed-app upgrade.**
Only group 5 was worked on. Main stages fully complete remain **11/15 (1–10, 12)**. Groups 1–4 remain PARTIAL; Issue #4 remains open. Pinned donor Test- `3176d6ee228f0ed4b78371f45209e10c1c724eff` was read-only. Beta branch `audit/information-block-gaps-20261014`.

## Concrete user-visible Kotlin/Compose implementation

- Added a third read-only **«Архив диагностики»** tab to **«История и рабочие записи»**. It reads the pinned donor `SharedPreferences("diagnostic_sessions")/records` StringSet without writing or deleting the original. Displays timestamp, scenario title, exact profile, recorded variant, original severity and report with an explicit warning that historical text is **not** an authorized crew procedure.
- Archive records are visible **only for exact selected model ID**. No automatic `ermak` → `2es5k`/`3es5k` mapping, no cross-model leakage, no assumption about МСУД-Н/015. This deliberately leaves some family archives inaccessible until an independently verified profile crosswalk exists.
- New pure `LegacyDiagnosticSessionCodec` decodes the **seven Base64 URL_SAFE/NO_WRAP UTF-8 fields** of pinned donor `DiagnosticSessionRepository.kt` (Git blob `cc63f7a7abf17b4498ba3644b095be1127ef4df2`), rejects malformed records and invalid UTF-8, reports corruption, preserves distinct same-timestamp records, and never treats archived text as runtime instructions.
- Hardened `HistoryCodec.decodeV2`: reject over-capacity or duplicate v2 storage **instead of silently truncating on the next write**. Normal user-facing 30-record cap and existing donor-compatible history behavior are unchanged.
- Hardened `AndroidHistoryStore` against a present-but-invalid legacy preference type, and `AndroidWorkNotesStore` against null/corrupt note storage being treated as an empty archive. Added note field/timestamp validation before writing and after reading. Existing local user records are never copied into the repository.
- Added read-only archive navigation instrumentation assertions (compiled for device, not executed).

**Code SHA:** [`b6034308fab60a024012025a54b5b188a75359a9`](https://github.com/DomEnota-hub/Beta/commit/b6034308fab60a024012025a54b5b188a75359a9). **Instrumentation-test SHA:** [`09264ca88823333066f7edb83d17d3322a30cb9c`](https://github.com/DomEnota-hub/Beta/commit/09264ca88823333066f7edb83d17d3322a30cb9c).

## Test evidence

- **Seven new JUnit cases:** five donor diagnostic archive codec tests (Russian text/pipe, malformed records, strict profile isolation, same-timestamp retention, bad timestamp/UTF-8); two history/notes integrity cases (over-capacity/duplicate v2, invalid note rejection).
- Stage 7 [CI on implementation SHA #42967166917](https://github.com/DomEnota-hub/Beta/actions/runs/42967166917) **SUCCESS terminal**: `:feature-history:test`, `:app-shell:assembleDebugAndroidTest`, `:app-shell:lintDebug`, `:app-shell:assembleDebug`.
- Stage 7 [CI on final code/test SHA #42967204683](https://github.com/DomEnota-hub/Beta/actions/runs/42967204683) **SUCCESS terminal**. Stage 15 [cross-feature QA #42967204519](https://github.com/DomEnota-hub/Beta/actions/runs/42967204519) **SUCCESS terminal**.
- First code SHA: **29/29 workflow runs SUCCESS terminal**. Final test SHA's full workflow sweep was still finishing when this document was created; record terminal totals separately in Issue #4, do not infer success from queued jobs.
- Android instrumentation **compiled but not executed** on a phone. No signed QA upgrade and no production release.

## Still open: mandatory acceptance and owners

1. **Signed in-place Test- → Beta upgrade**, preserving app identity, signing key, original SharedPreferences and real user history. **Owner:** release/Android QA. **Done when:** backup-safe upgrade on a dedicated test device with representative donor records; compare raw legacy records and v2 output, uninstall prohibited during migration test; verify rollback/corruption recovery. Signing provenance and matching key are not established here.
2. **Diagnostic archive mapping for Ermak/CHME3/TEM2**. **Owner:** storage + family-profile review. **Done when:** verified donor profile/variant → exact model/serial mapping and negative tests; do not guess an execution profile from a legacy journal ID.
3. **Acceptance states and sessions**, `technical_acceptance_states`, including legacy `BLOCKING` → `NOTE`, item ID applicability and save-parameters behavior. **Owner:** acceptance migration. **Done when:** per-item source IDs and family route are verified, no cross-family state transfer, device rollback tests.
4. **Recent materials and knowledge display**, `technical_recent_materials` and `knowledge_display_v2`, including independent emergency-mode opt-in. **Owner:** shell/content migration. **Done when:** stable target IDs resolve, unresolved IDs remain visible as historical references without fabricated routes; appearance preference migration separately checked.
5. **Data integrity/recovery and model-scoped work notes.** **Owner:** history + Android QA. **Done when:** device tests cover corrupted types, malformed/duplicate entries, rollback, app restart, model switching, storage-full write failure and deletion; settle the older «Рабочий» profile local-storage policy before production.
6. **User-device QA** remains final manual acceptance. No source verification for crew action permissions was started here; the future full permissions audit stays PARKED.

## Next action

At the next hourly run, begin **post-15 group 6/8**, text assistant corpus, source-backed search, cross-family links and false-positive regression. Return to group 5 after first 7+1 pass. Do not mark Stage 11/13/14/15 complete, do not close Issue #4, do not change Test-, and do not equate readable historical data with permission to act.
