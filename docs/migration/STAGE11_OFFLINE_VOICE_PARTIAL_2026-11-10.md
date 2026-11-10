# Этап 11/15 — офлайн-голос: проверенный частичный результат (10.11.2026)

**Статус: IN_PROGRESS.** Этап 10/15 завершён; этап 11 не закрыт и этап 12 не начинался.

## Изменения в Android Beta

Кодовый SHA: `daf89094c42c404600c1f2ab583a4b562326e327`.

- `app-shell/AssistantVoiceButton.kt`: push-to-talk в экране «Помощник» с явной кнопкой остановки, ограничением 20 секунд, уничтожением распознавателя при уходе с экрана, обработкой ошибок и запроса RECORD_AUDIO. Нет фонового прослушивания.
- **Только on-device Android SpeechRecognizer** (API 31+), `isOnDeviceRecognitionAvailable` + `createOnDeviceSpeechRecognizer`. Нет fallback к `createSpeechRecognizer` (может обращаться к сети), нет сетевых разрешений, не выполняется скрытая загрузка моделей. Если локального сервиса нет, голос закрыт, текстовый поиск работает.
- Распознанная фраза помещается **только в редактируемое поле**. Пользователь должен проверить её и отдельно нажать «Найти». Дальше действует неизменённый Stage 8–10 parser/index/source/profile/safety gate; никаких автоматических переходов, команд и выполнения инструкций по голосу.
- `assistant-core/AssistantVoicePolicy.kt`: запрет API <31, отсутствие сервиса, отсутствие разрешения, пустые/некорректные/слишком длинные транскрипты (240 символов).
- `AndroidManifest.xml`: RECORD_AUDIO и `queries` для RecognitionService; INTERNET не добавлен.
- `AssistantVoicePolicyTest.kt`: три тестовых группы для офлайн-availability, разрешения и валидации речи.
- `.github/workflows/stage11-assistant-voice.yml`: policy unit tests, lint, AndroidTest compile, Debug APK.

## Проверки

- [Stage 11 CI #42860507091](https://github.com/DomEnota-hub/Beta/actions/runs/42860507091) — **SUCCESS (terminal)** на кодовом SHA: `:assistant-core:test`, `:app-shell:lintDebug`, `:app-shell:assembleDebugAndroidTest`, `:app-shell:assembleDebug`.
- Stage 8/9/10 regression workflows на том же SHA — **SUCCESS**.
- Тесты микрофона и реального распознавания на устройстве **не выполнялись**, согласно договорённости о финальной QA. Доступность русской офлайн-модели зависит от устройства/службы.

## Проверка исходного Sherpa-ONNX и объективные блокеры

- В pinned доноре `Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` имеется `AssistantVoiceInput.kt` с интеграцией `com.k2fsa.sherpa.onnx` и ссылкой Gradle на `libs/sherpa-onnx.aar`, но **ни AAR, ни ONNX-ресурсы Zipformer/Silero в Git tree донора не входят**. В Beta их также нет. Перенос исходника без бинарных ресурсов не соберётся и не обеспечит распознавание.
- Код Sherpa-ONNX распространяется по Apache-2.0: https://github.com/k2-fsa/sherpa-onnx ; Silero VAD по MIT: https://github.com/snakers4/silero-vad . **Лицензия конкретных весов русской Zipformer-модели и право перепаковывать архив не подтверждены**; лицензию библиотеки нельзя автоматически переносить на модель.
- Android API подтверждает `createOnDeviceSpeechRecognizer`/availability с API 31: https://developer.android.com/reference/android/speech/SpeechRecognizer .

## Что нужно для закрытия этапа 11

1. Получить воспроизводимо проверенные Sherpa AAR, конкретную русскую Zipformer int8-модель, Silero VAD, `tokens.txt`, лицензии именно этих артефактов и SHA-256.
2. Включить модели и AAR в воспроизводимую Android-сборку, не нарушая лицензии и ограничений размера, добавить поддержку API 26–30 или документировать обоснованный недопуск.
3. Проверить на устройстве разрешение/отказ, тишину, отмену, 20-секундный таймаут, отсутствие сети, ошибки и произнесённые команды; подтвердить цепочку речь → текст → обычный safety-gated поиск.
4. После терминальных CI и QA отметить этап 11 закрытым. До этого **10/15 подтверждённых этапов**, текущий 11/15 IN_PROGRESS. Этап 12 не начинать.

Донор не менялся; исследовательские диагностические материалы не публиковались.
