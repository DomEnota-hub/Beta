# Data-first migration progress

Scope: `DomEnota-maker/Beta:modular-rebuild`. Pinned read-only donor: `DomEnota-maker/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`. This log records the addendum `RailBrakeCalculator_Work_Addendum_Data_First_v2_2026-10-12.md`; it does not authorize publication of imported operational content.

## Stage 0 — handoff baseline (2026-10-12)

- Starting branch HEAD: `6abe98e22d746aa8ed696804916b49aa3928cadf`, documentation handoff after code `c53f1a5977c8bbcd287d2a0913807aad253c35be`. Previous cycle details and open device/visual checks: [VL80S integration acceptance](VL80S_INTEGRATION_ACCEPTANCE_2026-10-12.md).
- [Bootstrap 38224131334](https://github.com/DomEnota-maker/Beta/actions/runs/38224131334) and [Pixel API 34 UI 38224131293](https://github.com/DomEnota-maker/Beta/actions/runs/38224131293) both `completed/success` on code SHA `c53f1a5977c8bbcd287d2a0913807aad253c35be`. The visible/system Back regression is closed. Later commit `6abe98e` changes documentation only. No final full-spec acceptance is claimed.
- Baseline boundaries read: `docs/MODULAR_CONTENT_TOPOLOGY.md`, `ARCHITECTURE_BOOTSTRAP.md`, `VL80S_MIGRATION_GUARD.md`, `VL80S_EXECUTABLE_DIAGNOSTIC_RUNTIME.md`, `VL80S_REMAINING_MIGRATION_AUDIT.md` and all three `FEATURE_*_BOUNDARY.md`.
- Existing VL80S canonical data includes 89 equipment + 89 Technical Data entries, 81 acceptance items / 8 routes, 103 diagnostic scenarios (all `CANDIDATE`), 18 observations, 15 Atlas hotspots, four pneumatic and five electrical training flows. These are not scheduled for repeat import.
- `content-packs/common/`, `electric/ermak/`, `diesel/chme3-family/` and `diesel/tem2-family/` have placeholder directories, not a completed content migration. Calculations/history are common functional blocks requiring source inventory and a separate contract, not per-model copies or user data inside content packs.
- Stage 0 does not establish technical/normative acceptance of VL80S content. Unfinished multi-device touch/visual and safety/source review from the previous specification remain explicitly open; broad UI development is deferred under the addendum.
- Next: source inventory across donor `app/`, `patch/`, `docs/`, Kotlin-embedded content, JSON/gzip, media, calculations/history. Each object needs one disposition and a count. The tree alone is discovery, not proof of completeness.

## Stage results

Append after each major completed stage: starting and ending SHA, source and destination counts, tests/CI on matching SHA, unresolved sources, safety status, and next step. Do not use `RailBrakeCalculator_BACKLOG.md` as a task source.

## Stage 1a — pinned source discovery (2026-10-12)

- Starting SHA `8056095b8d0fb7c2826165978c43159e1336f397`; source inventory checkpoint commit `bce37d937391bc84dc365fad81e36ea99e69bab4`. [Inventory](DATA_MIGRATION_INVENTORY.md) lists the 35 technical assets and 70 locomotive source JSON documents with observed top-level array counts and Git blob SHA prefixes.
- The pinned donor tree has 738 blobs. A local discovery ledger classified every path and three inspected ZIP members in 837 file/group rows: 169 exact `app/` ↔ `patch/app/` mirrors, 206 groups awaiting canonical mapping, 254 sources needing extraction review, 208 functional/test infrastructure rows. These interim statuses are **not** the six final migration dispositions; no data has been declared migrated by this count.
- Source groups observed: Ermak 111 equipment, 138 knowledge articles, 136 diagnostic scenarios, 22 schemes; CHME3/CHME3T/CHME3E catalogs 306/319/428 and diagnostics 55/56/67; TEM2/TEM2U catalogs 122/131 and diagnostics 22/24. These are source counts with possible overlap, not unique validated canonical totals.
- `exam_questions.json` is AES/CBC encoded. Using the donor's pinned `ExamPayloadCodec` read-only recovered the structural count of 329 unique IDs across four blocks (164/29/72/64). No question content was published or promoted.
- `RailBrakeCalculator.zip` is the CI build base; the overlay `patch/` contains `BrakeCalculator.kt` missing from root `app/`, while the ZIP contains the local `HistoryRepository.kt` absent from both mirrors. The ZIP also holds the two original VL80S rasters already recovered in Beta. This resolves the build composition for the calculations/history contract.
- Verification: Git tree SHA comparison for 169 mirrored pairs; JSON/gzip parse of 35 technical assets and 70 source documents; read-only ZIP member inspection; decoder-derived Q&A counts and uniqueness. No Android run was needed or started for source discovery. Safety and railway norm currency were **not** established.
- Remaining in Stage 1: object-level canonical mappings, nested fields, generator-embedded unique material, remaining ZIP members and variant conflicts. Next, document the common calculations/history contract and resolve source classifications before broad import.
