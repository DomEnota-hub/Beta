# Stage 14/15 — common knowledge and safety reference UI (11.11.2026)

**Status: PARTIAL. Fully closed stages remain 11/15 (1–10 and 12).** Stage 11 Sherpa-ONNX and Stage 13 family routes remain unfinished. Stage 15 was NOT started in this run. Donor Test- is read-only at `3176d6ee228f0ed4b78371f45209e10c1c724eff`.

## Concrete Kotlin/Compose change

The four common destinations in the shell no longer lead to the generic unavailable screen:

| Destination | Reference entries | Source pack |
|---|---:|---|
| База знаний | 13 | `common/knowledge/articles.pack.json` |
| Безопасность движения | 13 | `common/knowledge/articles.pack.json` (`signals-` / `movement-`) |
| Охрана труда | 22 | `common/safety/articles.pack.json` |
| Первая помощь | 18 | `common/first-aid/topics.pack.json` |
| **Total** | **66** | 3 packs; 21 source entries are retained for provenance, not displayed as article cards |

- New `feature-safety/CommonReferenceCatalog.kt` reads the three original pinned common packs (87 total objects) on demand, verifies pack identities, COMMON ownership, candidate state, manifest membership, global links and absence of model/variant claims. No copy or bulk `ACTIVE` promotion is made.
- New `feature-safety/CommonReferenceScreen.kt` loads and validates data in `Dispatchers.IO`, handles loading/error/back navigation, lists article summaries, and opens a reference detail with source titles and explicit warnings about unverified source currency and lack of permission to act.
- The first-aid pack contains unreviewed step-by-step donor blocks. **Those procedural blocks are NOT projected into the reference UI**; the first-aid section currently shows titles and summaries only, plus emergency call guidance. Other common reference cards show summary and non-block `details` as explicitly unverified donor text; no links or procedures are promoted to executable flows.
- `MainActivity` now routes `KNOWLEDGE`, `TRAFFIC_SAFETY`, `OCCUPATIONAL_SAFETY`, `FIRST_AID` to the new screen regardless of the working model's published family runtime. It still requires the user's existing explicit working-model selection at app entry, but does not require an execution for these common sections.
- `ContentRegistry.resolve()` publication gate and all family/diagnostic safety gates remain unchanged. `CANDIDATE` material is readable only through this **reference projection**, not through action/diagnostic/acceptance runtime. The full future normative crew-access audit remains parked.

## Tests and CI evidence

**Code HEAD:** `78a4b45a0d8270135355e5c65f4089818c4828c2`.

- Three new `CommonReferencePolicyTest` JVM tests: exact partition 13+13+22+18; first-aid blocks never projected; reject `ACTIVE`, `CONDITIONAL_ACTION`, `PROHIBITED`, foreign owner, `EXTENDED`, missing/unknown source refs and unrelated destinations.
- `qa/check_stage14_common_reference.py` checks the **actual built APK** includes all three packs, exactly 66 reference articles, preserved CANDIDATE status, provenance links and absence of first-aid procedure rendering.
- Dedicated workflow `.github/workflows/stage14-common-reference.yml` runs `:feature-safety:testDebugUnitTest :app-shell:testDebugUnitTest :app-shell:lintDebug :app-shell:assembleDebug`, APK inspection, pinned first-aid and knowledge validators.
- First CI attempt [#42925344204](https://github.com/DomEnota-hub/Beta/actions/runs/42925344204) FAILED due to Android unit-test source using unavailable `Files.readString`; corrected to `Files.readAllBytes(...).toString(Charsets.UTF_8)` in `78a4b45a`.
- **Final CI [#42925669562](https://github.com/DomEnota-hub/Beta/actions/runs/42925669562): SUCCESS (terminal)**, all job steps successful. Log: `BUILD SUCCESSFUL in 3m 33s`; `STAGE14_COMMON_REFERENCE_PASS articles=66 firstAid=18 traffic=13 knowledge=13 occupational=22 executable=0`. Android lint and debug APK build succeeded. Device UI/instrumentation execution is reserved for final manual QA.

## Limitations and required follow-up

1. **Stage 14 is NOT complete**: this is reference availability, not approved current normative procedures, first-aid algorithms, or all donor knowledge navigation and cross-links. Candidate source status remains UNKNOWN; source-by-source review is still needed before publishing any crew action.
2. The common packs contain 21 source entries whose current editions have not been independently verified in this run. They are visible as source titles for context, not treated as valid authorization. Existing content may include dated normative references; user must not mistake the reference projection for an operational instruction.
3. Stage 13 blanket exclusion of Ermak/CHME3/TEM2 family packs remains a separate known regression; seven family summaries from the previous run do not equal complete family routes. Stage 11 Sherpa-ONNX remains a separate mandatory TODO.
4. No Test- edits, no mass `ACTIVE`, no bypass of role/profile/safety gates, no APK production release. Full normative audit `docs/backlog/FUTURE_PERFORMANCE_AND_CREW_ACCESS_AUDIT.md` stays **FUTURE/PARKED**.

**Next concrete action (next independent Stage 15 cycle):** perform end-to-end integration QA of shell/common/reference/family paths and actual APK contents, add negative UI/navigation tests and inspect for missing user journeys; keep Stage 11/13/14 unresolved items explicitly in the post-15 backlog, and do not claim final migration complete. If stage 14 receives additional verified sources before Stage 15, restore only the specific validated action cards with full conditions/contraindications; never auto-promote candidates.
