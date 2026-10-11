# VL80S remaining migration audit

Pinned donor: `DomEnota-maker/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`.

This audit records the current modular migration state of VL80S and only the work that remains materially open.

## Canonical modular content already migrated

### Equipment and technical data

- 89 canonical equipment objects in model-owned Atlas packs.
- 89 corresponding Technical Data entries.
- 11 equipment domains: AU / BR / CB / CT / FR / HV / MC / PN / PR / SF / TR.
- generated legacy `vl80-detail-*` articles are intentionally superseded and are not migrated as a second catalog.

### Model profiles and applicability

- section-aware VL80S physical profile catalog with 9 buckets;
- profile selection is separate from the old broad `vl80s-general` donor applicability tag;
- unknown, modified and mixed sections remain fail-closed where exact section data is required.

### Acceptance

- 81 canonical acceptance items;
- 8 acceptance routes;
- shared `feature-acceptance` owns state, note persistence and route behavior;
- locomotive content owns the item/route data only.

### Diagnostics

- 103 canonical diagnostic cards:
  - 44 recommended;
  - 59 extended / `SUPPLEMENTAL_OPERATIONAL`.
- 1,181 Stage6 cross-feature relation edges preserved in `relation-graph.json`.
- actual enriched `DiagnosticRepository.scenarios` runtime exported from the pinned donor:
  - 103 executable scenarios;
  - 318 questions;
  - 954 strict YES/NO/UNKNOWN response edges.
- executable runtime validates question keys, targets, candidate-cause IDs and all three response branches fail-closed.
- model-specific observation index migrated:
  - 18 observations;
  - all links resolve against 103 canonical scenarios and 89 canonical equipment objects;
  - observation search has no action authority.
- diagnostic regeneration now preserves both `executableFlow` and `observationIndex`.
- regeneration was revalidated from the pinned donor without producing a generated-content diff.

All 103 diagnostic catalog entries remain `CANDIDATE`. Executable runtime availability does not itself grant publication status.

The structural candidate `vl80s.diag.pantograph-no-rise` remains gated until its independent GOLDEN REFERENCE acceptance actually passes.

### Schemes and interactive Atlas data

- 8 electrical scheme entries;
- 8 pneumatic scheme entries;
- 79 equipment objects linked to schemes;
- section-aware electrical/pneumatic variant policies;
- shared `feature-atlas` variant policy resolver:
  - selects only applicable overlays/rules;
  - refuses exact section claims when donor policy requires an actual section drawing;
  - fire-signalization serial conflict remains explicit-only and is never inferred automatically.
- exact contact-level replacement fragments are **not invented** where primary section drawings are unavailable.

### Top-view Atlas

- 15 model-owned normalized hotspots migrated;
- 4 hotspots have exact canonical equipment targets;
- aggregate VVK/BSA/cab zones remain presentation hotspots rather than invented equipment entities.
- original background resource was recovered from a verified historical Beta archive without restoring the legacy ZIP build:
  - source commit: `a3c93873bd128d4769d004098981235c169fd085`;
  - archive: `RailBrakeCalculator.zip`;
  - archive blob SHA: `6c3c7edc1713c1c901a566fd8a81a2494ee4ac58`;
  - archive entry: `RailBrakeCalculator/app/src/main/res/drawable-nodpi/vl80s_layout_section1.png`;
  - canonical output: `content-packs/electric/vl80s/atlas/interactive/layout-section1.png`;
  - SHA-256: `e492898a621b626c8fb74dc2f554b1bc74165ba41add01e5aa43f4a132e75367`.
- background provenance/hash are part of the Atlas layout contract.
- clickable shared-Atlas UI is wired and validated: the recovered image is rendered with normalized hotspot overlays, exact equipment hotspots emit typed canonical targets, aggregate zones remain informational, and Back returns from an equipment card to the layout.

### Stepwise pneumatic flows

Four legacy learning modes are canonical model-owned data:

- charging — 4 steps;
- service braking — 7 steps;
- release — 4 steps;
- auxiliary braking — 4 steps.

Step text and route coordinates remain explicitly training/presentation material, not exact pipe geometry and not action authority.

### Electrical functional flows

Five legacy functional trainer scenarios are canonical model-owned data:

- Тяга — 5 steps;
- Подъём ТП — 6 steps;
- Вспомогательные — 4 steps;
- Реостатный тормоз — 5 steps;
- Защита — 4 steps.

The migration preserves 50 node instances, 48 functional edges and 24 steps. Rendering authority belongs to the shared design system.

### Normal/reference values

Six VL80S reference/normal-value records from the donor `Vl80sNormalValues.kt` are migrated.

### Model-owned fire safety

The legacy `vl80-fire-safety` article has resolved ownership:

- data is owned by the VL80S model block;
- rendering is owned by shared `feature-safety`;
- it is not duplicated into Common;
- three VL80S fire-related diagnostic scenarios link to the model safety card;
- the donor source note was checked only to a 2025 revision, so current 2026 source status is deliberately not promoted to CURRENT;
- the migrated card is information-only and has no action authority.

## Deliberately not duplicated

The following donor concepts are superseded presentations rather than separate new stores:

- `vl80-pneumatic-groups` → canonical pneumatic equipment / schemes / Technical Data;
- `vl80-pneumatic-simulator` → canonical stepwise pneumatic flow data;
- `vl80-electrical-simulator` → canonical electrical functional-flow data;
- `vl80-detail-*` → canonical equipment + Technical Data cards;
- legacy EquipmentReference observations → canonical 89-object equipment catalog.

## Material work still open

### 1. Diagnostic publication / acceptance

This is the main remaining safety gate.

Runtime completeness and publication acceptance are separate concerns.

Before changing an individual scenario from `CANDIDATE` to `ACTIVE`:

1. its applicability/profile assumptions must be accepted;
2. source and safety review must be complete for the intended layer;
3. all branches must pass semantic acceptance, not only navigation smoke;
4. the extended/restricted policy must remain independent from recommended diagnostics;
5. `vl80s.diag.pantograph-no-rise` requires the separate GOLDEN REFERENCE gate.

Until then the runtime may be loaded/tested but normal user execution remains fail-closed.

### 2. Shared feature UI integration

On 2026-10-09, shared `feature-atlas` learning screens were wired into
`app-shell` and extended with graphical functional presentation:

- four pneumatic training modes support selecting a mode and stepping
  forward/back/reset; route segments accumulate up to the selected step;
- five electrical functional scenarios support the same navigation;
  the shared renderer draws nodes, functional edges and active states from
  model-owned scenario coordinates without introducing VL80S-specific UI;
- electrical equipment nodes open detailed information and, only where an
  exact canonical equipment target exists, navigate to its Atlas card;
- the app loads these flows from the canonical Atlas feature index and
  rejects cross-model or action-authoritative flow payloads.

#### Source-pinned pneumatic image recovery

The exact source raster used by the legacy step routes was located and
recovered from the verified historical Beta archive, NOT approximated:

- source commit: `a3c93873bd128d4769d004098981235c169fd085`;
- archive blob SHA: `6c3c7edc1713c1c901a566fd8a81a2494ee4ac58`;
- source entry: `RailBrakeCalculator/app/src/main/res/drawable-nodpi/vl80s_pneumatic_scheme.jpg`;
- canonical asset: `content-packs/electric/vl80s/atlas/interactive/pneumatic-scheme.jpg`;
- JPEG source size: 84,607 bytes; source dimensions: 1181 × 573 pixels;
- SHA-256: `e40ed2cfba42e24b38701af59f31f5870a880822b78a46d4cafeeebb8fd14176`.

The pneumatic flow's source provenance and matching coordinates are checked
fail-closed by the domain loader and migration validation. When its verified
raster is missing or fails runtime dimension checks, routes are NOT drawn on
an invented image: the UI falls back to readable steps.

Both graphical schemes are **functional/educational**, not exact wiring,
pipework, mounting or permission to operate. Electrical positions come
from the donor's functional training layout; the pneumatic overlay is
matched to the donor's original JPEG rather than inferred.

#### Clickable pneumatic apparatus

The 10 donor training-image regions and their original descriptive fields
(title, short description, normalized left/top/right/bottom rectangle,
working principle, possible failure signs and training checks) now live
as canonical model-owned pneumatic-flow data. They are pinned to
`DomEnota-maker/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`
and blob `0f18989087a7f4f2efcbdd46bdf05b1065d8f54c` in
`KnowledgeBaseScreen.kt`. The shared Atlas renderer now supports
image-region tapping, deterministic resolution of overlapping regions,
a horizontally scrollable accessible apparatus picker, and immediately
accessible scrollable apparatus detail dialogs. All explanations are explicitly donor training
content, NOT accepted operational instructions, and no guessed canonical
equipment mapping is used.

#### Shared diagnostics with strict publication gate

The `feature-diagnostics` module now owns both its verified executable
graph engine and a shared Compose catalog/step-by-step Yes/No/Unknown UI.
The app shell loads the model's diagnostic feature index and executable
runtime and provides a navigation callback from the interim Atlas layout.

The catalog uses `ContentRegistry.resolve` and checks the runtime's
model ownership before exposing or opening ANY scenario. This checks
publication status, current model, variant applicability and allowed
information layers. The raw executable runtime being present is never
enough to open a scenario. Search covers only approved scenarios.

**Current expected end-user behavior:** all 103 VL80S diagnostics remain
`CANDIDATE`, so the new diagnostic catalog must show no openable scenarios
until independent publication acceptance is completed. This is intentional,
not missing data. Golden reference status is not silently promoted.

#### Pixel emulator smoke coverage

An Android Compose instrumentation smoke suite now exists at
`app-shell/src/androidTest/java/ru/railbrake/calculator/shell/Vl80sNavigationSmokeTest.kt`,
executed by `.github/workflows/vl80s-android-ui-smoke.yml` on Pixel API 34.
It tests:

- navigation into the shared pneumatic and electrical training routes;
- mode switching, step-count resets, and return to the common Atlas;
- opening/dismissing source-pinned pneumatic instrument explanations;
- the diagnostic catalog staying empty for unpublished candidate scenarios,
  including search for the still-gated pantograph example.

Expanded integration evidence (2026-10-11):

- `Vl80sLearningFlowInstrumentationTest` exercises **all four pneumatic
  modes** and **all five electrical scenarios**, including Next, Previous,
  Restart and scenario-switch reset.
- `Vl80sContentNavigationInstrumentationTest` follows the **actual**
  Atlas transformer hotspot -> canonical equipment card -> Technical Data.
- The new test was first observed failing on the Android emulator with
  `Semantic Node has no parent layout with a Scroll SemanticsAction`,
  proving that long `RailContentEntryScreen` cards did not allow users to
  scroll to links. Shared design-system now gives the article and links one
  bounded vertical-scroll viewport with a fixed heading and resets scroll
  state when the canonical entry ID changes.
- Regression was confirmed green with **5/5 instrumented Android tests**
  (GitHub Actions run `38156179846`), plus green module/Gradle/APK
  validation (run `38156156994`). This covers source-pinned preview
  navigation; it does **not** grant operational authority to any content.
- The Android UI workflow now also re-runs for changes in shared design
  system, acceptance, safety, content-runtime and link-router modules.

Engineering review tools:

- Context7 checked current Android Jetpack Compose testing, semantics,
  `verticalScroll` and constrained `Column` patterns against official
  Android developer documentation, rather than guessing an API contract.
- Superpowers methodology was tried selectively for bounded QA:
  reproduce failing device test -> inspect exact failure -> minimal shared
  fix -> re-run full CI/UI suite. This produced a concrete scrollability
  regression test; its overall cost/benefit for larger migrations is
  still to be assessed.



This is device smoke coverage, NOT a source/safety acceptance of diagnostics
or a substitute for manual inspection of route drawing and touch regions.
The workflow is kept separate from basic module lint/build validations.

Remaining shared UI and acceptance work:

- independently review donor pneumatic texts against current approved
  operating documentation before relying on any reported checks;
- keep Acceptance presentation in shared `feature-acceptance`;
- extend emulator coverage and visually inspect touch maps, long text,
  physical Back navigation and responsive layouts on different screen sizes;
  first five Pixel API 34 UI cases now pass, but manual and multi-device
  acceptance is still outstanding;
- complete separate semantic, source and safety acceptance of diagnostic
  scenarios and publish only those that genuinely pass.

No model-specific UI implementation is introduced to complete these screens.

### 3. Exact section-specific graphical fragments

Variant policy resolution is implemented, but some donor policies explicitly require a primary/actual section drawing for exact contact-level or equipment-layout claims.

Those exact graphical fragments remain gated. They must be added only from verified source drawings; no generated or inferred fragment may silently become authoritative.

### 4. Final VL80S integration acceptance

After the shared feature screens above are wired, run a model-level acceptance that verifies:

- runtime-index loads every intended VL80S pack exactly once;
- no legacy ZIP/patch path is used;
- cross-feature links resolve within VL80S or to true Common content only;
- direct cross-model links are absent;
- working-model state is not mutated by viewing/navigation;
- recommended and extended diagnostics remain separated;
- candidate diagnostics cannot be executed through normal published navigation;
- Atlas top-view/background/hotspots/flows all load from canonical model assets;
- Acceptance, Atlas, Diagnostics, Technical Data and model Safety use shared feature/design-system implementations.

## Migration rule

No remaining legacy VL80S class or asset is copied merely because it exists.

For every remaining source choose exactly one:

- canonical data migration;
- shared feature/runtime migration;
- absorb into an already migrated canonical object;
- superseded legacy presentation — do not migrate;
- unresolved source/acceptance gate — keep fail-closed until explicitly resolved.
