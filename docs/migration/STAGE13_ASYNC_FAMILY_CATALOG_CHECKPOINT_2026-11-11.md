# Stage 13/15 — family catalog loading without blocking the UI (11.11.2026)

**Status: PARTIAL, NOT CLOSED.** Main stages fully completed: **11/15 (1–10, 12)**. Stage 11 Sherpa-ONNX remains a separate required TODO. Stage 13 is still active. Stage 14 has **not** been started in this run.

## Why this change was needed

At the previous checkpoint `FamilyContentScreen` invoked `FamilyContentCatalog.load(profile)` inside Compose `remember(profile)` before the user selected an execution, even for unpublished diagnostics. This could perform recursive asset enumeration and JSON parsing on the main/UI thread, independently of whether the chosen family was published. A prior user-facing review identified this as a performance risk. This checkpoint addresses the code path, **not** a measured latency result.

## Verified implementation (Beta only)

- `app-shell/src/main/java/ru/railbrake/calculator/shell/FamilyCatalogLoadPolicy.kt`: loading requires **an explicit registered execution** and only an Atlas or Acceptance destination. Diagnostics never load family packs through this path.
- `app-shell/src/main/java/ru/railbrake/calculator/shell/FamilyContentScreen.kt`: family asset enumeration/parsing runs in a cancellable `LaunchedEffect` via `withContext(Dispatchers.IO)` **after** execution selection. UI distinguishes loading, failure, empty publication, and unknown execution. State is keyed by model, execution, destination and repository to prevent reuse of an old model's snapshot after selection changes. Cancellation is rethrown instead of converted into a load failure.
- `app-shell/src/test/java/ru/railbrake/calculator/shell/FamilyCatalogLoadPolicyTest.kt`: **3 new JVM unit tests** across all seven non-VL80S models, checking no load before selection, valid exact execution, cross-series/unknown rejection, and diagnostics quarantine.

**Actual user-visible effect:** execution selector opens without attempting to parse family packs first; after selection, an explicit loading/error state is displayed. Unknown saved execution fails closed instead of showing a perpetual loading message. This is **not** publication of new Ermak/CHME3/TEM2 content.

## Commits and CI (terminal)

- Code: [`967cd33806ed710502b92364755d24ac3ddc1421`](https://github.com/DomEnota-hub/Beta/commit/967cd33806ed710502b92364755d24ac3ddc1421) — asynchronous, deferred, cancellable family loading + policy/tests.
- Code: [`384ad1c2f90629f8f02e14b11d0a8f457d2f2cb1`](https://github.com/DomEnota-hub/Beta/commit/384ad1c2f90629f8f02e14b11d0a8f457d2f2cb1) — unknown saved execution state.
- [Stage 13 family gates #42907011368](https://github.com/DomEnota-hub/Beta/actions/runs/42907011368): **SUCCESS terminal**, `:app-shell:testDebugUnitTest`, `:app-shell:lintDebug`, `:app-shell:assembleDebug`, built-APK quarantine, family pack validators.
- [Modular architecture bootstrap #42907023545](https://github.com/DomEnota-hub/Beta/actions/runs/42907023545): **SUCCESS terminal** (both jobs), including contract/runtime tests, Android lint, assembleDebug, APK assets and research/safety boundaries.
- On the final **code SHA `384ad1c2`**, **25/25 GitHub Actions workflow runs completed SUCCESS**. No pending/failing run in the fetched head_sha query.
- Phone/instrumentation execution remains for final manual QA. No production release and no claim of measured performance improvement.

## Non-negotiable remaining work and blockers

1. **Source-to-source user-access parity:** Test- @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` versus Beta, by object/series/execution/source, to distinguish formerly visible standard/extended informational material from genuinely unreviewed candidates. The fact that a migrated entry says `CANDIDATE/UNKNOWN` is not proof it was prohibited in Test-. The complete deep audit of crew permissions remains **FUTURE/PARKED**, per separate user direction; do not start it implicitly.
2. **Publication and packaging:** family `.pack.json` files still contain unreviewed entries. Gradle's family-directory APK quarantine remains in place. Need a narrow, independently reviewed allowlist of source-backed entries and their precise execution metadata, plus APK positive/negative regression, before re-enabling *any* family assets.
3. **Actual user routes:** Atlas/Acceptance/Diagnostics for Ermak, CHME3/T/E, TEM2/U are not yet published end-to-end; source-verified family graphs, links, role/variant gates and diagnostic safety must be independently validated.
4. **Separate required TODO:** Sherpa-ONNX offline voice Stage 11, with license/hash/ABI verification; cannot be called complete based on Android fallback.
5. **Unresolved donor source references:** CHME3 610, Ermak 548, ER-DIAG-136 and exam copyright checks remain in Issue #4 backlog; they must not block unrelated safe Kotlin work or be silently authorized.

**Next exact Stage 13 action:** implement a small machine-checkable **Test- → Beta visible-card crosswalk** (at least one representative per family, including opt-in state and execution), then restore a first **source-verified informational card per family** using a minimal packaged allowlist and test real navigation/APK content. If provenance or variant is unresolved, leave that card unpublished and explicitly record the missing source rather than changing the gate to accept all candidates.

## Scope protection

The separate plan `docs/backlog/FUTURE_PERFORMANCE_AND_CREW_ACCESS_AUDIT.md` is preserved and **not activated**. No permission policy, extended-mode authorization, role gate or donor repository was changed in this run. The existing candidate/research APK quarantine is unchanged.
