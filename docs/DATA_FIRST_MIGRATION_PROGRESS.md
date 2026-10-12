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
