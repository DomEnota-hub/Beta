# Stage 1/15: pinned asset and TEM2 source-object parity (2026-11-09)

**Status: PARTIAL, stage 1 remains open.** Source: read-only `DomEnota-hub/Test-` at `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Target: `DomEnota-hub/Beta`, branch `audit/information-block-gaps-20261014`.

## Raw-asset integrity boundary

The complete donor `app/src/main/assets/` tree contains **36 blobs**: 9 VL80S, 6 Ermak, 6 CHME3, 6 TEM2, and 9 shared assets. Their pinned Git blob SHA-1 and byte lengths are in `docs/migration/donor-asset-crosswalk.json`.

Exact byte equality was observed for **three distinct donor assets**, represented by **five Beta copies**:
- `ermak_links.json.gz`: two preserved copies under Ermak migration.
- `ermak_system_map.json.gz`: two preserved copies under Ermak migration.
- `source_presentations.json`: one preserved copy under locomotive-migration.

The remaining 33 assets have **no identical blob in the Beta tree**. This is **not** a missing-record finding: canonical packs are transformed and cannot be compared by raw blob SHA. The suggested family roots in the crosswalk are not verified object destinations.

`qa/validate_donor_asset_crosswalk.py` verifies all 36 manifest records, checks the five byte-identical copies against pinned Git blob hashes, validates catalog roots, and verifies that existing runtime-index paths do not traverse directories, reference another family, or include candidate/research/migration paths. Four negative/positive unit tests cover blob hashing, tampering, path traversal and candidate/cross-model rejection.

**CI:** `Pinned donor asset crosswalk` run [42665809286](https://github.com/DomEnota-hub/Beta/actions/runs/42665809286) **SUCCESS**, 4/4 tests; `DONOR_ASSET_CROSSWALK_PASS assets=36 exact_copies=5 indexed_runtime_packs=51`.

## TEM2/TEM2U: full source-object comparison for six uncompressed donor JSON assets

A direct read of the six pinned donor JSON assets and Beta canonical pack `sourceObject.object` fields found:

| Kind | Donor occurrences | Distinct Beta canonical objects | Differences |
|---|---:|---:|---:|
| TEM2 + TEM2U catalog | 122 + 131 = **253** | **253** | 0 |
| TEM2 + TEM2U diagnostic scenarios | 22 + 24 = **46** | **33** | 0; 13 identical-source merges |
| Shared scheme layouts | **17** | **17** | 0 |
| Shared stepwise sequences | **17** | **17** | 0 |
| **Total** | **333** | **320** | **0** |

All 333 source occurrences resolve to canonical IDs in `content-packs/diesel/tem2-family/migration/source-audit.json`; 320 have disposition `MIGRATED`, 13 `MERGED_WITH_CANONICAL`, and `unresolvedReferences=[]`. The existing migration validator also asserts 1,073 internal links and model/variant separation.

**Crucial:** all 320 canonical objects are still marked `publicationStatus=CANDIDATE`, `actionDisposition=INFORMATION_ONLY`, `provenance=UNKNOWN`, `sourceStatus=UNKNOWN`. Source-object equivalence does **not** authorize publication or operational instructions. No TEM2 runtime-index is present in the inspected model root; Android integration is a separate stage.

Added repeatable CI workflow `.github/workflows/tem2-source-parity.yml`: fetches the six exact donor files at the pinned SHA, verifies each Git blob SHA through `qa/migrate_tem2.py`, compares **all 333 source objects** with their 320 canonical Beta objects via `qa/validate_tem2.py --donor-dir`, and verifies byte-for-byte regeneration of the canonical packs.

**CI:** `TEM2 pinned source object parity` run [42666239232](https://github.com/DomEnota-hub/Beta/actions/runs/42666239232) **SUCCESS**; `TEM2_VARIANT_AND_SCHEME_PASS {'catalog': 253, 'diagnostics': 33, 'layouts': 17, 'sequences': 17}`.

## Remaining stage-1 work

1. Perform semantic record-level parity for VL80S, Ermak, CHME3/Т/Э, and shared assets, including compressed `.json.gz` donor inputs, stable IDs, aliases, profile applicability, provenance and links.
2. For TEM2, audit source authority, execution-specific applicability and publication gates separately; **do not promote the 320 candidate objects automatically**.
3. Verify non-asset Kotlin/legacy local-state feature parity and the difference between authoring content and actual Android runtime registration.
4. Re-run the full modular CI to terminal status and fix any failures before marking the stage complete.

No Android UI or application logic was changed in this pass. This report proves a bounded data-preservation slice, not whole-app readiness.
