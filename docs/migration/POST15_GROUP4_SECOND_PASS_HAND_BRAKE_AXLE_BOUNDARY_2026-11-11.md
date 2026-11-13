# Post-15 group 4/8 — second pass: physically impossible manual-brake axle substitution

**Date:** 2026-11-11. **Status:** IN_PROGRESS, verified functional patch, not normative acceptance. **Main stages:** 11/15 fully verified in their previously scoped engineering acceptance. **Donor:** Test- @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` READ-ONLY. **Target:** Beta `audit/information-block-gaps-20261014`.

## Concrete user-facing change

**Code/test SHA:** [`785940abb7bf3bd2e7d05365ab6b83f791621023`](https://github.com/DomEnota-hub/Beta/commit/785940abb7bf3bd2e7d05365ab6b83f791621023).

- `feature-calculations/.../BrakeCalculator.kt`: mass-based hand-brake substitution now rejects a calculation that would claim more actually braked axles than the known total axles of the train; also rejects invalid direct-call total axle counts. Appendix №12 substitution now enforces the same physical upper bound. This does not modify coefficients or authorize securing.
- `app-shell/.../SecuringScreen.kt`: when mass mode is entered with axle load but **without an axle count**, a visible warning explicitly says physical feasibility of the proposed hand-brake substitution cannot be verified until the actual axle count is known. The existing arithmetic preview remains labelled unapproved.
- `BrakeCalculatorSafetyBoundaryTest.kt`: new positive/negative JUnit test exercises an impossible two-axle substitute (4 braked axles claimed) and feasible variants in both modes.
- `SecuringInputReviewTest.kt`: new UI-input-to-engine regression verifies both impossible drafts return `SecuringReview.Invalid` with an explicit reason, rather than a plausible preliminary quantity.

**Newly approved operational calculations/actions:** 0. **Newly blocked physically impossible input cases:** 2 calculation modes. Existing independent mode drafts and VU-45 arithmetic-only verification unchanged. No blanket hiding of reference knowledge; no action/safety gate weakened.

## Verified checks

At **code SHA `785940ab`**: **30/30 GitHub Actions workflows terminal SUCCESS**, including:
- [Stage 4 calculations parity and safety #43013658417](https://github.com/DomEnota-hub/Beta/actions/runs/43013658417): calculation JUnit, lintDebug, assembleDebug.
- [Stage 15 cross-feature integration QA #43013658467](https://github.com/DomEnota-hub/Beta/actions/runs/43013658467): JVM/integration/negative checks, AndroidTest compilation, lint, APK integrity and content gate; `STAGE15_APK_INTEGRATION_PASS vl80s_core_packs=28 common_references=66 family_previews=84 forbidden_assets=0`.
- [Modular architecture bootstrap #43013665639](https://github.com/DomEnota-hub/Beta/actions/runs/43013665639): unit/contract tests, Android lint/assemble, Stage 50/51 research and source/profile/action negative gates, terminal SUCCESS.

**No instrumentation executed on a real phone.** The two new regression methods are included in the green Stage 4 JUnit suite.

## QA delivery: both unique APKs, Google Drive Rail

Destination: [Google Drive Rail](https://drive.google.com/drive/folders/1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd). Both are **Debug/QA only, version 1.2.2-modular-alpha01**, not production. Both original GitHub artifact ZIPs and extracted APKs passed ZIP integrity tests; Google Drive parent/name/size were verified and re-downloaded APK SHA256 matched the CI evidence.

1. [Stage 15 APK](https://drive.google.com/file/d/13eLE6Yn3QPLWnp-dtlRsttwpqWuKgABF/view): `RailBrake_Beta_1.2.2-modular-alpha01_post15-group4-second-pass_stage15_785940ab.apk`; **9,657,121 bytes**; SHA256 `e38d3fe1e8b1d378a1f571d841ac68a0cf00477d9c3bbbd54000f5cdc95d09fd`; GitHub artifact `13851433262`.
2. [Stage 51 APK](https://drive.google.com/file/d/1PyQE5GZoxl-u2rbCR6Hrx5gZLlafz_fy/view): `RailBrake_Beta_1.2.2-modular-alpha01_post15-group4-second-pass_stage51_785940ab.apk`; **9,657,033 bytes**; SHA256 `266a19761156d00e53a95410bbe935cbb0612b16337030c71e5f43b88cfdb0ff`; GitHub artifact `13852061069`.

## Still open

1. BY_MASS donor coefficient table remains `DONOR_PARITY_ONLY`: current primary source, conditions and applicability are not confirmed. Owner: calculation-source-review; criterion: precise current source + matching table and variants + tests.
2. Appendix №12 still `FORMULA_REVIEWED_LOCAL_RULES_REQUIRED`: local TРА/owner-specific applicability, composition, profile and placement conditions unverified. Owner: infrastructure-normative-review; criterion: local rules and source-backed real examples.
3. VU-45 remains `ARITHMETICALLY_CONSISTENT_NOT_APPROVED`: verify fields/edition/force/density/tail against rules effective 01.07.2026, no automatic permission. Owner: brake-normative-review.
4. Physical device QA (draft switching, accessibility, history persistence, input errors, offline) deferred to final manual acceptance. Owner: Android-QA.
5. Mass-mode preview without axle count is still a **reference-only** quantity with an explicit feasibility warning, not an operational securing recommendation.

**Next scheduled position:** group **5/8**, history and data migration. Inspect existing legacy history/diagnostic archive storage for silent data loss or profile bleed; add a concrete Kotlin fix plus positive/negative regression tests. Return to unresolved group 4 only on subsequent pass. Do not close Issue #4 or start the parked full permissions audit.
