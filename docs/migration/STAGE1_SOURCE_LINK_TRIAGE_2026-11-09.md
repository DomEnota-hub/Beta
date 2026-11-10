# Stage 1/15: evidence-gated source-link triage (2026-11-09)

**Status: IN_PROGRESS.** This triage narrows the source-authority workload; it **does not resolve** any unsafe link, certify a source, publish content or close Stage 1. Donor is read-only `Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Target is Beta branch `audit/information-block-gaps-20261014`.

## Concrete findings from pinned source audits

- CHME3/CHME3T/CHME3E: **610 unresolved source/variant/target triples** are concentrated in **19 distinct target IDs**. Of these, **18 IDs have no source-object mapping in the pinned catalog/diagnostic mapping**. The 19th, `CHME3T-EQ-EDB-CONTROL`, has a catalog mapping for **CHME3T only**, but unresolved references also occur under **CHME3** and **CHME3E**. This is an **unverified cross-variant applicability** case, not evidence that the other variants are compatible. A separate scheme ID `CHME3T-SCH-EDB` also appears across all three variants without a pinned source mapping; it remains blocked. **Both** CHME3T-prefixed IDs are explicitly flagged for unverified cross-variant applicability, including when the target has no mapping at all.
- Ermak: **57 distinct unresolved source IDs**, of which **55 SOURCE_GAP IDs account for 542 occurrences**, and **2 AMBIGUOUS_SOURCE_ID values account for 6 occurrences**. `ER-SRC-039` and `ER-SRC-041` are known collisions. Reused raw numbers are not sufficient evidence to choose one publication. The separate `ER-DIAG-136` index gap is still blocked by the original quarantine validator.
- Legacy history: the pinned donor Git **tree** lacks `HistoryRepository.kt`, but the pinned donor **`RailBrakeCalculator.zip` contains the original implementation**. Verified member Git blob `d95a2ce465e2f09bb96d74b8318f36b16d21afd0` and archive SHA-256 `1b713a42e88e242653f1e44e3b0406ca7c45ee2cbaa458bf272fc648307b9fa6` are recorded in `docs/data-migration/legacy-zip-member-manifest.json` and checked by `qa/validate_legacy_zip_member_manifest.py`. Format observed: SharedPreferences `calculation_history` / StringSet `records`; five `|`-separated fields (timestamp plus four URL-safe Base64 fields), max 30, deduplication by timestamp. **This resolves the source-format discovery gap, NOT the migration implementation or its safety gate.** Draft PR #2 contains only a read-only codec.

## New machine-checkable disposition

`docs/migration/stage1-source-link-triage.json` is a **non-runtime** evidence ledger with one entry for each of the 19 CHME3 target IDs and 57 Ermak source IDs. Each entry includes reference/occurrence count, variant or registry-key context, explicit quarantine state, runtimeImport=false and the evidence required to revisit the disposition. CHME3 variant applicability must be checked independently for each variant.

`qa/validate_stage1_source_link_triage.py` compares **every ledger entry** against the existing pinned source-audit JSONs, rejects missing/duplicated IDs, count drift, fabricated mappings, silent variant changes, unreviewed publication and incorrect evidence requirements. Its regression suite `qa/test_stage1_source_link_triage.py` has **12 tests**; CI `.github/workflows/stage1-source-link-triage.yml` also runs the existing quarantine gate.

**Important:** 610 unresolved triples have **not** been fixed; 542 + 6 Ermak occurrences have **not** acquired authority. The ledger is a precise, enforceable work queue. It cannot itself serve as a source citation or authorize a diagnostic action.

## Next evidence-backed work

1. Locate original manufacturer scheme/equipment documents for the 19 CHME3 targets, verify series and modification applicability, then resolve *individual* triples only with document locator and test evidence. Prioritize `CHME3T-EQ-EDB-CONTROL` and `CHME3T-SCH-EDB` cross-variant risks.
2. Recover the original numbered Ermak source registry or verified publications for the 55 missing IDs; for `ER-SRC-039` and `ER-SRC-041`, preserve distinct publication identities until disambiguated with primary evidence. Verify `ER-DIAG-136` separately.
3. Use the already verified ZIP-backed `HistoryRepository.kt` schema and draft PR #2 as the source for stage-7 migration; keep `HistoryStorageMigrationGate.legacyFormatVerified=false` until Android storage, backup/recovery, collision/malformed handling and signed upgrade tests are implemented.
4. Keep 329 exam questions as a verified, **not published** source corpus until a safe candidate target and licensing/source authority are established. Preserve encrypted plaintext boundaries.
5. Continue source-authority verification and the remaining stage-1 gaps. Stage 2 begins only after Stage 1's evidence gates are satisfied.

No Android UI, calculator, assistant, runtime index or user-visible content was modified in this work.

## CI checkpoint (HEAD `54bec6e7d53aa312e8dd9e63600845f4274b9193`)

- [Source-link triage #42695727411](https://github.com/DomEnota-hub/Beta/actions/runs/42695727411): **SUCCESS (terminal)**; 12 regression tests, all 19 CHME3 target groups, 57 Ermak IDs, original quarantine validator.
- [Original source quarantine #42695727268](https://github.com/DomEnota-hub/Beta/actions/runs/42695727268): **SUCCESS (terminal)**.
- [Full Modular architecture bootstrap #42695727974](https://github.com/DomEnota-hub/Beta/actions/runs/42695727974): **SUCCESS (terminal)**; Kotlin tests, Android lint, assembleDebug and APK checks. This verifies the audit changes did not break the current slice; it does not establish Android feature parity.

**Remaining blockers:** authoritative sources for CHME3/Ermak links, cross-variant EDB applicability, **implementation and upgrade verification** of the now-known history schema, and safe target/licensing review for the 329 exam questions. No source links have been promoted. **Next operation:** obtain source evidence for the two CHME3T EDB cross-variant IDs and separately reconcile the 55 missing Ermak source IDs. The present document is a checkpoint, not a completed Stage 1.

## Дополнение 10.11.2026: первичные локаторы ЧМЭ3Т ЭДТ, без снятия карантина

Для двух приоритетных целей `CHME3T-EQ-EDB-CONTROL` и `CHME3T-SCH-EDB` найдены и просмотрены **два независимых исторических источника**:

1. З. Х. Нотик, «Тепловоз ЧМЭ3Т: особенности электрической схемы», журнал «Электрическая и тепловозная тяга», № 3, 1989, с. 21–25, раздел «Электрическое торможение», рис. 14 «Цепи управления тормозными контакторами»: https://www.booksite.ru/tyaga/1989/1989_3.pdf . Это техническая публикация своего времени, **не** действующее заводское РЭ.
2. ОАО «РЖД», «Руководство по техническому обслуживанию и текущему ремонту тепловозов ЧМЭ3», ЧМЭ3 ИО, утверждено 31.12.2004: https://y-pad.tv/wp-content/uploads/2021/11/Rukovodstvo_TO_TR_CHME3.pdf . П. 3.3.4 (с. 56) отдельно выделяет оборудование реостатного тормоза **ЧМЭ3Т**, п. 3.3.5 (с. 57) рассматривает электронное оборудование **ЧМЭ3Т и ЧМЭ3Э**, п. 7.3.7 (с. 79) отдельно ссылается на работы по ЭДТ ЧМЭ3Т. Это документ по ТО/ТР, **не инструкция на ремонт для локомотивной бригады**. Наличие скана редакции 2004 года **не доказывает актуальность текста с изменениями на 2026 год**.

Создан `docs/migration/chme3t-edb-historical-evidence.candidate.json`, где зафиксированы оба источника и **3 проверяемых исходных объекта** в двух сохранённых документах донора. `qa/validate_chme3t_edb_evidence.py` и `qa/test_chme3t_edb_evidence.py` сверяют идентификаторы, точные JSON pointers и SHA-256 объектов, применимость только `ЧМЭ3Т`, **8** несовместимых ссылок `ЧМЭ3/ЧМЭ3Э` и неизменность запрета публикации. Проверки включены в `.github/workflows/stage1-source-link-triage.yml`.

**Результат:** историческое наличие цепей и оборудования ЭДТ на ЧМЭ3Т подтверждено на уровне источников, но `CHME3T-SCH-EDB` и `CHME3T-EQ-EDB-CONTROL` **не объявлены каноническими runtime-ссылками**. Остаток **610/610** неразрешённых source triples ЧМЭ3, включая 8 cross-variant конфликтов; 548 вхождений «Ермака» не менялись. Необходимо отдельно установить текущую редакцию технической документации, заводскую схему, исполнение конкретного тепловоза и применимость оборудования. Никаких ремонтных действий в приложение не добавлено.


## Дополнение 10.11.2026: исправление реального риска упаковки кандидатных схем

При проверке `app-shell/build.gradle.kts` выявлен неполный фильтр `ignoreAssetsPattern`: он исключал `*.candidate.json`, но **не гарантировал исключение** файлов вида `shared-scheme-pairs.candidate.pack.json`, которые лежат в `content-packs/diesel/chme3-family/atlas/` и `content-packs/electric/ermak/atlas/` вне каталогов `migration`/`authoring`. Оба содержат записи `publicationStatus=CANDIDATE`, в том числе схемы, которые не должны автоматически попадать в APK.

Фильтр дополнен универсальными масками `*.candidate.*` и `*.research.*`; `qa/validate_stage50_runtime_boundary.py` теперь проверяет оба исходных кандидатных пакета, запрещает такие имена в **фактическом APK** и содержит отрицательные ZIP-фикстуры для CHME3/Ermak и сжатых research-пакетов. Этот пункт считается проверенным **только после терминального SUCCESS** полного Android workflow на финальном HEAD. Содержимое не переводилось в runtime и не утверждалось как руководство для локомотивной бригады.

**CI finding and corrective relocation (10.11.2026):** The first full APK build on commit `574e922f` **FAILED** the newly strengthened leak check: `assets/diesel/chme3-family/atlas/shared-scheme-pairs.candidate.pack.json` was actually packaged. Therefore the broad `ignoreAssetsPattern` masks alone were **not effective** for this suffix. Both unapproved shared-scheme candidate packs were moved into `atlas/migration/` (the already excluded asset directory) without modifying their bytes; source-mapping/validation scripts were updated. The negative APK fixtures still target the old unsafe locations. Final success requires full Android CI with `--apk` on the relocation commit; until then this is an unverified fix, not a release approval.

**Проверка исправления:** на кодовом HEAD `ff793fca1cc2b98a90ef8bbf0236bc5a42304578` полный [Modular architecture bootstrap #42730193545](https://github.com/DomEnota-hub/Beta/actions/runs/42730193545) завершился **SUCCESS (terminal)**: Kotlin/контрактные тесты, lint, assembleDebug, проверка индексированных ресурсов и Stage 50 `--negative --apk` с запретом `.candidate.`/`.research.` внутри собранного APK. Всего **15/15** workflow на этом HEAD завершились SUCCESS. Перенесённые два пакета сохраняют исходные Git blob SHA (`1457e69560e3f3af0c2bf38da1dbd86c03ff3f75` и `dbc660f058fd5085cc8d625371355ac02ea6f341`); 110 исходных объектов остаются non-runtime. **Это не закрытие этапа 1 и не QA на устройстве.**

## Дополнение 10.11.2026: независимая проверка распределения 610 ссылок по исполнениям и Git blob pin

В исходном реестре Stage 1 были только суммарные количества по 19 целевым ID и наборы исполнений. Это позволяло незаметно перераспределить ссылки между ЧМЭ3/ЧМЭ3Т/ЧМЭ3Э, сохранив общий итог, либо заменить содержимое исходного аудита при неизменном числе ссылок. Теперь `stage1-source-link-triage.json` использует schemaVersion 2, `referenceCountsByVariant` для каждого из 19 ID и закреплённые Git blob SHA обоих исходных аудитов: ЧМЭ3 `0ba6617d293e101eddbe26da9b976eb8e5555bcf`, Ермак `f02a5e84d92552561852e61d1f8d7df0fd3508c5`. Валидатор сверяет реальные байты файлов по Git blob-алгоритму, а не только поля внутри JSON. Добавлены 6 отрицательных регрессионных сценариев (всего 18 для source-link triage): перестановка количества между исполнениями при неизменном общем числе, потеря варианта, подмена каждого из SHA и изменение байтов исходного аудита при неизменных счётчиках, плюс позитивная проверка точных SHA.

Особенно важно для `CHME3T-EQ-EDB-CONTROL`: 2 неразрешённые ссылки относятся к ЧМЭ3 и 2 к ЧМЭ3Э; для `CHME3T-SCH-EDB`: 8 относятся к ЧМЭ3Т, 2 к ЧМЭ3 и 2 к ЧМЭ3Э. Эта статистика **не доказывает применимость**, а лишь сохраняет фактическое распределение и предотвращает скрытую подмену. Любое изменение pinned-аудитов требует осознанного обновления blob SHA, review и повторного CI. Никакие из 610 ссылок ЧМЭ3 или 548 вхождений Ермака не разрешены, `runtimeImport=false`; диагностические действия не опубликованы. **Этап 1 остаётся IN_PROGRESS.**
