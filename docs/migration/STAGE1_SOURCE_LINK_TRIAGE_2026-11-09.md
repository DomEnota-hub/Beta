# Stage 1/15: evidence-gated source-link triage (2026-11-09)

**Status: IN_PROGRESS.** This triage narrows the source-authority workload; it **does not resolve** any unsafe link, certify a source, publish content or close Stage 1. Donor is read-only `Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Target is Beta branch `audit/information-block-gaps-20261014`.

## Concrete findings from pinned source audits

- CHME3/CHME3T/CHME3E: **610 unresolved source/variant/target triples** are concentrated in **19 distinct target IDs**. Of these, **18 IDs have no source-object mapping in the pinned catalog/diagnostic mapping**. The 19th, `CHME3T-EQ-EDB-CONTROL`, has a catalog mapping for **CHME3T only**, but unresolved references also occur under **CHME3** and **CHME3E**. This is an **unverified cross-variant applicability** case, not evidence that the other variants are compatible. A separate scheme ID `CHME3T-SCH-EDB` also appears across all three variants without a pinned source mapping; it remains blocked. **Both** CHME3T-prefixed IDs are explicitly flagged for unverified cross-variant applicability, including when the target has no mapping at all.
- Ermak: **57 distinct unresolved source IDs**, of which **55 SOURCE_GAP IDs account for 542 occurrences**, and **2 AMBIGUOUS_SOURCE_ID values account for 6 occurrences**. `ER-SRC-039` and `ER-SRC-041` are known collisions. Reused raw numbers are not sufficient evidence to choose one publication. The separate `ER-DIAG-136` index gap is still blocked by the original quarantine validator.
- Legacy history: repository code search in `DomEnota-hub/Test-` and `DomEnota-hub/Beta` finds **references** to `HistoryRepository` in `BrakeCalculatorApp.kt` but **no implementation** of that class. A commit-history query for the expected donor path returned no commits. The exact storage format remains unverified; do not infer it from similarly named classes in unrelated projects.

## New machine-checkable disposition

`docs/migration/stage1-source-link-triage.json` is a **non-runtime** evidence ledger with one entry for each of the 19 CHME3 target IDs and 57 Ermak source IDs. Each entry includes reference/occurrence count, variant or registry-key context, explicit quarantine state, runtimeImport=false and the evidence required to revisit the disposition. CHME3 variant applicability must be checked independently for each variant.

`qa/validate_stage1_source_link_triage.py` compares **every ledger entry** against the existing pinned source-audit JSONs, rejects missing/duplicated IDs, count drift, fabricated mappings, silent variant changes, unreviewed publication and incorrect evidence requirements. Its regression suite `qa/test_stage1_source_link_triage.py` has **12 tests**; CI `.github/workflows/stage1-source-link-triage.yml` also runs the existing quarantine gate.

**Important:** 610 unresolved triples have **not** been fixed; 542 + 6 Ermak occurrences have **not** acquired authority. The ledger is a precise, enforceable work queue. It cannot itself serve as a source citation or authorize a diagnostic action.

## Next evidence-backed work

1. Locate original manufacturer scheme/equipment documents for the 19 CHME3 targets, verify series and modification applicability, then resolve *individual* triples only with document locator and test evidence. Prioritize `CHME3T-EQ-EDB-CONTROL` and `CHME3T-SCH-EDB` cross-variant risks.
2. Recover the original numbered Ermak source registry or verified publications for the 55 missing IDs; for `ER-SRC-039` and `ER-SRC-041`, preserve distinct publication identities until disambiguated with primary evidence. Verify `ER-DIAG-136` separately.
3. Obtain authoritative history storage implementation/schema before changing `HistoryStorageMigrationGate.legacyFormatVerified`; do not borrow the unrelated MediaLoader history schema.
4. Keep 329 exam questions as a verified, **not published** source corpus until a safe candidate target and licensing/source authority are established. Preserve encrypted plaintext boundaries.
5. Continue source-authority verification and the remaining stage-1 gaps. Stage 2 begins only after Stage 1's evidence gates are satisfied.

No Android UI, calculator, assistant, runtime index or user-visible content was modified in this work.

## CI checkpoint (HEAD `54bec6e7d53aa312e8dd9e63600845f4274b9193`)

- [Source-link triage #42695727411](https://github.com/DomEnota-hub/Beta/actions/runs/42695727411): **SUCCESS (terminal)**; 12 regression tests, all 19 CHME3 target groups, 57 Ermak IDs, original quarantine validator.
- [Original source quarantine #42695727268](https://github.com/DomEnota-hub/Beta/actions/runs/42695727268): **SUCCESS (terminal)**.
- [Full Modular architecture bootstrap #42695727974](https://github.com/DomEnota-hub/Beta/actions/runs/42695727974): **SUCCESS (terminal)**; Kotlin tests, Android lint, assembleDebug and APK checks. This verifies the audit changes did not break the current slice; it does not establish Android feature parity.

**Remaining blockers:** authoritative sources for CHME3/Ermak links, cross-variant EDB applicability, original history storage schema, and safe target/licensing review for the 329 exam questions. No source links have been promoted. **Next operation:** obtain source evidence for the two CHME3T EDB cross-variant IDs and separately reconcile the 55 missing Ermak source IDs. The present document is a checkpoint, not a completed Stage 1.

## Дополнение 10.11.2026: первичные локаторы ЧМЭ3Т ЭДТ, без снятия карантина

Для двух приоритетных целей `CHME3T-EQ-EDB-CONTROL` и `CHME3T-SCH-EDB` найдены и просмотрены **два независимых исторических источника**:

1. З. Х. Нотик, «Тепловоз ЧМЭ3Т: особенности электрической схемы», журнал «Электрическая и тепловозная тяга», № 3, 1989, с. 21–25, раздел «Электрическое торможение», рис. 14 «Цепи управления тормозными контакторами»: https://www.booksite.ru/tyaga/1989/1989_3.pdf . Это техническая публикация своего времени, **не** действующее заводское РЭ.
2. ОАО «РЖД», «Руководство по техническому обслуживанию и текущему ремонту тепловозов ЧМЭ3», ЧМЭ3 ИО, утверждено 31.12.2004: https://y-pad.tv/wp-content/uploads/2021/11/Rukovodstvo_TO_TR_CHME3.pdf . П. 3.3.4 (с. 56) отдельно выделяет оборудование реостатного тормоза **ЧМЭ3Т**, п. 3.3.5 (с. 57) рассматривает электронное оборудование **ЧМЭ3Т и ЧМЭ3Э**, п. 7.3.7 (с. 79) отдельно ссылается на работы по ЭДТ ЧМЭ3Т. Это документ по ТО/ТР, **не инструкция на ремонт для локомотивной бригады**. Наличие скана редакции 2004 года **не доказывает актуальность текста с изменениями на 2026 год**.

Создан `docs/migration/chme3t-edb-historical-evidence.candidate.json`, где зафиксированы оба источника и **3 проверяемых исходных объекта** в двух сохранённых документах донора. `qa/validate_chme3t_edb_evidence.py` и `qa/test_chme3t_edb_evidence.py` сверяют идентификаторы, точные JSON pointers и SHA-256 объектов, применимость только `ЧМЭ3Т`, **8** несовместимых ссылок `ЧМЭ3/ЧМЭ3Э` и неизменность запрета публикации. Проверки включены в `.github/workflows/stage1-source-link-triage.yml`.

**Результат:** историческое наличие цепей и оборудования ЭДТ на ЧМЭ3Т подтверждено на уровне источников, но `CHME3T-SCH-EDB` и `CHME3T-EQ-EDB-CONTROL` **не объявлены каноническими runtime-ссылками**. Остаток **610/610** неразрешённых source triples ЧМЭ3, включая 8 cross-variant конфликтов; 548 вхождений «Ермака» не менялись. Необходимо отдельно установить текущую редакцию технической документации, заводскую схему, исполнение конкретного тепловоза и применимость оборудования. Никаких ремонтных действий в приложение не добавлено.

