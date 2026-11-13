# RailBrake Beta — post-15 group 3/8, third pass: independently reviewed adult first aid

**11.11.2026. Status: IN_PROGRESS / DEVICE_QA_PENDING; 20/20 CI terminal SUCCESS.** Main migration stages remain **11/15**. Donor Test- pinned at `3176d6ee228f0ed4b78371f45209e10c1c724eff` was READ-ONLY.

## User-facing code result

Code SHA: `cf7978e7595197f65b99d7d5de2e923286cd8bef`.

- `feature-safety/.../CommonReferenceCatalog.kt`: introduced a separate `CommonReferenceReviewedAid` projection containing independently reviewed, source-bound guidance for **two** cards: `common.first-aid.unconscious` and `common.first-aid.cpr`. The 16 other first-aid cards remain summary-only; donor `blocks` are **never** projected. Source status for the original donor remains `UNKNOWN`.
- `CommonReferenceScreen.kt`: the two cards now show six real numbered steps each, a precise adult-only scope warning and a clickable Ministry of Health source. This is working Compose content, not a mere link or Markdown note.
- `CommonReferencePolicyTest.kt`: new regression covers exactly 2/18 reviewed cards, 16 still hidden, source binding, invalid/missing source rejection, no donor procedure projection and no source-status promotion. Existing 66 common reference summaries and 35 external links remain available.

**Verification matrix (each item is a separate claim; statuses apply only to the new UI steps, not the donor pack):**

| Card / step | Status | Source and precise scope |
|---|---|---|
| Unconscious #1: scene safety | ПОДТВЕРЖДЕНО | Order 220n, annex 2, §1 |
| Unconscious #2: severe external bleeding | ПОДТВЕРЖДЕНО | Order 220n, annex 2, §2 |
| Unconscious #3: consciousness, airway, breathing ≤10 sec | ПОДТВЕРЖДЕНО | Order 220n, annex 2, §3; Ministry poster on absence of consciousness |
| Unconscious #4: recovery position or airway support if impossible | ПОДТВЕРЖДЕНО | Order 220n, annex 2, §4.2 |
| Unconscious #5: emergency call and breathing monitoring | ПОДТВЕРЖДЕНО | Order 220n, annex 2, §§4.2, 9 |
| Unconscious #6: no normal breathing → CPR | ПОДТВЕРЖДЕНО | Order 220n, annex 2, §4.1; Ministry universal algorithm |
| CPR #1: absent consciousness/normal breathing; agonal breaths | ПОДТВЕРЖДЕНО | Order 220n, annex 2, §§3–4; MChS VGSCh commander manual, §15.2 |
| CPR #2: emergency call and AED | ПОДТВЕРЖДЕНО | Order 220n, annex 2, §4.1 |
| CPR #3: adult chest compressions 100–120/min, 5–6 cm | ПОДТВЕРЖДЕНО | Ministry first-aid poster on cardiac arrest (adult CPR) |
| CPR #4: trained rescue breaths 30:2 or compression-only | ПОДТВЕРЖДЕНО | Ministry adult CPR poster (30:2); American Red Cross hands-only adult CPR guidance for untrained rescuers; not a pediatric protocol |
| CPR #5: AED voice instructions | ПОДТВЕРЖДЕНО | Order 220n, annex 2, §4.1; Ministry CPR poster |
| CPR #6: continue until signs of life, handover, exhaustion or danger | ПОДТВЕРЖДЕНО | Ministry CPR poster; safety condition of Order 220n, §4 |

**Primary sources and edition evidence:**
- Ministry of Health order №220н dated 03.05.2024, in force from 01.09.2024; annex 2: https://www.consultant.ru/document/cons_doc_LAW_477698/b3bff558c42175d685ba919d095586a664ff2f7d/
- Ministry of Health official first-aid materials and posters, page **updated 05.03.2026**: https://minzdrav.gov.ru/special/pervaya-pomosch (including posters "Универсальный алгоритм" and "При отсутствии сознания, остановке дыхания и кровообращения")
- American Red Cross, hands-only adult CPR when not trained in rescue breaths: https://www.redcross.org/take-a-class/cpr/performing-cpr/hands-only-cpr
- MChS VGSCh §15.2 on agonal breathing: https://vgsch.organizations.mchs.gov.ru/uploads/resource/2023-01-19/spravochnik-komandira-otdeleniya-vgsch_16741234351189053200.pdf

**Actively sought contradiction, still blocked:** donor `common.first-aid.poisoning` says Order 220n allows emesis "only for poisonous, not caustic substances." **ОПРОВЕРГНУТО as an attribution to the order**: annex 2 §6.2 has no such qualifier. However this is NOT a clearance to induce vomiting: NHS and Poison Control warn against unsupervised induced vomiting, and older MChS pages conflict. The entire donor poisoning procedure remains hidden and **ТРЕБУЕТ ПРОВЕРКИ** for a safely scoped replacement; do not automatically copy or publish it. Sources: https://www.nhs.uk/conditions/Poisoning/ ; https://www.poison.org/first-aid-for-poisonings ; https://mchs.gov.ru/deyatelnost/bezopasnost-grazhdan/otravleniya_0 .

## CI and actual QA APK

Exact code SHA `cf7978e7`: **20/20 GitHub Actions terminal SUCCESS**.
- Group 3 tests, lint and APK: https://github.com/DomEnota-hub/Beta/actions/runs/43079067644
- Stage 14: https://github.com/DomEnota-hub/Beta/actions/runs/43079067550
- Stage 15: https://github.com/DomEnota-hub/Beta/actions/runs/43079067496
- Modular/Stage 51: https://github.com/DomEnota-hub/Beta/actions/runs/43079080636

Two **unique Debug/QA APKs** uploaded to Google Drive **Rail** (folder `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`). ZIP and APK integrity PASS; Google Drive metadata confirms parent and size; **both APKs were re-downloaded byte-for-byte and SHA256 verified**.
- Stage 15: https://drive.google.com/file/d/17R4Qqn16571vskVehwV-ZRd-Lynxxqw6/view ; **9,667,341 bytes**; SHA256 `e62ebf2aae46e13fe5333d06753aa423bb6dea451ed3fff743015d7e5dc6835a`; artifact `13884615124`.
- Stage 51: https://drive.google.com/file/d/1BoEcx4sz8ihU95yzDhkm_n6w4Y0opfse/view ; **9,667,273 bytes**; SHA256 `0a44c66fb864d1e193020510aeffefd9b52c75b4e1cc69d8e8bb6e3eab140697`; artifact `13884315651`.

No device instrumentation was executed; AndroidTest compilation is not device testing. No production release, no new locomotive diagnostic graphs or crew actions.

## Remaining and exact resume

**Group 3 IN_PROGRESS / DEVICE_QA_PENDING:** 2/18 first-aid cards have source-reviewed adult UI steps; **16/18** still need independent point-by-point verification and content integration, including poisoning conflict; **21** donor source records still UNKNOWN; **329** exam questions remain rights-blocked; additional links and final device QA pending. Keep complete third-party permissions audit PARKED.

**Next scheduled group: 4/8, third pass**, calculations / VU-45 / securing; start from the latest group-4 checkpoint and choose one real Kotlin/Compose/data regression with source-bound tests. Do not rerun completed group-3 research without new evidence. Issue #4 remains OPEN.
