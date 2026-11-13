# RailBrakeCalculator — post-15 remediation group 3/8: common knowledge, source evidence and safe navigation

**11.11.2026 — PARTIAL / CODE AND CI VERIFIED.** The post-15 group 3 work changed actual Kotlin/Compose behavior. It does not close group 3, Stage 14, Stage 15 or Issue #4. Main stages fully completed remain **11/15 (1–10 and 12)**. Test- donor is read-only at `3176d6ee228f0ed4b78371f45209e10c1c724eff`.

## Scope and implementation

- Beta working branch: `audit/information-block-gaps-20261014`.
- Code/test/CI commit: `f85cae83b7d98e3befd24901082349c066412376`.
- Changed Kotlin: `feature-safety/.../CommonReferenceCatalog.kt`, `CommonReferenceScreen.kt`, plus `CommonReferencePolicyTest.kt`.
- Added actual-APK source/link audit `qa/check_post15_group3_common_navigation.py` and dedicated workflow `.github/workflows/post15-group3-common-navigation.yml`.
- **66 already readable common reference cards** remain available in four sections: knowledge 13, traffic safety 13, occupational safety 22, first aid 18. No new unreviewed action card was promoted.
- **New user-facing search** on all four reference lists, matching title, summary and donor keywords, including abbreviations. It deliberately does **not** index or render hidden, unreviewed first-aid procedural blocks.
- **11 safe donor cross-links** are now traversable between eligible cards in the **same** common section: 3 knowledge links and 8 occupational-safety links. The link resolver requires `COMMON_INTERNAL`, compatible type, eligible CANDIDATE/STANDARD/INFORMATION_ONLY target, common owner and no foreign model/variant; it rejects absent targets and cross-section targets. SOURCE links are represented separately as evidence, not executable navigation.
- **21 source entries** (19 knowledge, 2 first aid) are displayed as title + explicit `sourceStatus` and `provenance` information on each reference card. All 21 currently carry `UNKNOWN`; their presentation says **not confirmed**, not “official/current/approved”. No internal IDs are displayed.
- First-aid source descriptions and summaries remain visible; unreviewed stepwise donor blocks are not presented as actionable algorithms. No source metadata or existing runtime execution gate was promoted/relaxed. Full future permissions audit remains parked.

## CI and tests

At the code SHA **20/20 workflow runs completed SUCCESS (terminal)**, with no failures:
- [Post-15 group 3 common navigation #42954314626](https://github.com/DomEnota-hub/Beta/actions/runs/42954314626): `:feature-safety:testDebugUnitTest`, `:app-shell:testDebugUnitTest`, `:app-shell:lintDebug`, `:app-shell:assembleDebug`, `:app-shell:assembleDebugAndroidTest` — **BUILD SUCCESSFUL in 3m 2s**. AndroidTest APK was compiled, **not executed on device**.
- Actual built APK: `POST15_GROUP3_COMMON_PASS articles=66 sources_unverified=21 safe_internal_links=11 executable=0`.
- Existing gate: `STAGE14_COMMON_REFERENCE_PASS articles=66 firstAid=18 traffic=13 knowledge=13 occupational=22 executable=0`.
- [Stage 14 #42954314533](https://github.com/DomEnota-hub/Beta/actions/runs/42954314533), [Stage 15 integration #42954314299](https://github.com/DomEnota-hub/Beta/actions/runs/42954314299), [Modular bootstrap #42954321883](https://github.com/DomEnota-hub/Beta/actions/runs/42954321883): **SUCCESS**.
- Added three JVM regression tests for synonym search, suppression of hidden procedure text, same-section link isolation, missing/foreign targets and source provenance status. Six `CommonReferencePolicyTest` tests now cover the common reader.

## Focused external source discovery (not normative clearance)

- Ministry of Health order **№220н (03.05.2024)** is available on an official [MChS regional government page](https://55.mchs.gov.ru/deyatelnost/napravleniya-deyatelnosti/dobrovolnaya-pozharnaya-ohrana/normativnye-akty-i-inye-dokumenty-dobrovolchestva-volonterstva-v-oblasti-zashchity-ot-chrezvychaynyh-situaciy-prirodnogo-i-tehnogennogo-haraktera-grazhdanskoy-oborony-pozharnoy-bezopasnosti-i-bezopasnosti-lyudey-na-vodnyh-obektah/prikaz-ministerstva-zdravoohraneniya-rossiyskoy-federacii-ot-3-maya-2024-g-220n-ob-utverzhdenii-poryadka-okazaniya-pervoy-pomoshchi). [MChS first-aid document index](https://psi.mchs.gov.ru/deyatelnost/podgotovka-i-prosveschenie-naseleniya/pervaya-pomoshch-i-psihologicheskaya-podderzhka/normativnye-dokumenty-ob-okazanii-pervoy-pomoshchi) also lists the order.
- Ministry of Health provides [first-aid algorithms](https://minzdrav.gov.ru/special/documents/9801-algoritmy-okazaniya-pervoy-pomoschi), published 12.09.2024. These have **not** yet been mapped step-by-step to the 18 donor first-aid cards.
- Order **№262н (24.05.2024)** is described as effective from 01.09.2024 through 01.09.2030 in [legal text summary](https://www.consultant.ru/document/cons_doc_LAW_477795/013179d818df772793d688735db88002e143f684/); this does **not** prove the exact donor card wording or any later amendment.
- Therefore **no SOURCE entry was automatically marked CURRENT** and no first-aid procedure was published. Full edition/content matching is outstanding.

## Open blockers and exact acceptance criteria

1. **21 source records**: verify exact edition, title, provenance and applicable sections against primary sources; annotate per-source and per-card status. Do not treat the donor's text as legally current merely because a similar official document exists. Owner: source-review.
2. **18 first-aid procedures**: independently cross-check the donor blocks against applicable current first-aid order and official algorithm for each scenario, contraindications, scope and conditions. Only then provide separately labelled, source-backed, non-misleading steps. Owner: first-aid-review.
3. **329 exam questions**: provenance, licensing and redistribution permission are still unresolved; no unauthorized content was copied or activated. Owner: content-rights-review.
4. **Other donor navigation**: only the 11 currently validated same-section links were restored. Verify remaining cross-section and external references individually; avoid untrusted source URLs and foreign-profile navigation. Owner: common-content.
5. **Device acceptance**: run real search, link traversal, back navigation, rotation, offline behavior and accessibility checks on device at final QA. Current Android instrumentation tests only compile. Owner: Android QA.
6. **Safety and applicability**: reference visibility must remain distinct from action authorization. Full comprehensive permissions audit is explicitly parked in `docs/backlog/FUTURE_PERFORMANCE_AND_CREW_ACCESS_AUDIT.md`; do not initiate without a new instruction.

## Next group

Group 3 remains **PARTIAL** and its unresolved items remain in the post-15 backlog. The next scheduled run should work **group 4/8: calculations, VU-45 and securing normative acceptance**, prioritizing Kotlin/Compose and tests with source-bound conditions. After the first 7+1 pass revisit all PARTIAL groups. Do not close Issue #4 or release production; do not modify Test-.


## Second pass (11.11.2026): government source links for first-aid reference cards

**Status: PARTIAL / code committed; CI and APK delivery require terminal verification.** This is group 3/8 only, not an authorization to perform donor procedures. Main stages fully completed remain 11/15. The Test- donor was not modified.

- Code SHA `06baaac74fc35926f1db9bf09d805901a45cc490` (catalog, Compose screen and JUnit).
- All **18 first-aid summaries** now expose links to separately located official government materials: **17** ordinary first-aid cards each have two resources (MChS-hosted Ministry of Health order **220н**, Ministry of Health 2024 first-aid algorithms); the **worker-kit** card has one MChS official explainer that identifies Ministry of Health order **262н**. **35 external resource links** across the 18 cards; none is sourced from untrusted donor URLs.
- Links are shown under a separate **“official materials for independent cross-check”** section with explicit caveats. Existing donor source records remain **UNKNOWN**, and all unreviewed first-aid blocks remain hidden; no action or normative clearance is implied. Offline mode retains local summaries; official links need internet.
- JUnit regression added for exact 17+1 mapping, approved government domains, fake donor URL injection, source requirement and preservation of unknown status. Existing 66 common reference summaries and 11 same-section internal links remain unchanged.
- Verified government discovery pages (not an individual comparison of each donor algorithm): MChS 220н page https://55.mchs.gov.ru/deyatelnost/napravleniya-deyatelnosti/dobrovolnaya-pozharnaya-ohrana/normativnye-akty-i-inye-dokumenty-dobrovolchestva-volonterstva-v-oblasti-zashchity-ot-chrezvychaynyh-situaciy-prirodnogo-i-tehnogennogo-haraktera-grazhdanskoy-oborony-pozharnoy-bezopasnosti-i-bezopasnosti-lyudey-na-vodnyh-obektah/prikaz-ministerstva-zdravoohraneniya-rossiyskoy-federacii-ot-3-maya-2024-g-220n-ob-utverzhdenii-poryadka-okazaniya-pervoy-pomoshchi ; Ministry of Health algorithms https://minzdrav.gov.ru/special/documents/9801-algoritmy-okazaniya-pervoy-pomoschi ; MChS kit explainer https://mchs.gov.ru/deyatelnost/bezopasnost-grazhdan/aptechki-pervoy-pomoshchi .
- **Still required:** step-by-step legal/content verification for all 18 donor first-aid blocks, edition verification of 21 source entries, 329 exam question rights, remaining cross-section links and device UX/behavior tests. Full postponed permissions audit remains parked. Do not close group 3 or Issue #4.
- CI runs triggered on code SHA include dedicated group 3, Stage 14 and Stage 15; terminal results and the Drive Rail APK delivery must be reported separately in Issue #4 after verification. No QA delivery is claimed by this checkpoint.
