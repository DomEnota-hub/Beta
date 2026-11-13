# RailBrakeCalculator — post-15 group 6/8: assistant search and source-marked reference navigation

**11.11.2026. Status: PARTIAL / CI PENDING.** This checkpoint is NOT a claim of a completed group or a released application. Main stages fully complete: **11/15**. Previous groups 1–5 remain PARTIAL. Test- donor `3176d6ee228f0ed4b78371f45209e10c1c724eff` remained read-only.

## User-visible implementation in Beta

Code baseline `cc62941ea180e57d3d8b00fd098fc77b74d7bcb2`; current implementation SHA `c56e85da62feb8f6377f5a678f3739505967814d`.

1. **Common reference search in the Assistant.** A separate read-only search lane projects existing `CommonReferencePolicy` summaries from the three pinned common packs, without installing CANDIDATE entries into the published `ContentRegistry`. Existing visible cards: knowledge **13**, traffic safety **13**, occupational safety **22**, first aid **18**, **66 total**. Search uses donor keywords and the existing assistant query normalizer. An explicit locomotive-specific query cannot silently return a common card as a model-specific result. Fault/scheme/acceptance intents and categories do not promote common references.
2. **Family reference search in the Assistant.** The existing curated `crew-reference/summaries.json` has **84 summary-only entries** (12 each for 2ЭС5К, 3ЭС5К, ЧМЭ3, ЧМЭ3Т, ЧМЭ3Э, ТЭМ2, ТЭМ2У). The Assistant can search these in a separate lane, including explicit requests for a model other than the working locomotive. Before reading a family summary the user must explicitly select a registered execution. This includes separate Ermak МСУД-Н/015 and CHME3T pre/from №6245 profiles. Unknown execution and cross-model matches fail closed. Normalized multiword search matches only visible title and summary, never hidden procedural fields.
3. **Revalidated navigation.** Common hits open the original `CommonReferenceScreen`, re-checking eligible card IDs and showing source/edition uncertainty. Family hits open `FamilyContentScreen` under the selected exact model/execution and re-check the pinned donor SHA, ID and applicability; no working-model switch. These routes do **not** activate diagnostic candidates, acceptance actions or a hidden extended mode.
4. **Honest status text.** Published runtime hits and read-only donor references are visibly distinguished. Unknown/archival source status remains unverified; no blanket ACTIVE promotion. First-aid procedural blocks remain unavailable as executable guidance. No new user action was authorized.

Changed Kotlin/Compose files include `AssistantCommonReferencePolicy.kt`, `AssistantFamilyReferencePolicy.kt`, `AssistantSearchScreen.kt`, `MainActivity.kt`, `CommonReferenceScreen.kt`, `FamilyContentScreen.kt` and `FamilyReferencePreview.kt`. Added JUnit tests for real common packs, model/execution isolation, source/rights-negative cases and multiword search, plus a compiled-only Android UI smoke source.

## Tests and CI: **NOT YET TERMINAL ON FINAL CODE**

- Intermediate SHA `2194a87a` failed `:app-shell:compileDebugUnitTestKotlin` because `Files.readString` was unavailable on the Android test API; fixed at `886b0b502e096e9409d512bc75b1af0ac3d76159` by using `Files.readAllBytes`.
- Intermediate SHA `71e087ac` failed Kotlin compilation because the Assistant UI had newly required parameters before MainActivity was updated. Fixed in later implementation commits.
- Final code SHA `c56e85da62feb8f6377f5a678f3739505967814d` is awaiting terminal GitHub Actions results. Relevant runs: Stage 15 `42975011351`, Stage 9 `42975011465`, Stage 8 `42975011512`, common group 3 `42975011417`. **Do not mark success or upload a new group 6 APK until these pass.** Device instrumentation is reserved for final manual acceptance.

## Verified previous QA delivery, separate from this new code

A previous group-5 DEBUG QA APK was extracted from successful Stage 15 run `42967204519`, artifact `13832111585`; ZIP integrity checked and SHA256 computed. The APK was uploaded to the existing Google Drive `Rail` folder and independently confirmed by Drive metadata:

- File: `RailBrake_Beta_1.2.2-modular-alpha01_post15-group5_debugQA_09264ca8.apk`
- Size: **9,624,201 bytes**
- SHA256: `d60d38f7e151204337283cc6925d50e0394ec122514efba46666f4b086a33575`
- Drive file ID: `1dS51s4D6G446EA26QRqSb_Pvj5o0fQ2k`
- Type: DEBUG QA, **not** a signed upgrade or production release.

This previous APK does NOT contain the group 6 changes.

## Open work / acceptance

- Wait for terminal CI on final group 6 code; fix any failure; inspect actual APK contents, deliver new QA APK to Google Drive `Rail`, verify Drive metadata and APK SHA256.
- Compare remaining donor multi-turn conversation intent/clarification, 55+ speech/diagnostic cases, ranking and source-to-card mapping. Current lanes do not prove full donor 1:1 parity.
- Cross-section/extended-mode links, rights and current editions for common sources, family references and negative runtime behavior need further source-bound review. No mass activation or full future crew-permissions audit in this group.
- On-device navigation and installed upgrade acceptance remain deferred to final manual QA. No production release.
- Group 6 remains **PARTIAL**; after the first 7+1 pass revisit open group 6 issues. **Next independent group: 7/8**, then Sherpa-ONNX as separate group 8/8. Issue #4 stays OPEN.

The source automation chat cannot be written to from this run; the Issue #4 checkpoint and run report are durable records.
