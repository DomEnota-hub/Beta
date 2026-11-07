# Этап 18/51, пакет 29: ER-DIAG-090–092, ТМ поезда (07.11.2026)

**CANDIDATE / RESEARCH_DRAFT_BLOCKED.** Исходный HEAD `d3fabcf233db74c211a33b69e9b4100b00f05f30`, предыдущий [CI №42325076195](https://github.com/DomEnota-hub/Beta/actions/runs/42325076195) completed/success. Разрешённая ветка `audit/information-block-gaps-20261014`; донор Test- @ 3176d6ee228f0ed4b78371f45209e10c1c724eff только для чтения.

| ID | Исходный статус | Различение |
|---|---|---|
| 090 | CURRENT_RULE_CONFIRMED / all_confirmed_profiles | Падение давления ТМ ≠ разрыв рукавов 092, команда ЭПК 089 или ошибка индикации. |
| 091 | CURRENT_RULE_CONFIRMED / brake_395, brake_130_uktol, brake_130_2_uktol | Перезарядка ≠ переходный процесс после отпуска; профиль и вид поезда обязательны. |
| 092 | CURRENT_RULE_CONFIRMED / all_confirmed_profiles | Подтверждённое повреждение/разъединение рукава ≠ только падение ТМ 090, ≠ межсекционная ПМ 079. |

Для каждого SHORT=8, DETAILED=12, пять отдельных информационных расширений, три источниковых сопоставления, исходные 8 полей сохранены. Донор gzip blob c3a22c62db42308eb4b7ee44ff2da02f47686625, проекция pack blob 69945cc0e6c5c316911ffab1489da9dfd3e8ba9a. **Raw gzip для 090–092 независимо не распаковывался.**

## Независимая сверка источников

- [Новые Правила тормозов](https://prg.kz/m/amp/document/39816410/), приложение №65 к протоколу №83 от 25–26.11.2025, введены 01.07.2026; подтверждены дата и структура разделов 3/9/10, но не конкретные пункты, значения, местная редакция и полномочия.
- [2580р](https://internet-law.ru/documents/dop_documents/2/tipov/0/raspo_40323.html) от 12.12.2017: открытая версия содержит изменения №752/р от 25.03.2024. Наличие более поздних изменений и применимая редакция **UNKNOWN**.
- [3508/р](https://meganorm.ru/mega_doc/norm_update_01012026/instrukciya/0/instruktsiya_po_tekhnicheskomu_obsluzhivaniyu_remontu_i.html) от 28.12.2022, доступная редакция 14.01.2025: область технического обслуживания и ремонта; не даёт универсальных полномочий в пути.
- [Учебная схема 3ЭС5К](https://rcit.su/techinfoV8.html) и [архивное РЭ6](https://rcit.su/techinfoV56.html) применяются для различения ТМ/ПМ и аппаратуры, не как современный маршрут действий. Тип №395/№130/№130-2 конкретной машины не подтверждён.

## QA и границы

Все три: CANDIDATE, runtimeImport=false, executable=false, actionAuthorityGranted=false, sourceAuthorityVerified=false, exactInstalledVariantConfirmed=false, substantiveSafetyReviewed=false. Только ранее зафиксированные данные; YES/NO/UNKNOWN, UNKNOWN→STOP, действующий отказ→STOP, профиль UNKNOWN→BLOCKED. Предупреждение HIDDEN до прочтения и подтверждения, не даёт полномочий. Не выполнять разрядку/зарядку, опробование, переключение кранов, соединение/разъединение рукавов или работу под давлением. Нет неподтверждённых норм, уставок и процедур.

`qa/validate_stage18_ermak_brake_batch29.py --negative`: проверка донорских полей, графов, источников, безопасности и отрицательных мутаций. **CI на итоговом HEAD необходим для технического закрытия**, включая Kotlin/JVM, Android lint, assembleDebug и проверку APK. Device QA: NOT_RUN / DEFERRED до тестового APK. Следующий цикл после зелёного CI: 093 КЛУБ-У отдельно от 094 САУТ и 095 ТСКБМ.
