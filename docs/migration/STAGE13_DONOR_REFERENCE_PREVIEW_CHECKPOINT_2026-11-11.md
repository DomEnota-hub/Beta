# Stage 13/15 — non-actionable donor reference previews (11.11.2026)

**Status: PARTIAL. Main stages fully completed: 11/15 (1–10, 12).** Stage 11 Sherpa-ONNX is a separate unfinished TODO. Stage 13 remains unfinished; Stage 14 was **not** started in this run.

## User-facing change

Seven small, source-traceable **reference summaries** from the pinned Test- donor now appear under **Atlas** after an explicit registered execution is selected, even though the migrated full family packs are still in quarantine. This corrects a small, concrete portion of the blanket-visibility regression without giving an unreviewed action any executable status.

- The summaries are **titles and descriptions only**. They contain no checklists, repair steps, links, diagnostic graphs or automatic action permission.
- Each card is explicitly labelled **«Справочные описания из Test- · НЕ инструкция к действию»**. The UI says normative currency and permission to perform work are **not confirmed**.
- For generic Ermak data and CHME3T without a verified before/after №6245 split, the UI explicitly states **applicability to the selected execution is NOT confirmed**. The user must still select an execution; unknown/cross-model execution fails closed.
- These summaries are limited to **Atlas**. Acceptance and Diagnostics do not display them as executable checklists or flows. Existing published VL80S data, source/profile gates and safety restrictions remain unchanged.
- The full family directories `electric/ermak`, `diesel/chme3-family`, `diesel/tem2-family` remain excluded from the APK, but **one separate curated summary asset** `assets/crew-reference/summaries.json` is included and checked in the built APK. The full exclusion is still a known **migration regression to resolve**, not a final design.

## Pinned donor → target object crosswalk (all seven are reference-only)

| Working model | Donor object | Donor file Git blob | Target pack | Scope |
|---|---|---|---|---|
| 2ЭС5К | `ER-KB-SYS-10` | `08d164fc` | `electric/ermak/technical-data/knowledge/knowledge-01.pack.json` | General Ermak; execution unverified |
| 3ЭС5К | `ER-KB-SYS-10` | `08d164fc` | same | General Ermak; execution unverified |
| ЧМЭ3 | `CHME3-CHME3-ACC-AUX-GENERATOR` | `fa63f0ca` | `diesel/chme3-family/technical-data/catalog/catalog-01.pack.json` | Donor variant `chme3` |
| ЧМЭ3Т | `CHME3T-CHME3-ACC-COUPLER` | `3682ce0b` | `diesel/chme3-family/technical-data/catalog/catalog-30.pack.json` | Pre/from №6245 split unverified |
| ЧМЭ3Э | `CHME3E-CHME3-ACC-INJECTOR` | `095e3230` | `diesel/chme3-family/technical-data/catalog/catalog-20.pack.json` | Donor variant `chme3e` |
| ТЭМ2 | `TEM2-EQ-OIL-SEP` | `c7a94c1c` | `diesel/tem2-family/technical-data/catalog/catalog-07.pack.json` | Donor variant `tem2` |
| ТЭМ2У | `TEM2-EQ-OIL-SEP` | `766ac526` | same | Donor variant `tem2u` |

Donor reference: `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`. All six unique donor blob SHAs were compared against the pinned donor Git tree, and the seven titles, summaries, object IDs, source paths and blob SHAs were compared against the Beta migrated packs. This is **donor-object provenance**, **not** independent confirmation that a particular manufacturer instruction is currently in force.

## Actual code, packaging and automated checks

- Code SHA: [`bf41af7ee3ce56cdc45b2532d09c95399e15c0c1`](https://github.com/DomEnota-hub/Beta/commit/bf41af7ee3ce56cdc45b2532d09c95399e15c0c1).
- New `FamilyReferencePreview.kt`: typed `DONOR_VARIANT` / `EXECUTION_UNVERIFIED` policy; rejects missing/foreign/unknown execution, non-Atlas route, malformed provenance; loads curated JSON, not family candidate packs.
- Updated `FamilyContentScreen.kt`: cancellable IO loading of small preview JSON after explicit selection, separate from family catalog loading; informational display only.
- New `FamilyReferencePreviewPolicyTest.kt`: three unit tests for exact/foreign/missing execution, cross-model, diagnostics/acceptance exclusions and unverified family scope.
- New `qa/validate_family_reference_preview.py`: **7/7** records checked against pinned donor SHAs and target pack fields; rejects procedural fields and unreviewed promotion.
- Updated `qa/check_stage13_apk_quarantine.py`: requires the curated asset in the actual built APK while still rejecting full unreviewed family directories and research candidates.
- Updated `.github/workflows/stage13-family-gates.yml`: checks reference asset, source-object parity, Android tests/lint/APK, family validators.

**CI terminal evidence on code SHA `bf41af7e`:** [Stage 13 family profiles and publication gates #42916434018](https://github.com/DomEnota-hub/Beta/actions/runs/42916434018) **SUCCESS**. Log contains `BUILD SUCCESSFUL in 4m 4s`, `STAGE13_APK_QUARANTINE_PASS app-shell-debug.apk assets=87`, `STAGE13_DONOR_SUMMARY_PARITY_PASS entries=7 models=7 executable=0`. All **25/25** workflow runs associated with this code SHA were **SUCCESS terminal**, including [Modular architecture bootstrap #42916710525](https://github.com/DomEnota-hub/Beta/actions/runs/42916710525). No phone QA; no production release. Donor Test- unchanged.

## What remains and what this does NOT claim

1. **Only seven reference summaries, not seven fully restored cards/feature routes.** No acceptance workflow, diagnostic action, interactive scheme or cross-link has been restored for these families. These previews cannot be counted as published, source-approved diagnostic content.
2. Most previously readable donor objects are still missing from the packaged family UI. The mass exclusion and overly narrow `FamilyPublicationGate` remain an acknowledged regression, **not a satisfactory endpoint**. Expand safe reference visibility by verified donor-object mapping and review the separate standard/extended display policy; never simply change all `CANDIDATE` to `ACTIVE`.
3. Unresolved provenance/variant/rights remain: Ermak 548 references, CHME3 610 references, `ER-DIAG-136`, CHME3T serial applicability, exam copyright and local/updated normative requirements.
4. Full normative audit of what locomotive crews may/should not do remains **FUTURE/PARKED** in `docs/backlog/FUTURE_PERFORMANCE_AND_CREW_ACCESS_AUDIT.md`, not activated by this work.
5. Device UI/instrumentation execution is reserved for final QA; build/CI alone does not prove all visuals and user journeys.

**Next exact Stage 13 action:** extend the machine-checkable donor-to-Beta reference crosswalk and safe **non-actionable** display for formerly accessible standard/extended knowledge; separately source-verify specific Atlas/Acceptance/Diagnostics routes and exact executions before granting any action status. If full external source validation blocks only this stage, preserve it as PARTIAL and advance to independent Stage 14 at the next scheduled run, keeping Stage 13 as an obligatory backlog item. Do not call Stage 13 complete or close Issue #4.
