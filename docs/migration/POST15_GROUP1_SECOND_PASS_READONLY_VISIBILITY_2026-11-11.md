# RailBrakeCalculator — post-15 second pass, group 1/8: family reference visibility without execution

**Date:** 11.11.2026. **Status: PARTIAL / CODE AND CI VERIFIED; QA APK DELIVERED.** This is the second pass over the first of eight remediation groups, not closure of group 1, stage 13, or Issue #4. Main migration stages accepted: **11/15**. Immutable donor Test- at `3176d6ee228f0ed4b78371f45209e10c1c724eff` was not changed.

## User-facing behavior actually changed in Beta

- [`dcaf7ecca614a8bb0bfc9694a22c9f98ac7d9080`](https://github.com/DomEnota-hub/Beta/commit/dcaf7ecca614a8bb0bfc9694a22c9f98ac7d9080): `FamilyReferencePreviewPolicy` now exposes an **independent, read-only** `searchBeforeExecution` route. For a model with several executions, only donor summaries marked `EXECUTION_UNVERIFIED` and with no execution ID can appear. For a model with a single registered execution, the matching `DONOR_VARIANT` summary can be read before choosing the execution. The existing `canShow` execution gate remains unchanged.
- [`a27390089bdcce1f164b56c98249b49f055d6594`](https://github.com/DomEnota-hub/Beta/commit/a27390089bdcce1f164b56c98249b49f055d6594): `FamilyContentScreen` loads only the small curated Atlas summaries even when execution is not selected, shows search, individual reference cards and prominent **execution not selected / applicability unverified / not permission to act** warnings. Full family packs, acceptance and diagnostics still require exact execution and separate authorization.
- [`045d8ff3b99bfa931d205347f7ce6af1d6092687`](https://github.com/DomEnota-hub/Beta/commit/045d8ff3b99bfa931d205347f7ce6af1d6092687): three new JVM tests cover single-variant reference visibility without execution, multi-execution Ermak isolation, CHME3T serial boundary №6245, invalid provenance, model/section isolation, and the unchanged fail-closed action/pack gates.

**Measured source inventory and scope:** `crew-reference/summaries.json` has **84** previously packaged, donor-traceable, summary-only records: 12 each for 2ЭС5К, 3ЭС5К, ЧМЭ3, ЧМЭ3Т, ЧМЭ3Э, ТЭМ2 and ТЭМ2У. **84 reference cards** are now eligible to be viewed before execution selection under their exact model; **0 new cards copied**, **0 new executable routes**, **0 newly approved actions**. All 84 still have uncertainty/permission warnings. This is policy and static asset verification, **not physical-device navigation proof**. No donor-variant summary of one CHME3T serial group is exposed as applicable to the other.

## Verified CI and actual APK

At final implementation/test SHA `045d8ff3`: **28/28 GitHub Actions workflow runs terminal SUCCESS**, including:
- [Stage 13 family profiles/publication gates #42988490795](https://github.com/DomEnota-hub/Beta/actions/runs/42988490795): `:app-shell:testDebugUnitTest`, Android lint, `:app-shell:assembleDebug`, `STAGE13_DONOR_SUMMARY_PARITY_PASS entries=84 models=7 executable=0`, family variant/source checks and actual APK gate. Gradle **BUILD SUCCESSFUL in 3m**.
- [Stage 15 integration QA #42988490791](https://github.com/DomEnota-hub/Beta/actions/runs/42988490791): terminal SUCCESS, Debug APK and AndroidTest compilation plus integration checks. **AndroidTest not executed on a device**.
- [Modular architecture bootstrap #42988498396](https://github.com/DomEnota-hub/Beta/actions/runs/42988498396) and [Stage 9 assistant UI #42988490745](https://github.com/DomEnota-hub/Beta/actions/runs/42988490745): terminal SUCCESS.

Stage 15 artifact `13841556145` ZIP integrity PASS; extracted `app-shell-debug.apk` ZIP integrity PASS; curated `assets/crew-reference/summaries.json` present; full `assets/electric/ermak/`, `assets/diesel/chme3-family/`, `assets/diesel/tem2-family/` still excluded (**0** directories). This exclusion remains a **known migration regression/backlog**, not a successful full-family publication.

**Delivered Debug/QA APK (not production)** to verified Google Drive `Rail` folder ID `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`:
- [`RailBrake_Beta_1.2.2-modular-alpha01_post15-group1-second-pass_debugQA_045d8ff3.apk`](https://drive.google.com/file/d/11Hw_JQuTxksXBJTTQVbv_KTmyhWqzf1l/view)
- Size **9,649,409 bytes**, SHA256 **`569db254124cfd069df6b33120ed9d2e06475040a23d392b20a125079112ca7c`**.
- Upload verified independently with Drive file metadata: exact name, size and parent folder. Under 100 MB, delivered as one APK, no split-ZIP.

## Mandatory open work and next action

1. **Full family parity still missing:** large Ermak/CHME3/TEM2 catalogs, acceptance, interactive schemes, diagnostic graphs and action paths remain excluded/blocked. Need source-to-source comparison and typed **knowledge visibility vs action permission** separation before replacing `ignoreAssetsPattern` or `FamilyPublicationGate`; never mass-activate candidates or bypass roles/profiles.
2. **Sources and rights:** 548 Ermak references, 610 CHME3 links, exact serial/MSUD variants, current edition and lawful redistribution need verification. No full external normative/crew-permission audit now: `docs/backlog/FUTURE_PERFORMANCE_AND_CREW_ACCESS_AUDIT.md` remains PARKED by user instruction.
3. **Device acceptance:** check model switching, no-execution reference list/card/back/search, source/variant warning, offline, rotation, accessibility and negative scenarios on the final manual QA device. No production release.
4. **No false stage closure:** 11/15 main stages fully accepted, group 1 remains PARTIAL, Issue #4 OPEN.

**Next scheduled position:** unresolved remediation **group 2/8**, diagnostic reference visibility vs locomotive-crew action, contraindications, stop points and safe source/profile gates; prioritize independent Kotlin/Compose changes, not another registry-only pass. Keep group 1 backlog open and return later. Original automation chat publication cannot be guaranteed from this run; Issue #4 and this file are durable checkpoints.
