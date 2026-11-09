# Stage 1/15: evidence-gated source-link triage (2026-11-09)

**Status: IN_PROGRESS.** This triage narrows the source-authority workload; it **does not resolve** any unsafe link, certify a source, publish content or close Stage 1. Donor is read-only `Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Target is Beta branch `audit/information-block-gaps-20261014`.

## Concrete findings from pinned source audits

- CHME3/CHME3T/CHME3E: **610 unresolved source/variant/target triples** are concentrated in **19 distinct target IDs**. Of these, **18 IDs have no source-object mapping in the pinned catalog/diagnostic mapping**. The 19th, `CHME3T-EQ-EDB-CONTROL`, has a catalog mapping for **CHME3T only**, but unresolved references also occur under **CHME3** and **CHME3E**. This is an **unverified cross-variant applicability** case, not evidence that the other variants are compatible. A separate scheme ID `CHME3T-SCH-EDB` also appears across all three variants without a pinned source mapping; it remains blocked. **Both** CHME3T-prefixed IDs are explicitly flagged for unverified cross-variant applicability, including when the target has no mapping at all.
- Ermak: **57 distinct unresolved source IDs**, of which **55 SOURCE_GAP IDs account for 542 occurrences**, and **2 AMBIGUOUS_SOURCE_ID values account for 6 occurrences**. `ER-SRC-039` and `ER-SRC-041` are known collisions. Reused raw numbers are not sufficient evidence to choose one publication. The separate `ER-DIAG-136` index gap is still blocked by the original quarantine validator.
- Legacy history: repository code search in `DomEnota-hub/Test-` and `DomEnota-hub/Beta` finds **references** to `HistoryRepository` in `BrakeCalculatorApp.kt` but **no implementation** of that class. A commit-history query for the expected donor path returned no commits. The exact storage format remains unverified; do not infer it from similarly named classes in unrelated projects.

## New machine-checkable disposition

`docs/migration/stage1-source-link-triage.json` is a **non-runtime** evidence ledger with one entry for each of the 19 CHME3 target IDs and 57 Ermak source IDs. Each entry includes reference/occurrence count, variant or registry-key context, explicit quarantine state, runtimeImport=false and the evidence required to revisit the disposition. CHME3 variant applicability must be checked independently for each variant.

`qa/validate_stage1_source_link_triage.py` compares **every ledger entry** against the existing pinned source-audit JSONs, rejects missing/duplicated IDs, count drift, fabricated mappings, silent variant changes, unreviewed publication and incorrect evidence requirements. Its regression suite `qa/test_stage1_source_link_triage.py` has **12 tests**; CI `.github/workflows/stage1-source-link-triage.yml` also runs the existing quarantine gate.

**Important:** 610 unresolved triples have **not** been fixed; 542 + 6 Ermak occurrences have **not** acquired authority. The ledger is a precise, enforceable work queue. It cannot itself serve as a source citation or authorize a diagnostic action.

## Next evidence-backed work

1. Locate original manufacturer scheme/equipment documents for the 19 CHME3 targets, verify series and modification applicability, then resolve *individual* triples only with document locator and test evidence. Prioritize `CHME3T-EQ-EDB-CONTROL` and `CHME3T-SCH-EDB` cross-variant risks.
2. Recover the original numbered Ermak source registry or verified publications for the 55 missing IDs; for `ER-SRC-039` and `ER-SRC-041`, preserve distinct publication identities until disambiguated with primary evidence. Verify `ER-DIAG-136` separately.
3. Obtain authoritative history storage implementation/schema before changing `HistoryStorageMigrationGate.legacyFormatVerified`; do not borrow the unrelated MediaLoader history schema.
4. Keep 329 exam questions as a verified, **not published** source corpus until a safe candidate target and licensing/source authority are established. Preserve encrypted plaintext boundaries.
5. Run and confirm terminal CI on the current HEAD before reporting this checkpoint as verified. Stage 2 begins only after Stage 1's evidence gates are satisfied.

No Android UI, calculator, assistant, runtime index or user-visible content was modified in this work.
