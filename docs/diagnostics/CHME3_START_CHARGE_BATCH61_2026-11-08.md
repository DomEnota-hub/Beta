# ЧМЭ3, пакет 61: неразобравшаяся цепь пуска и заряд АКБ (08.11.2026)

Начальный HEAD `4d76951d5386b6264051df39dfda93f9166e259e`, предшествующий CI [№42467711708](https://github.com/DomEnota-hub/Beta/actions/runs/42467711708) completed/success. Работа только в ветке `audit/information-block-gaps-20261014`. Донор `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` читался без изменений.

## Сверка независимых исходных сценариев

- **CHME3-DIAG-106**, «После пуска цепь пуска не разбирается»: `docs/locomotives/chme3/diagnostics_electrical_control_pass3.json#/scenarios/5`, `chme3.diagnostics.chme3-diag-106`, `EMERGENCY_ELECTRICAL`, `SAFETY_GATE_REQUIRED`.
- **CHME3-DIAG-107**, «Нет зарядки аккумуляторной батареи»: `#/scenarios/6`, `chme3.diagnostics.chme3-diag-107`, `NORMAL_DIAGNOSTIC`, `TRIAGE_ONLY_NO_REPAIR`.
- **CHME3-DIAG-108**, «Регулятор напряжения работает неустойчиво / большой зарядный ток»: `#/scenarios/7`, `chme3.diagnostics.chme3-diag-108`, `ELEVATED_ELECTRICAL`, `TRIAGE_ONLY_NO_REPAIR`.

Проверены ID, title, profile, riskClass, actionAuthority, evidenceRefs/evidenceStatus, equipmentIds и точные пути по закреплённому JSON blob `41d241cb0b58e5657ef0d6210e7b272d44df52d0`, индексу миграции и `diagnostics-01.pack.json`. Ссылка на gzip blob `6a6068ad1ea54cb964b65a10ecf5c2425b2276e8`; **независимой распаковки нет, равенство графов не заявляется**.

## Источники и границы

- [Нотик 1996 §68](https://www.sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/148.htm): историческая последовательность КД1/КД2 и окончания пуска. Донор содержит упоминание механического разделения контактов. Это **запрещено к переносу в действия**: при продолжающемся/неизвестном пусковом режиме только STOP, отдельный аварийный gate.
- [Нотик 1996 §69](https://www.sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/149.htm): историческое описание возбуждения ВГ и цепи зарядки. Нет зарядки (107) ≠ повышенный/неустойчивый ток (108). Отсутствие тока не доказывает дефект АКБ; большой ток не доказывает дефект регулятора.
- [Нотик 1996 §67](https://www.sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/146.htm): модификации ЧМЭ3Т/ЧМЭ3Э отличаются, в том числе электронным регулированием. Не переносить историческую схему ЧМЭ3 на конкретную машину.
- Донорские SCBIST и местные материалы 2007 года остаются `UNVERIFIED_TRAINING_OR_FIELD`/`LOCAL_LEGACY_UNVERIFIED`; это не действующее РЭ, уставки/номера проводов/процедуры не перенесены.

## Технический авторинг

Три независимых `CANDIDATE`; каждый SHORT 8 узлов, DETAILED 12 узлов и пять расширений по 4 узла. Итого 60 основных узлов, 15 расширений (ещё 60 информационных узлов). Отдельный `qa/validate_chme3_start_charge_batch61.py --negative` проверяет provenance, полную достижимость, UNKNOWN→STOP, запрет технических действий, профиль, source/role/safety gates, аварийный STOP для 106 и отрицательные мутации. Kotlin/JVM, Android lint, `assembleDebug`, APK resources и итоговый CI считать PASS только по завершении запуска на итоговом HEAD.

`publicationStatus=CANDIDATE`, `runtimeImport=false`, `executable=false`, `actionAuthorityGranted=false`, `sourceAuthorityVerified=false`, `humanSafetyReviewPassed=false`, `unknownProfile=BLOCKED`. Расширения скрыты, предупреждение дочитывается и отдельно подтверждается; это не разрешение действий. Device QA добавлена в единый реестр как `NOT_RUN/DEFERRED`.

Открыто: актуальные заводские РЭ, конкретный профиль/схема/модернизация, подтверждённые записи, полномочия и safety review, независимый gzip, финальная физическая QA. Следующий цикл после зелёного CI: `CHME3-DIAG-109` (нет тяги при работающем дизеле) и отдельный профиль-критичный `CHME3-DIAG-110` (ЧМЭ3Т, реостатный тормоз), без объединения сценариев.
