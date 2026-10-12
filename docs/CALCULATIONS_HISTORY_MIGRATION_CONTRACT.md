# Calculations and History — data-first migration contract

Pinned source: `DomEnota-maker/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`. This is a source/compatibility contract, **not** a claim that the new modular application has the calculator or history UI. Numerical behavior below is donor behavior, **not** an independent check of current railway rules.

## Effective build and ownership

The donor `README.md` says its CI unpacks `RailBrakeCalculator.zip` and overlays `patch/`; root `app/` mirrors overlapping paths. All 169 common `app/` and `patch/app/` blobs in this pinned tree are SHA-identical. `BrakeCalculator.kt` is present only in `patch/app/src/main/java/ru/railbrake/calculator/core/` (Git blob `5ec501f1a157666ea36d9fff0f3103fe118fbf9b`). `HistoryRepository.kt` is present in the ZIP base (archive Git blob `6c3c7edc1713c1c901a566fd8a81a2494ee4ac58`), not in either mirror. The UI consumer is `app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt` (blob `b369e8fbf500799a860f1356672abd9a4b41748b`); theme preferences are also used in `app/src/main/java/ru/railbrake/calculator/MainActivity.kt`.

The data/algorithm boundary is a common functional calculations contract, and history is a separate common local-storage boundary (see `docs/AUXILIARY_APP_BLOCKS.md`). Neither belongs to a locomotive pack. The legacy table of locomotive masses is reference/profile data for an optional consist input; it does not make the calculator model-owned. Do not copy local user records into the repository.

## Modes and donor algorithm

| Operation | Inputs and units | Calculation and outputs | Source/decision |
|---|---|---|---|
| Wagon axle count | number of 4-, 6-, 8-axle wagons and extra axles; nonnegative integers | `4*w4+6*w6+8*w8+extra` with exact integer overflow rejection | `BrakeCalculator.wagonAxles`; retain as helper |
| By mass | mass `M` tonnes >0; axle count >0 **or** manual axle load tonnes/axle >0; slope `i` exactly one of 0,2,4,6,8,10,12 ‰ | axle load `M/n` unless manually supplied; select table row, `K=M*k/100`, `N=M*kManual/100`, separately ceil each; emits raw/rounded values, category, slope and coefficients | `calculateMass`; keep formula and table together until source/status review |
| Mass shortage supplement | prior mass result; available shoes ≥0; braked axles per hand-brake unit >0 | shortage `max(0,ceil(K)-available)`; **exact** remaining equivalent `max(0,K-available)`; additional axles `ceil(equivalent*kManual/k)`; units `ceil(additional/axlesPerUnit)`; reserve from actually braked axles | `calculateMassSupplement`; do not replace exact equivalent with integer shortage |
| Appendix №12 | axle count >0; profile NORMAL/BROKEN_FULL_TRACK/SEPARATE_SEGMENT; slope `i` ‰ ≥0; formula 1/2 when `i>0.5`; oily rails; wind speed m/s ≥0 and dangerous direction; available shoes ≥0; axles per parking-brake unit >0; leaving without locomotive and paragraph-20 confirmation | at `i≤0.5` base 2, otherwise `n*(1.5*i+1)/200` or `n*(4*i+1)/200`; oily multiplier 1.5 before ceiling; one opposite-side shoe at `0.5<i≤1`; wind 0/3/7 per 200 axles, then ceil; substitute 5 axles per missing shoe, with special parking-brake rule only at `i<0.5` and additional oil/wind shoes still owed. Result exposes exact bases, shoe counts, shortage, substitution, units, reserve, applied rules | `calculateAppendix12`; conditional `leavingWithoutLocomotive && i>2.5` requires explicit paragraph-20 confirmation. Railway source currency unverified |

Mass coefficients, indexed by slope `[0,2,4,6,8,10,12]‰`:

| Row | 0 | 2 | 4 | 6 | 8 | 10 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shoes per 100 t, load ≥10 t/axle | .2 | .2 | .2 | .2 | .2 | .3 | .4 |
| Shoes per 100 t, load <10 t/axle | .4 | .4 | .4 | .4 | .6 | .8 | 1.0 |
| Manually braked axles per 100 t | .4 | .4 | .4 | .4 | .6 | .8 | 1.0 |

Exactly 10.0 t/axle takes the ≥10 row. Explicit `LESS_THAN_10` at exactly 10.0 is **training-only**, never a silent normative default. Wind coefficient applies only in the dangerous direction: speed `>15` →3, `>21` →7 (strict boundaries). Slope `0.5` is low-slope base but **not** the `<0.5` special parking-brake rule. `ProfileMode` is carried as an input and the UI explains it; the current formula implementation does **not** branch on that enum, so do not invent a numerical effect.

The donor UI has direct mass/axles, wagon counts, consist picker and manual axle-load input paths; output is quick or study. The mass result can prefill Appendix №12, while station conditions are computed in that separate mode. `LocomotiveDatabase.kt` in the ZIP base contains **46** `LocomotiveSpec` entries with name/category/mass tonnes/axles/note/massKind/sourceNote; user-defined consist entries are constructed in the UI. These values are unverified reference inputs, can vary by modification, and require a dedicated static-data mapping before reuse. They must not silently become authoritative model specs.

Validation: finite positive mass/load; positive axles; finite nonnegative Appendix slope/wind; nonnegative available shoes; positive axles per hand-brake unit; exact table slope in mass mode; formula required only above 0.5‰; overflow fails; above 2.5‰ without paragraph-20 confirmation rejects the specified leaving-without-locomotive condition. `ceilToInt` also rejects nonfinite/overflow values. The UI's Russian numeric parsing, empty input, error labels and saveable form state should be tested during functional migration, not guessed from the pure engine.

## Donor regression vectors (structural handoff)

These are exact expected assertions from the pinned ZIP's `app/src/test/java/ru/railbrake/calculator/core/BrakeCalculatorTest.kt` and its displayed source behavior; they were **not rerun as compiled donor tests** in this data-first cycle because no Kotlin compiler is installed in the current scratch environment. A future engine transfer must run these plus missing/invalid/rounding cases.

| Case | Input | Expected donor output |
|---|---|---|
| Mass ordinary | 4000 t, 212 axles, 12‰ | 16 shoes; 40 manually braked axles |
| 10 t/axle boundary | 1200 t, 120 axles, 10‰ | heavy row, 4 shoes; explicit training override <10 gives 10 |
| Exact shortage | 3800 t, 200 axles, 12‰; 15 shoes, 4 axles/unit | exact 15.2; rounded 16; shortage 1; remaining equivalent 0.2; one additional axle and one unit |
| Appendix formula 1 | 200 axles, 8‰, oily, wind 16 m/s dangerous direction, 15 shoes, 4 axles/unit | 23 total shoes; shortage 8; 40 substitute axles; 10 units |
| Low slope special | 200 axles, 0‰, no oil/wind/shoes, 4 axles/unit | 2 base shoes; special one parking-brake unit; 0 substitute axles |
| Same with wind | previous, wind 16 m/s dangerous direction | 3 wind shoes, 3 extra after special; 15 substitute axles, 5 units |
| Exactly 0.5‰ | 200 axles, 0 shoes, 4 axles/unit | special rule false; 10 substitute axles, 3 units |
| Wind strictness | 200 axles, 8‰; speed 15/15.0001/21/21.0001 m/s | coefficients 0/3/3/7 |
| Invalid | nonfinite mass/wind; wagon axle integer overflow; leaving without locomotive at >2.5‰ without confirmation | rejected by donor tests |

## History shape and local compatibility

The ZIP member `app/src/main/java/ru/railbrake/calculator/data/HistoryRepository.kt` defines exactly five `HistoryRecord` fields: `timestampMillis: Long`, `mode: String`, `title: String`, `summary: String`, `details: String`. Mass writes `mode="По массе"`; Appendix writes `mode="ИДП №12"`. UI shows all records newest first, category filters, and **clear all**; no individual delete/export/recovery operation was found in this source.

Persistence is Android `SharedPreferences("calculation_history", MODE_PRIVATE)`, key `"records"`, a `StringSet`. Each entry is five pipe-separated fields: decimal timestamp then four UTF-8 strings encoded Android Base64 `NO_WRAP | URL_SAFE`. `load` silently drops malformed entries and sorts descending by timestamp. `add` prepends, deduplicates by timestamp and keeps at most **30** records; `clear` removes the key. A same-millisecond collision can lose a record. No explicit schema version or transactional recovery exists. Preserve raw records before changing the serializer; a new reader must accept this exact format, avoid writing an incompatible value under the same key, and demonstrate in-place upgrade with sample records and corrupt-entry handling. No real user data was accessed.

`app-shell` currently has `applicationId="ru.railbrake.calculator"`, matching the donor, and `android:allowBackup="false"`. This is a necessary but insufficient condition for preserving local preferences: install/signing identity and upgrade behavior are not verified here. Do not uninstall an installed app as part of migration.

`SharedPreferences("calculation_inputs")` holds string keys `axles`, `slope`, `available_shoes` in both calculators, and `accent_palette` / `theme_mode` in `MainActivity`. Other UI inputs are Compose `rememberSaveable`/ephemeral in the inspected source, not proven durable persistent settings. Snapshot these keys and defaults and test restored values before changing preference ownership. The calculator/history are not copied into `content-packs/common/`.

## Open decisions and next functional stage

- Railway norm and source revisions for mass coefficients, Appendix №12, locomotive masses and UI explanatory claims have **not** been independently reviewed. Retain donor behavior as a regression reference only; do not label it current law.
- A minimal mapping for 46 locomotive reference specimens and any linked static tables belongs to the common reference layer or explicitly applicable model profile **after source review**. The pure formula/table can remain within the future calculations module until separating it is provably behavior-preserving.
- The next separately authorized functional stage will port and execute the engine tests, implement a legacy-compatible history reader/writer and preference migration, connect shared UI/navigation, and verify upgrade with matching signing identity. This data-first cycle does not claim those functions work in the modular APK.
