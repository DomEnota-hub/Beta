# Этап 7/15 — история расчётов и рабочие записи

Дата реализации: 10.11.2026. Целевая ветка: `audit/information-block-gaps-20261014`.
Donor `Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` только для чтения.

## Фактическая реализация
1. `feature-history/HistoryCodec.kt`: legacy `StringSet` формат из pinned ZIP, точные 5 полей, URL-safe Base64, 30 записей, безопасный v2 reader/writer; независимые модельные рабочие заметки.
2. `app-shell/AndroidHistoryStores.kt`: первая загрузка мигрирует из `calculation_history/records` в отдельный `railbrake_history_v2/records_v2`. Исходный ключ остаётся нетронутым; повреждённый v2 не перезаписывается; clear не вызывает повторный импорт.
3. `app-shell/HistoryAndNotesScreen.kt`: доступный раздел «История и рабочие записи», фильтры по расчётам, просмотр деталей, подтверждение очистки, заметки с привязкой к выбранной модели, подтверждение удаления.
4. `MainActivity.kt`: подключён маршрут `RECORDS`. `Vu45VerificationScreen.kt` и `SecuringScreen.kt` сохраняют только результаты с явным предупреждением об отсутствии эксплуатационного допуска.
5. `qa/validate_legacy_local_state_code_dispositions.py`, `qa/validate_legacy_zip_member_manifest.py`, `donor-kotlin-crosswalk.yml`: актуализированы проверки состояния миграции без изменения донорских хэшей и статусов других локальных хранилищ.

## Контрольные проверки
- `feature-history:test`: Unicode, символ `|`, ошибки Base64, idempotent roundtrip, коллизии timestamp, лимит 30, раздельные модели, запрет молчаливого удаления заметок.
- `app-shell:assembleDebugAndroidTest`: компиляция нового smoke `HistoryNavigationInstrumentationTest`; на устройстве не выполнялся.
- `app-shell:lintDebug` и `app-shell:assembleDebug`: обязательные проверки перед объявлением этапа завершённым.
- CI: [Stage 7 #42826178014](https://github.com/DomEnota-hub/Beta/actions/runs/42826178014) SUCCESS на предшествующем SHA; окончательный код `962bd97c12a89752554b427536d617bc9035789f` требует терминального CI, который фиксируется в Issue #4.

## Не подтверждено
- Подписанное обновление установленного Test- с сохранением SharedPreferences, а также поведение на реальном устройстве.
- Политика локального хранения рабочих заметок для профиля «Рабочий» (требует отдельной сверки).
- Иные донорские хранилища: диагностические сессии, приёмка, recent materials и настройки отображения остаются в отдельном backlog.
- Нормативная применимость результатов расчётов по-прежнему закрыта; история не делает расчёт разрешённым.

**Следующий этап 8/15:** перенос parser/index/engine/runtime/conversation ассистента с подтверждёнными источниками, модельным контекстом и fail-closed.
