# ЧМЭ3, пакет 60: поездные контакторы и ослабление возбуждения (08.11.2026)

Предыдущий HEAD `2b5a39f1e004ad05b0365a987065867b78343606`; предшествующий CI [№42463792522](https://github.com/DomEnota-hub/Beta/actions/runs/42463792522) completed/success, проверено до авторинга. Рабочая ветка только `audit/information-block-gaps-20261014`; донор `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` только читался.

## Точные исходные идентичности

- **CHME3-DIAG-104**, «Не включается один из поездных контакторов»: `docs/locomotives/chme3/diagnostics_electrical_control_pass3.json#/scenarios/3`, `chme3.diagnostics.chme3-diag-104`, risk `ELEVATED_ELECTRICAL`, evidence `OFFICIAL_INDEX_PLUS_LEGACY_LOGIC`.
- **CHME3-DIAG-105**, «Не происходит ослабление возбуждения тяговых электродвигателей»: `#/scenarios/4`, `chme3.diagnostics.chme3-diag-105`, risk `ELEVATED_ELECTRICAL`, evidence `996R_SECONDARY_PLUS_LOCAL_LEGACY`.

Git blob донорского JSON `41d241cb0b58e5657ef0d6210e7b272d44df52d0`; ID, title, equipmentIds, evidenceRefs, evidenceStatus, riskClass, actionAuthority, possibleVariants сверены с каноническим индексом миграции и `diagnostics-01.pack.json`. Ссылка на исходный gzip blob `6a6068ad1ea54cb964b65a10ecf5c2425b2276e8`; **независимой распаковки нет**, равенство графов не заявляется.

## Источниковая сверка и противоречия

- [Нотик, 1996, §61](https://sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/109.htm) описывает три группы ТЭД и КП1–КП3, а также две ступени ослабления возбуждения для ЧМЭ3. Это историческое пособие, не действующее РЭ.
- [§74](https://sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/156.htm) описывает релейное управление переходами ЧМЭ3 (РП1/РП2), [§96](https://sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/191.htm) электронное управление ЧМЭ3Э. Их алгоритмы **не смешаны**; [§67](https://sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/146.htm) отмечает различия модификаций.
- Донорские графы предлагают проверки катушек, силовых ветвей и блокировок. Без текущего РЭ, конкретного профиля, полномочий и safety review это **не разрешённые процедуры**. В исследовательских версиях оставлены только вопросы о **ранее зафиксированных наблюдениях**, STOP и информационные выводы без доказанной причины.
- Вторичный 996/р, официальный индекс без первичного пункта и местные материалы 2007 года не повышены до действующей нормативной базы. Численные пороги и номера контактов из архивного текста не перенесены в процедуры.

## Авторинг и техническая проверка

Два самостоятельных `CANDIDATE`: для каждого SHORT 8 узлов, DETAILED 12 узлов, пять отдельных расширений по четыре узла. Суммарно **40 основных узлов и 10 расширений** (плюс 40 узлов расширений). Отдельный `qa/validate_chme3_traction_batch60.py --negative` проверяет ID, поля донора, графы, источник, reachability, UNKNOWN→STOP, закрытые publication/runtime/role/safety gates и отрицательные мутации каждого сценария. Проверки Kotlin/JVM, lint, assembleDebug и ресурсов APK, а также итоговый CI **считать PASS только после фактического завершения workflow на итоговом HEAD**.

`publicationStatus=CANDIDATE`, `runtimeImport=false`, `executable=false`, `actionAuthorityGranted=false`, `sourceAuthorityVerified=false`, `humanSafetyReviewPassed=false`, неизвестный профиль `BLOCKED`. Расширения скрыты, требуют дочитать предупреждение и подтвердить отдельно; подтверждение не разрешает технических операций. Реестр device QA дополнен; физические проверки **NOT_RUN/DEFERRED**.

Открыто: актуальные заводские РЭ, конкретное исполнение/схема и модернизации, первичный 996/р и официальный индекс, роли, safety review, независимый gzip, финальная device QA. Следующий пакет после зелёного CI: `CHME3-DIAG-106` (пусковая цепь не разбирается), **отдельный аварийный safety gate**, затем `CHME3-DIAG-107` при возможности.
