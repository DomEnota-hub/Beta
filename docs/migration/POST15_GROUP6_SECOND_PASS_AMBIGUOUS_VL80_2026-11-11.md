# Post-15 group 6/8, second pass: exact model routing in text assistant

Date: 2026-11-11. **Group 6 IN_PROGRESS**; verified code and CI, final device QA deferred. Exactly one group worked. Main 15-stage status remains **11/15** previously verified. Epic #4 OPEN. Test- donor `3176d6ee228f0ed4b78371f45209e10c1c724eff` was not modified.

## User-facing correction

**Bug:** `TextQueryParser` mapped the generic model name `ВЛ80` to the **specific** `ВЛ80С`, without evidence that the user meant that execution. This could route a request for another VL80 series to VL80S content. Separate family and common-reference lanes could also ignore a bare generic model and search the current model or generic knowledge instead.

**Implemented in Beta only:**
- Code SHA [`9b39cbfe269ffd63931b6f6c45d3e9c8e1fa2bfe`](https://github.com/DomEnota-hub/Beta/commit/9b39cbfe269ffd63931b6f6c45d3e9c8e1fa2bfe): removed unsafe `вл80→vl80s` alias; added explicit generic `ВЛ80` / `ВЛ 80` / `VL80` / `VL 80` detection and a clarification response, even when the working model is VL80S. Valid exact `ВЛ80С`, `VL80S` and hyphenated `ВЛ80-С` / `ВЛ-80С` still route to VL80S.
- Code/test SHA [`bcb6ee25326ab938cdd597e9a6a9203995ad8bc5`](https://github.com/DomEnota-hub/Beta/commit/bcb6ee25326ab938cdd597e9a6a9203995ad8bc5): common read-only references and family reference search now reject an ambiguous bare VL80 instead of silently substituting the working family.
- Eight Kotlin source/test files changed across `assistant-core` and `app-shell`. One new JUnit test plus expanded lexical corpus, family-lane and common-lane negative regressions. Existing safety/source/profile/action gates unchanged.
- **0** new published cards, **0** newly approved diagnostic graphs, **0** newly authorized crew actions, **0** source status promotions. This is a concrete wrong-model search/navigation fix, not a claim of full assistant parity.

## CI and APK verification

At final code SHA `bcb6ee25`, **29/29 GitHub Actions runs terminal SUCCESS**:
- [Stage 8 assistant text #43030157870](https://github.com/DomEnota-hub/Beta/actions/runs/43030157870)
- [Stage 9 Compose UI #43030157625](https://github.com/DomEnota-hub/Beta/actions/runs/43030157625)
- [Stage 10 lexical corpus #43030157556](https://github.com/DomEnota-hub/Beta/actions/runs/43030157556)
- [Stage 15 integration #43030157742](https://github.com/DomEnota-hub/Beta/actions/runs/43030157742): JUnit, Android lint, assembleDebug, AndroidTest compilation, negative gates, APK integrity; `BUILD SUCCESSFUL in 3m 46s`, `STAGE15_APK_INTEGRATION_PASS vl80s_core_packs=28 common_references=66 family_previews=84 forbidden_assets=0`. This does **not** establish complete family parity.
- [Modular bootstrap / Stage 51 #43030166403](https://github.com/DomEnota-hub/Beta/actions/runs/43030166403): SUCCESS. Instrumentation **compiled, not executed on a device**.

Both distinct **unapproved Debug/QA** APKs, version `1.2.2-modular-alpha01`, were extracted from CI artifacts, checked as ZIP/APK, delivered as individual APKs (<100 MB) to existing Google Drive `Rail` folder `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`, checked by Drive metadata, and re-downloaded with matching SHA256:

1. Stage 15 [`RailBrake_Beta_1.2.2-modular-alpha01_post15-group6-second-pass_stage15_bcb6ee25.apk`](https://drive.google.com/file/d/1vxjhFe_MKBeNKgtq6oo0Z49V8DKv_iNp/view), **9,660,077 bytes**, SHA256 `44fdb7e64bc93b8e59141e4e10d24ec8dcb87cba49aff17d00ce3881609bccad`, artifact `13860093650` (archive digest `1be98adbf800049e14541f3ae8c5e1eaac471124b2ba9adc64a4b07cb7df7396`).
2. Stage 51 [`RailBrake_Beta_1.2.2-modular-alpha01_post15-group6-second-pass_stage51_bcb6ee25.apk`](https://drive.google.com/file/d/1RH7IW-z4q4u3ikKo1rYVsyiE236FszU8/view), **9,660,141 bytes**, SHA256 `e2af5e0fb7e8cd924c09339c95b28ecad941aeef73d03c5ef532ef69c8e2b733`, artifact `13859059883` (archive digest `fd81b949de39093d00195362fb130cefdf84673bb04274ea8972e672cd147ee0`).

No production release. No phone testing claimed. No mass ACTIVE or broad source permissions audit.

## Remaining group 6 / precise next action

Full parser/index/UI corpus and model-specific content parity, wrong-card scoring under multi-component queries, explicit model/variant applicability, source-link accuracy, and physical-device UX remain OPEN. Family full packs are still missing, so this group is **IN_PROGRESS**, not FUNCTIONAL_DONE. Return to these in the next group-6 pass without repeating already verified bare-VL80 tests.

**Next scheduled position: group 7/8** Android lifecycle/performance/QA: inspect actual assistant runtime model-switch/loading lifecycle and add a targeted regression with Kotlin/Compose and CI. Sherpa remains separate group 8. Do not close Issue #4. Report cannot be posted to the original automation chat by this execution; this checkpoint, Issue #4 and the run result are the durable records.
