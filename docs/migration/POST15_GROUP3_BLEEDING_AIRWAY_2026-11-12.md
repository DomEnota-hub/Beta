# Group 3 — adult bleeding and airway obstruction, 2026-11-12

Code c885937bc665d097721c72f4f6bd3aef302eb7e9; code+tests c3a204d98103bba1b70e4ad84d837aed71c517c5. CommonReferenceCatalog.kt and CommonReferencePolicyTest.kt changed. Existing Compose renderer now displays six reviewed steps each for bleeding and airway, in addition to unconscious and CPR: 4/18 cards with scoped reviewed guidance, 14 remaining. No new card IDs, no donor status promotion, no donor blocks exposed. Donor blob 09587b2da7f23ac532755fd8aad4ced100d369fa read from Test-, matches Beta pack manifest; compared both topics and nosebleed. Donor unchanged.

## Claim matrix (reviewed UI scope, not donor approval)
Sources checked 2026-11-12:
A: Order 220n 03.05.2024, effective 01.09.2024, annex 2 https://www.consultant.ru/document/cons_doc_LAW_477698/b3bff558c42175d685ba919d095586a664ff2f7d/
B: Ministry materials page updated 05.03.2026, bleeding and airway posters https://minzdrav.gov.ru/special/pervaya-pomosch
C: Red Cross severe bleeding https://www.redcross.org/take-a-class/resources/learn-first-aid/bleeding-life-threatening-external and tourniquet https://www.redcross.org/take-a-class/resources/articles/how-to-apply-a-tourniquet
D: MChS airway guidance https://mchs.gov.ru/deyatelnost/bezopasnost-grazhdan/chelovek-podavilsya-chto-delat_7 and https://29.mchs.gov.ru/deyatelnost/bezopasnost-grazhdan/neprohodimost-dyhatelnyh-putey
E: Red Cross airway guideline, updated 2023 https://guidelines.redcross.org/guidelines-database/foreign-body-airway-obstruction/

| Claim | Status | Basis |
|---|---|---|
| Bleeding 1 safety, PPE without delaying lifesaving aid | ПОДТВЕРЖДЕНО | A §1, C |
| Bleeding 2 emergency call and sustained direct pressure | ПОДТВЕРЖДЕНО | A §§2,9; C |
| Bleeding 3 no direct pressure on protruding object/bone, no extraction, stabilize | ПОДТВЕРЖДЕНО | A §2, C |
| Bleeding 4 pressure dressing, tourniquet for uncontrolled life-threatening limb bleeding/major limb injury | ПОДТВЕРЖДЕНО | A §2, C |
| Bleeding 5 placement 5–7 cm proximal, not joint, tighten, record time, visible, no self-release | ПОДТВЕРЖДЕНО | C tourniquet technique; B bleeding materials |
| Bleeding 6 monitoring, thermal protection, urgent help for suspected internal bleeding | ПОДТВЕРЖДЕНО | A §§5,9; C |
| Airway 1 effective cough: encourage and monitor | ПОДТВЕРЖДЕНО | D partial obstruction |
| Airway 2 severe obstruction: call, lean forward, up to 5 back blows | ПОДТВЕРЖДЕНО | A §§1,9; D, E |
| Airway 3 up to 5 abdominal thrusts if back blows fail | ПОДТВЕРЖДЕНО | D, E |
| Airway 4 alternate; pregnancy/large body habitus chest thrusts instead | ПОДТВЕРЖДЕНО | D, E |
| Airway 5 unconscious: CPR starting with compressions | ПОДТВЕРЖДЕНО | A §4.1, D, E |
| Airway 6 visible object only, no blind sweep; medical evaluation after severe obstruction/thrusts | ПОДТВЕРЖДЕНО | D, E |
| Infant/child technique | НЕ ПРИМЕНИМО | Adult-only projection; no pediatric approval |
| Nosebleed donor 15–20 minute wait before escalation | ТРЕБУЕТ ПРОВЕРКИ | NHS https://www.nhs.uk/conditions/nosebleed/ advises 10–15 min and earlier urgent help for excessive bleeding/head injury/dizziness/dyspnea. Do not publish donor timing as universal. Ice evidence weak. |
| Older MChS four back blows and blanket ventilation warning | ОПРОВЕРГНУТО as current universal guidance | 23.09.2013 https://65.mchs.gov.ru/deyatelnost/press-centr/novosti/3381864 conflicts with D/E and CPR after unconsciousness. |
| Poisoning emesis conflict | ТРЕБУЕТ ПРОВЕРКИ | Prior checkpoint; still hidden. |

Tests added exact four reviewed IDs, 14 unreviewed, contraindications, poisoning/nosebleed remain hidden. Existing source/profile gates unchanged.

## CI / APK
At checkpoint 15/19 workflows terminal SUCCESS on c3a204d9; four in progress: group3 https://github.com/DomEnota-hub/Beta/actions/runs/43291677950 ; Stage14 https://github.com/DomEnota-hub/Beta/actions/runs/43291677792 ; Stage15 https://github.com/DomEnota-hub/Beta/actions/runs/43291678142 ; modular https://github.com/DomEnota-hub/Beta/actions/runs/43291692038 . No terminal Android build or APK delivery claimed. Intermediate c885937b also has running CI; Stage15 43291657189, modular 43291667073; inspect both commits for unique artifacts and deliver to Rail, verify ZIP/APK and Drive metadata/re-download. No artifacts returned yet from these four runs. No device tests or production.

Group3 IN_PROGRESS / CI_PENDING / DEVICE_QA_PENDING. Main stages 11/15. 21 donor source records and 329 exam rights unresolved. Resume: finish CI on both SHAs, fix failures, deliver all unique APKs; then group4 calculations per queue. Next group3 pass: nosebleed source reconciliation, then trauma/seizure, actual UI steps and tests. Issue #4 stays open.
