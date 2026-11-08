# ЧМЭ3, пакет 71: РУ3/ОМ, закрытие вторичного 996/р (08.11.2026)

Начальный HEAD `ad3c3a530f7dac33d0380a4734830e6efe62c0de`, предыдущий CI [№42515424381](https://github.com/DomEnota-hub/Beta/actions/runs/42515424381) completed/success. Ветка `audit/information-block-gaps-20261014`. Донор `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` только читался.

**Единственный оставшийся ID документа** `docs/locomotives/chme3/diagnostics_996r_detail_pass3.json`: `CHME3-DIAG-326` «С 5-й позиции не растут обороты — РУ3 не включается из-за цепи ОМ12/ОМ22/ОМ32», `/scenarios/5`, blob `f29c287c2eae1fb60e0cac61cab098fa8cae3c0f`. Сверены ID, заголовок, три профиля, riskClass `NORMAL_DIAGNOSTIC`, actionAuthority `SOURCE_AND_PROFILE_REQUIRED`, evidenceRefs, equipmentIds с pinned donor index и `diagnostics-03.pack.json`. Canonical `chme3.diagnostics.chme3-diag-326`. Gzip blob `6a6068ad1ea54cb964b65a10ecf5c2425b2276e8` не распакован независимо; графовое равенство не заявлено.

Сценарий отдельно от 004 (общий набор оборотов), 103 (РУ3 из другого источника), 322 (чётные позиции), 323 (РУ5/первая позиция). Разделены архивное отсутствие РУ3 и уже включённое РУ3 при отсутствии роста оборотов. ОМ12/ОМ22/ОМ32 остаются **гипотезой вторичного 996/р**, а не доказанной причиной.

Источник `CHME3-SRC-CDOCKA-996R-CHME3` имеет статус `996R_CONFIRMED_SECONDARY`. Первичный действующий текст 996/р, его пункт/редакция, РЭ/ИДМБ, конкретная схема и модернизация не подтверждены. З. Х. Нотик, *Тепловозы ЧМЭ3, ЧМЭ3Т, ЧМЭ3Э*, Транспорт, 1996, только исторический контекст, не современное эксплуатационное РЭ.

Подготовлены **SHORT 8, DETAILED 12 и пять отдельных EXTENDED_ONLY расширений по четыре узла**. Только прежние наблюдения, без новых пусков, измерений, доступа к аппаратам, нагрузочных испытаний, перемычек или принудительного включения реле. `CANDIDATE`, `runtimeImport=false`, `executable=false`, `actionAuthorityGranted=false`, `sourceAuthorityVerified=false`, `humanSafetyReviewPassed=false`, `unknownProfile=BLOCKED`. UNKNOWN→STOP. Предупреждение требует полного чтения и подтверждения, не дающего права на действия.

QA `qa/validate_chme3_996r_secondary_batch71.py --negative`: донорская идентичность, профиль, источники, графы, границы, безопасность и отрицательные мутации. Общий CI выполняет Kotlin/JVM, Android lint, assembleDebug и APK. **PASS только после завершения CI итогового HEAD.** Device QA в общем реестре **NOT_RUN/DEFERRED**.

После успешного CI исследовательски охвачены все **6/6** исходных ID этого документа. Следующий цикл: самостоятельный блок ЧМЭ3Э, начиная с `CHME3E-DIAG-001` из `docs/locomotives/diesel/chme3-family/chme3e/diagnostics_stage3.json`, после повторной сверки HEAD и оставшихся ID.
