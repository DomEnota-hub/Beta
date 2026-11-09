# Этап 50/51: граница Android runtime, APK и ранние исследовательские сценарии (09.11.2026)

## Фактическая исходная точка
Разрешённая ветка `audit/information-block-gaps-20261014`, исходный HEAD `1cc7d288393589e4d37741f1293bbac0a870f72b`. Два CI этапа 49: [№42591925419](https://github.com/DomEnota-hub/Beta/actions/runs/42591925419) и [№42591925320](https://github.com/DomEnota-hub/Beta/actions/runs/42591925320), `completed/success`. Донор `DomEnota-hub/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` использован **только для чтения**.

## Изменения одного логического этапа
1. **Восемь ранних ВЛ80С ID** сопоставлены по закреплённому source snapshot (103 ID) с отдельными research-файлами: `pantograph-no-rise` (Stage4), `gv-no-close` и `ekg-stuck` (Stage5), `gv-no-open` и `ekg-slow-transition` (Stage6), `compressor-long-run`, `compressor-no-start`, `compressor-pressure` (Stage7). Проверяется точный `originalId`, `scenarioId`, donor SHA, профиль, статус `CANDIDATE`, запреты runtime/action, предупреждения, режимы SHORT/DETAILED и отсутствие ложной device QA. **Это сверка идентичности, а не доказательство эквивалентности графов исходному runtime**. Два Stage5 файла остаются gzip-исследованиями.
2. **ЧМЭ3 `CHME3-DIAG-001`–`012`**: каждому исходному исследовательскому JSON добавлен индивидуальный `deviceQA=DEFERRED_TO_POST_RELEASE_DEVICE_QA`. Другие поля, графы, источники и статусы не менялись. Отсутствие маркера теперь отрицательный критерий отдельного Stage50 QA.
3. **APK research isolation**: `app-shell/build.gradle.kts` сохраняет legacy `content-packs` assets, но через `androidResources.ignoreAssetsPattern` исключает каталоги `authoring`, `migration` и research/candidate файлы. Добавлен отдельный Stage50 QA и проверка фактического ZIP APK в основном Android CI. APK должен содержать старый опубликованный runtime index и все его индексированные пакеты, но **не** research authoring/migration. Текущий legacy executable flow ВЛ80С с 103 сценариями не подменяется и не объявляется новым допуском.
4. **Отрицательные проверки**: подмена source ID, donor SHA, публикации, runtime-флага, action authority, warning gate, device QA и утечка research assets в ZIP должны отклоняться. Новых процедур, перемычек, обходов защит, HV-вмешательств или runtime-адаптеров не добавлено.

## Критерии завершения
- `python3 qa/validate_stage49_cross_family_research.py --negative` без пропущенных индивидуальных device QA маркеров.
- `python3 qa/validate_stage50_runtime_boundary.py --negative`: ранние 8 ID и 12 маркеров, отрицательные мутации, конфигурация исключений APK.
- После `assembleDebug`: `python3 qa/validate_stage50_runtime_boundary.py --negative --apk app-shell/build/outputs/apk/debug/app-shell-debug.apk`. При обнаружении любого `assets/**/authoring/**`, `assets/**/migration/**`, `*.research.json[.gz]`, `*.candidate.json[.gz]` сборка должна провалиться. Все индексированные legacy runtime packs должны остаться.
- Kotlin/JVM, Android lint, `assembleDebug`, APK resources и оба независимых CI должны закончиться `completed/success` на **итоговом HEAD**. До этого **не объявлять этап технически завершённым**.

## Открытые ограничения
Независимая графовая эквивалентность восьми ранних кандидатов и исходных gzip/runtime-графов, актуальные заводские РЭ/ИДМБ, конкретное исполнение и роли, source/role/safety gates, ручная Android-проверка. Никакие кандидаты не получают runtime-активации и эксплуатационного допуска.

## Следующий цикл
После успешного CI: этап 51, итоговый аудит и подготовка тестовой сборки, затем отдельная физическая device QA по единому реестру. Device QA до выпуска APK остаётся `NOT_RUN / DEFERRED`.

**Промежуточный статус документа:** изменения внесены; подтверждение итоговых CI и APK ZIP обязательно до закрытия этапа.
