# ЧМЭ3, пакет 63: компрессор, давление и тормоза (08.11.2026)

Стартовый HEAD `343015c56a321b76f193721c218d15c381d0b088`, предшествующий CI [№42476641621](https://github.com/DomEnota-hub/Beta/actions/runs/42476641621) completed/success. Только ветка `audit/information-block-gaps-20261014`; донор `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` только читался.

## Пять различных исходных объектов

- **CHME3-DIAG-201** «Компрессор не набирает давление»: `docs/locomotives/chme3/diagnostics_brake_aux_pass3.json#/scenarios/0`, `content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-201-compressor-no-pressure.research.json`; исходные evidenceRefs `CHME3-SRC-SCBIST-PAM, CHME3-SRC-SCBIST-TROUBLE-2020`.
- **CHME3-DIAG-202** «Компрессор не отключается / работает непрерывно»: `docs/locomotives/chme3/diagnostics_brake_aux_pass3.json#/scenarios/1`, `content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-202-compressor-no-unload.research.json`; исходные evidenceRefs `CHME3-SRC-SCBIST-PAM, CHME3-SRC-SCBIST-TROUBLE-2020`.
- **CHME3-DIAG-203** «Давление воздуха быстро падает»: `docs/locomotives/chme3/diagnostics_brake_aux_pass3.json#/scenarios/2`, `content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-203-rapid-air-pressure-loss.research.json`; исходные evidenceRefs `CHME3-SRC-SCBIST-PAM`.
- **CHME3-DIAG-204** «Тормоза не отпускают»: `docs/locomotives/chme3/diagnostics_brake_aux_pass3.json#/scenarios/3`, `content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-204-brakes-not-releasing.research.json`; исходные evidenceRefs `CHME3-SRC-SCBIST-PAM`.
- **CHME3-DIAG-205** «Самопроизвольное торможение / внезапное наполнение ТЦ»: `docs/locomotives/chme3/diagnostics_brake_aux_pass3.json#/scenarios/4`, `content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-205-unexpected-brake-application.research.json`; исходные evidenceRefs `CHME3-SRC-SCBIST-PAM`.

Для всех пяти исходные ID/названия/профили, `BRAKE_SAFETY`, `SAFETY_GATE_REQUIRED`, equipmentIds и evidenceRefs сверены с pinned donor blob `1094688cc2e633fab21b6f989cc902f7a34d19d2`, migration index и `diagnostics-02.pack.json`. Канонический gzip blob `6a6068ad1ea54cb964b65a10ecf5c2425b2276e8` не удалось независимо декодировать через доступный API: **сходство исходных графов не утверждается**, только ID/title/profile.

## Независимые границы и источники

- **201**: отсутствие/медленный набор ГР; отличать отсутствие вращения, недостаточную производительность и утечку, не делать физические проверки.
- **202**: непрерывная работа и разгрузка; прежде отделить недостижение давления (201) от потенциально опасного превышения. Не регулировать регулятор.
- **203**: падение давления; отдельно ГР, ТМ, управление, ТЦ и штатную команду торможения. Не перекрывать арматуру.
- **204**: неотпуск; отдельно восстановление ТМ, остаточное давление ТЦ, вспомогательный тормоз и механическую рычажную передачу. Не начинать движение.
- **205**: некомандное торможение; отдельно ЭПК/safety, разрядку ТМ и локальное наполнение ТЦ. Не сбрасывать/обходить ЭПК.

Историческая техническая основа: З.Х. Нотик, *Тепловозы ЧМЭ3, ЧМЭ3Т, ЧМЭ3Э*, 2-е изд., Транспорт, **1996**, §§14, 55, 58–60 ([содержание](https://raillook.com/materialy/transport/jeleznodorojniy/tyagoviy-podvijnoi-sostav/1996-teplovozy-chme3-chme3t-chme3e-izd-2-z-h-notik/)). Архивная литература не является действующим РЭ. Действующие с **01.07.2026** Правила тормозов: приложение №65 к протоколу 83-го заседания ([документ](https://base.garant.ru/413231681/850c9b8f5271cc2c815bc04e52704941/)); существование и дата проверены, **точные пункты, пороги и применимость к конкретному исполнению не подтверждены**. Старые правила 2014 года не использовать как текущие. Практические `SCBIST-PAM` и подборка 2020 года: `HYPOTHESIS_ONLY`, не разрешение действий.

## Авторинг, тесты и статус

Каждый сценарий: SHORT 8 узлов, DETAILED 12 узлов, **пять независимых EXTENDED_ONLY расширений по четыре узла**. Всего 100 основных узлов, 25 расширений (100 информационных узлов). У каждого YES/NO/UNKNOWN с UNKNOWN→STOP, проверка достижимости, безопасные терминалы и отсутствие причинных диагнозов. В QA `qa/validate_chme3_brake_air_batch63.py` есть сверка pinned source/index/pack, 37 отрицательных мутаций на сценарий, source/role/safety gates и реестр device QA.

Все `CANDIDATE`, `runtimeImport=false`, `executable=false`, `actionAuthorityGranted=false`, `sourceAuthorityVerified=false`, `humanSafetyReviewPassed=false`, `unknownProfile=BLOCKED`. Предупреждение скрыто, требует дочитывания и отдельного подтверждения, не даёт прав на вмешательство. Device QA: **NOT_RUN/DEFERRED** в едином реестре, только после тестового APK.

**CI итогового HEAD:** проверять после публикации коммита. В workflow включён `python3 qa/validate_chme3_brake_air_batch63.py --negative`, дополнительно должны пройти Kotlin/JVM, lint, assembleDebug и проверка ресурсов. До завершения CI не считать пакет технически закрытым.

**Открыто:** заводские РЭ, точный профиль/схема, действующие пороги и пункты Правил, записи приборов, полномочия, независимая распаковка gzip, safety review, финальная физическая QA. Следующий пакет после успешного CI: оставшиеся исходные `CHME3-DIAG-206..208` из того же документа, без дублей.
