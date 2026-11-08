# ЧМЭ3, пакет 66: реверсор, направление, реле, АКБ (08.11.2026)

Исходный HEAD `27b29bf582dbde7d5fa3f4ec15a39b6ffb5f1b23`, предыдущий CI [№42490165084](https://github.com/DomEnota-hub/Beta/actions/runs/42490165084) completed/success. Только ветка `audit/information-block-gaps-20261014`; донор `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` исключительно читался.

- `CHME3-DIAG-304` «Реверсор не переводится»: SHORT 8, DETAILED 12, пять отдельных расширений; границы 305, 207, 109.
- `CHME3-DIAG-305` «Тепловоз движется только в одном направлении»: SHORT 8, DETAILED 12, пять отдельных расширений; границы 304, 104, 109.
- `CHME3-DIAG-306` «Контакторы или реле дребезжат / самопроизвольно отпадают»: SHORT 8, DETAILED 12, пять отдельных расширений; границы 102, 107, 307.
- `CHME3-DIAG-307` «Аккумуляторная батарея проседает при пуске»: SHORT 8, DETAILED 12, пять отдельных расширений; границы 106, 107, 108.

Донор: `docs/locomotives/chme3/diagnostics_extended_pass3.json`, blob `9fa23a5c9e3da49fb025fb55245227314f6020da`, pointers `/scenarios/3..6`; canonical `content-packs/diesel/chme3-family/diagnostics/recommended/diagnostics-02.pack.json`. Совпадение ID/названия/профиля, не графов; gzip blob `6a6068ad1ea54cb964b65a10ecf5c2425b2276e8` независимо не декодирован. Точные riskClass/actionAuthority/evidenceStatus/evidenceRefs/equipmentIds сохранены.

Исторический источник: З.Х. Нотик, 1996, [§65](https://www.sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/123.htm) реверсор PZ-702 и разные ранние/поздние блок-контакты; [§67](https://sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/146.htm) отличия ЧМЭ3Т/Э; [§68](https://www.sinref.ru/000_uchebniki/05300_transport_jd_teplovozi/170_teplovozi_chme3_chme3t_chme3e_izdanie2_notik_1996/148.htm) питание управления и пуск. Номера контактов, токи и действия не перенесены как нормы. Местные/практические источники HYPOTHESIS_ONLY.

Все сценарии `CANDIDATE`, `runtimeImport=false`, `executable=false`, `unknownProfile=BLOCKED`; source/role/safety gates закрыты. Только ранее полученные наблюдения, UNKNOWN→STOP, опасность→STOP; без новых переключений, движения, пусков, измерений, перемычек и обходов защит. Расширения скрыты до полного чтения предупреждения и отдельного подтверждения, которое не даёт полномочий. Device QA NOT_RUN/DEFERRED.

CI: `python3 qa/validate_chme3_extended_electrical_batch66.py --negative` (40 отрицательных мутаций на сценарий, 160 всего), Kotlin/JVM, Android lint, assembleDebug и APK ресурсы считать PASS только после успешного CI итогового HEAD. До этого пакет НЕ завершён.

Открыто: действующее РЭ, точная модернизация, независимое gzip-сравнение, реальные штатные записи, роли/safety gates и физический Android QA. Следующий цикл после зелёного CI: CHME3-DIAG-308 и следующие ещё не обработанные ID.
