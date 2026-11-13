# RailBrakeCalculator — post-15 remediation group 4/8: calculations, VU-45 and securing

**11.11.2026 — PARTIAL / ACTUAL KOTLIN+COMPOSE CHANGES AND CI VERIFIED.** Group 4 is not closed. Completed main stages remain **11/15 (1–10 and 12)**. Donor Test- pinned at `3176d6ee228f0ed4b78371f45209e10c1c724eff` was not modified. Beta working branch: `audit/information-block-gaps-20261014`.

## Real implementation and user-visible effect

Code commits in order:
1. `585f1c97a35618484d6cffc20ebd406b531684d4` — `BrakeCalculator.kt`: fixed integer overflow in Appendix №12 wind-shoe calculation. Previously `axleCount * windCoefficient` multiplied two `Int` values **before** conversion to `Double`; for large valid integers this could wrap to a positive, much smaller number and silently undercount wind shoes. Multiplication now starts in `Double` and passes the existing checked ceiling and total/shortage overflow guards.
2. `50d53e258a6c11e1273b4cd3a27f08013e77e76a` — new direct engine regression tests: 1,500,000,000 axles at 16 and 22 m/s must yield 22,500,000 and 52,500,000 wind shoes respectively; invalid/contradictory mass, axle count and axle load must be rejected even when engine is invoked outside the Compose input validator.
3. `4e212b7650d46845763acc2ec0a5b6b83d4903c0` — input-review regression: the same high-axle wind result passes through `SecuringInputReview.byAppendix` while keeping `FORMULA_REVIEWED_LOCAL_RULES_REQUIRED`.
4. `eab3b56ce300c0627a355d0db6b1a1e26d95795a` — `SecuringScreen.kt`: users now see the **unrounded mass result**, its **unverified donor-table coefficient**, Appendix №12 **pre-rounding base**, **explicit formula/low-slope rule**, **wind coefficient per 200 axles**, and the named legal reference with a warning that local applicability remains unverified. No automatic action authorization was added.

The pure `calculateMass` entry point now rejects negative axle counts even if a manual axle load was supplied, and rejects mutually inconsistent mass/axle-count/manual-load triples. The UI validator already rejected such contradictory triples; this fixes the missing **engine-level** defense. Existing two separate securing forms, independent drafts, VU-45 arithmetic-only checking and history remain intact.

**No normative coefficients were invented or changed**, and no experimental diagnostic content was activated. The numerical stress cases prove overflow safety, not a claim that a billion-axle train is physically meaningful or that these outputs are operational instructions.

## Source-bound normative scope

- [Mintrans Order №250 / Appendix №12 to the train-operation instruction, clauses 8–20](https://sudact.ru/law/prikaz-mintransa-rossii-ot-23062022-n-250/pravila-tekhnicheskoi-ekspluatatsii-zheleznykh-dorog/prilozhenie-n-2/prilozhenie-n-12/): clause 8 has formulas 1/2, clause 9 requires local norms and local rules for automated calculations, clause 12 requires rounding up, clause 15 prescribes +3 shoes per 200 axles at wind **over 15 m/s** and +7 at **over 21 m/s** when aligned with possible movement. Clauses 1 and 20 limit leaving rolling stock without locomotive on slopes above 2.5‰. Current code preserves the requirement for separately verified local conditions.
- [Rules for brake equipment, Appendix №65 to Council Protocol №83 (25–26.11.2025)](https://base.garant.ru/413231681/850c9b8f5271cc2c815bc04e52704941/): in force since **01.07.2026**; VU-45 field/edition and train-specific normative checks remain an independent acceptance task. Their existence does **not** validate the donor mass table.
- The `BY_MASS` table remains `DONOR_PARITY_ONLY` because no verified current primary source for the coefficients/applicability was established. Appendix №12 remains `FORMULA_REVIEWED_LOCAL_RULES_REQUIRED`. `CalculationPublicationPolicy.canPublishOperationalResult` remains false for both. VU-45 still reports `ARITHMETICALLY_CONSISTENT_NOT_APPROVED`, not operational approval.

## Verified CI and tests

- `Stage 4 calculations parity and safety` on the changed calculation/test commits: [#42960530174](https://github.com/DomEnota-hub/Beta/actions/runs/42960530174), [#42960543432](https://github.com/DomEnota-hub/Beta/actions/runs/42960543432), [#42960555337](https://github.com/DomEnota-hub/Beta/actions/runs/42960555337): **SUCCESS (terminal)**, including `:feature-calculations:test`, `:app-shell:lintDebug`, `:app-shell:assembleDebug`.
- On final code commit `eab3b56c`, **29/29 workflow runs completed SUCCESS (terminal)**. This includes [Stage 15 cross-feature integration QA #42960567463](https://github.com/DomEnota-hub/Beta/actions/runs/42960567463) and [Modular architecture bootstrap #42960573513](https://github.com/DomEnota-hub/Beta/actions/runs/42960573513).
- Added **three JUnit regression tests**: two direct-engine safety tests and one end-to-end draft-review test. Existing donor-parity tests remain green.
- Android UI instrumentation was **not executed on a physical device**. No production release.

## Still open / acceptance criteria

1. **Mass table:** find an authoritative current primary source, verify the coefficient table and conditions against the specific application/owner. Until then: reference-only, no operational approval. Owner: calculation-source-review.
2. **Appendix №12:** confirm actual local ТРА/owner rules, formula selection for composition and profile, applicable shoe placement and special cases. Test with source-backed real examples. Until then: arithmetic preview, not a securing order. Owner: infrastructure-normative-review.
3. **VU-45:** check every applicable field and comparison under the rules in force since 01.07.2026, including train category, brake force, density, tail values and edition. Do not call a mathematically consistent document operationally valid. Owner: brake-normative-review.
4. **Numerical coverage:** expand realistic bounded test vectors, full source-to-source donor parity, local conditions and negative cases; verify warning visibility and data retention on device. Owner: calculation-QA.
5. **Device QA:** run VU-45 and both securing forms, input switches, saving, accessibility and offline behavior at final manual acceptance. Owner: Android-QA.

## Next scheduled group

Group 4 remains **PARTIAL**, because normative acceptance is not complete. Continue with **group 5/8** in the next run; return to group 4 after the first 7+1 pass. Do not start the parked full crew-access permissions audit, do not alter donor Test-, do not close Issue #4.
