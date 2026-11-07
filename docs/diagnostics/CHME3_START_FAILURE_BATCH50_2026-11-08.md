# ЧМЭ3, пакет 50: CHME3-DIAG-001 «Дизель не запускается» (08.11.2026)

**Технический результат проверен на исходном коммите; итоговая документационная правка ожидает повторного CI.** Начальный HEAD `058fa9aaa29500b60cd43b7d23bdecd9fd7b52de`, предыдущий [CI №42421708838](https://github.com/DomEnota-hub/Beta/actions/runs/42421708838) completed/success. В этом цикле один сложный сценарий, не объединять с CHME3-DIAG-002 «Дизель запускается и глохнет».

**Донор:** `Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`, `docs/locomotives/chme3/diagnostics_powerplant_pass3.json#/scenarios/0`, blob `63988703bb795e82f40335a756b8b9bd3cad8e0a`. Сверены ID, название, профили ЧМЭ3/ЧМЭ3Т/ЧМЭ3Э, риск `NORMAL_DIAGNOSTIC`, equipmentIds, evidenceRefs. Canonical pack ID `chme3.diagnostics.chme3-diag-001`; это соответствие ID/названия, **не** эквивалентность графа. Три gzip не распакованы независимо. Донорские исторические гипотезы `MIXED_LEGACY_FIELD` не подтверждают диагноз.

**Источники:** З.Х. Нотик, 2-е изд., Транспорт, **1996**, [§15](https://www.sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/025.htm) дизель, [§38](https://sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/066.htm) регулятор, [§61](https://www.sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/109.htm) электропередача, [§68](https://www.sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/148.htm) пуск ЧМЭ3. [Библиографическая запись](https://dntb-centr.ru/b/424). Исторический учебный материал, не современное РЭ. §68 не распространять автоматически на ЧМЭ3Т/Э.

**Результат авторинга:** SHORT 8 узлов, DETAILED 12, пять раздельных информационных расширений, 15 отрицательных мутаций в `qa/validate_chme3_start_failure_batch50.py`, включены в CI. Различаются отсутствие проворота, проворот без воспламенения, краткое воспламенение, цепь разрешения и альтернативные топливно-регуляторные гипотезы. Только уже имеющиеся наблюдения; UNKNOWN→STOP, запрет нового пуска для диагностики, перемычек, обхода защит, силовых вмешательств. Extended скрыт, чтение предупреждения до конца и отдельное подтверждение обязательны и не дают полномочий. Профили UNKNOWN/BLOCKED, runtimeImport=false.

**Не подтверждено:** действующие заводские РЭ и схемы конкретной машины, современная нормативная применимость, роль, независимая gzip-сверка. Device QA **NOT_RUN / DEFERRED**, критерии внесены в единый реестр. Kotlin/JVM, lint, assembleDebug и APK не считать успешными до завершённого CI этого коммита.

**Следующий цикл после зелёного CI:** отдельный CHME3-DIAG-002 и другие ещё не подготовленные сценарии при наличии источников.

## Проверки

[CI №42425526786](https://github.com/DomEnota-hub/Beta/actions/runs/42425526786) на `755e94beb63b8d7ddbb1d3580edfbfb457429410`: **completed/success**. Пройдены 15 отрицательных мутаций, Kotlin/JVM, Android lint, assembleDebug и APK. В документационной правке уточнено происхождение даты: `updatedAt=2026-10-01` относится к закреплённому донорскому JSON, а не к дате исходных полевых наблюдений. Итоговый HEAD требует самостоятельного зелёного CI. Device QA остаётся NOT_RUN/DEFERRED.
