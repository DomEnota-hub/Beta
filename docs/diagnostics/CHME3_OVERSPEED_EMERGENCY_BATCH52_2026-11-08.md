# ЧМЭ3, пакет 52: CHME3-DIAG-003 «Дизель идёт в разнос / срабатывает предельный регулятор» (08.11.2026)

## Live checkpoint и исходная идентичность

Перед работой ветка `audit/information-block-gaps-20261014` имела HEAD `ff8128b01f1996493e99b217f3a757e4e7ba9335`, workflow [№42430089893](https://github.com/DomEnota-hub/Beta/actions/runs/42430089893) был **completed/success**. Выполнен один сложный аварийный сценарий, не фиктивный пакет из пяти.

Донор **только читать**: `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Документ `docs/locomotives/chme3/diagnostics_powerplant_pass3.json#/scenarios/2`, Git blob `63988703bb795e82f40335a756b8b9bd3cad8e0a`. Исходные поля: `CHME3-DIAG-003`, `EMERGENCY_STOP`, `SAFETY_GATE_REQUIRED`, `LEGACY_CAUSE_MODEL_PRIMARY_ACTION_PENDING`, `CHME3-EQ-DIESEL/GOVERNOR/OVERSPEED-GOV/INJECTION-PUMP`, `CHME3-SRC-SCBIST-PAM` и `CHME3-SRC-996R-CURRENT-INDEX`, три исходных профиля ЧМЭ3/Т/Э. Canonical `chme3.diagnostics.chme3-diag-003` в `diagnostics-01.pack.json`, исходный gzip Git blob `6a6068ad1ea54cb964b65a10ecf5c2425b2276e8`. Сверка с закреплённой проекцией не является независимой распаковкой gzip и не подтверждает эквивалентность графов.

**Важная граница:** исходный legacy pack содержит `emergency_action`. Исследовательский кандидат **не импортирует** этот узел, не переиспользует текст аварийной операции и не изменяет исходный pack. Runtime выключен. Для публикации любого действия нужны отдельно проверенные актуальный пункт, исполнение, роль и safety gate.

## Источники и расхождения

- З.Х. Нотик, *Тепловозы ЧМЭ3, ЧМЭ3Т, ЧМЭ3Э*, 2-е изд., «Транспорт», **1996**: [§39 «Предельный регулятор»](https://sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/068.htm), [§38 «Объединённый регулятор»](https://sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/065.htm), [§38 «Различия ЧМЭ3Т/Э»](https://sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/067.htm). §39 описывает историческую уставку; её значение **не переносить** в действующие нормы или вопросы графа. §38 отмечает различия конструкций регулятора ЧМЭ3Т/Э.
- Указатель `CHME3-SRC-996R-CURRENT-INDEX` **не** содержит проверенного точного аварийного пункта. Публично обнаружена [редакция №996/р с изменением №592/р от 05.03.2024](https://urizdat.ru/books/zheleznodorozhnyy-transport/lokomotivy-i-lokomotivnoe-hozyaystvo-ct-ctr/perechen-deystviy-lokomotivnyh-brigad-po-vyyavleniyu-i-ustraneniyu-neispravnostey-na-lokomotivah-pri-poezdnoy-i-manevrovoy-rabote-utverzhden-rasporyazheniem-oao-rzhd-ot-12-04-2022-996-r-v-redakcii-rasporyazheniya-oao-rzhd-ot-05-03-2024-592-r.html); её наличие не доказывает редакцию на 08.11.2026 и не раскрывает полномочия по данному событию.
- `CHME3-SRC-SCBIST-PAM`: закреплённая полевая практика, первичный материал и дата не перепроверены. Только гипотеза.

## Авторинг и отрицательные gates

`content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-003-overspeed-emergency.research.json`: SHORT **8** узлов, DETAILED **12**, пять независимых информационных расширений (активное событие, предельный регулятор, объединённый регулятор, отличия исполнений, действующий порядок). Полный обход, YES/NO/UNKNOWN; UNKNOWN→STOP. При активной/не исключённой аварии → STOP без процедуры. Границы с CHME3-DIAG-002/004/005 сохранены. Нет операций, испытаний, регулировок, повторных пусков, сбросов, вмешательств в топливный привод. `CANDIDATE`, `runtimeImport=false`, `executable=false`, `actionAuthorityGranted=false`, `sourceAuthorityVerified=false`, `humanSafetyReviewPassed=false`, `emergencyActionAuthorized=false`. `confirmedVariant=null`, `unknownProfile=BLOCKED`.

`qa/validate_chme3_overspeed_emergency_batch52.py --negative`: строгая сверка идентичности, riskClass, evidenceRefs, профилей, графов, расширений, emergency gates и **30** отрицательных мутаций. Подключено к `.github/workflows/modular-bootstrap.yml`. Физический Android **NOT_RUN / DEFERRED**, критерии внесены в единый реестр.

## Статус и следующий шаг

Состояние: **CANDIDATE, не опубликован, runtime запрещён; source/role/profile/safety gates BLOCKED**. Актуальная заводская схема, конкретная машина, действующий аварийный пункт и роль не подтверждены. Kotlin/JVM, lint, assembleDebug и workflow фиксировать как пройденные **только после зелёного CI на итоговом HEAD**; этот документ не заменяет проверку.

Следующий пакет после завершённого зелёного CI: независимо рассмотреть CHME3-DIAG-004 «Дизель не набирает обороты по позициям» и соседние безопасно отделимые сценарии; не наследовать аварийные действия из 003.
