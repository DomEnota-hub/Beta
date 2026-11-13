# Этап 12/51: пакет 2, тормоза ВЛ80С

Дата 05.11.2026. Ветка `audit/information-block-gaps-20261014`. Базовый HEAD `88d390d1eb223e44818301acaf81b5b64035deb2`. Предыдущий [CI №42011734254](https://github.com/DomEnota-hub/Beta/actions/runs/42011734254): success. Донор `DomEnota-hub/Test-@3176d6ee228f0ed4b78371f45209e10c1c724eff` только читать.

| Исходный ID | Самостоятельная граница | SHORT | DETAILED | Расширения |
|---|---|---:|---:|---:|
| `epk-leak` | EPK_LEAK_NOT_ALSN_ACTIVATION_OR_PIPE_LEAK | 6 | 12 | 5 |
| `equalizing-reservoir-mismatch` | EQUALIZING_RESERVOIR_NOT_PIPE_LEAK_OR_NO_CHARGE | 6 | 12 | 5 |
| `handbrake-not-release` | HAND_BRAKE_MECHANICAL_NOT_KVT_OR_RIGGING | 6 | 12 | 5 |
| `independent-brake-no-apply` | INDEPENDENT_BRAKE_NO_APPLY_NOT_AUTO_OR_HAND_BRAKE | 6 | 12 | 5 |
| `independent-brake-no-release` | INDEPENDENT_BRAKE_NO_RELEASE_NOT_HAND_BRAKE_OR_WHEEL_DRAG | 6 | 12 | 5 |

## Источники и разночтения

Сверены точные ID, заголовки, категория, слой происхождения, профиль `vl80s-general` и число донорских вопросов (3) по `content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json` (blob `1b4b9f175274f4738e6463bd756b9783471e73a2`), происходящему от закреплённого gzip (blob `6ffdfdabf2f467dcdc4958768905f2b675ac0c26`). Буквальные исходные вопросы из gzip **не извлечены**: `donorOriginalQuestions=null`, `originalQuestionTextVerified=false`. Новые вопросы не выдаются за дословные донорские.

Васько Н. М. и др., *Электровоз ВЛ80С*, 1990: https://ru.djvu.online/file/wXVHhRmTUUuqq. Сверены печ. стр. 17 (ручной тормоз), 155–159 (КРМ 395-3, КВТ 254-1), 193–195 (ЭПК, КВТ/РД и ТМ), 376 (ЭПК-150). Источник архивный, не эксплуатационный допуск. Разночтение КВТ: руководство называет 254-1, донор не подтверждает модификацию; установленное исполнение UNKNOWN/BLOCKED. ЭПК-150 в архиве также не доказывает его установку.

*Правила технического обслуживания тормозного оборудования и управления тормозами*, приложение №65 к протоколу №83 от 25–26.11.2025, действуют с 01.07.2026: https://base.garant.ru/413231681/850c9b8f5271cc2c815bc04e52704941/. Проверены статус и разделы 3.1, 3.2, 4; точные современные процедуры и числовые нормы по каждому дефекту **не подтверждены** (`scopeOnly=true`). Исторические нормы и операции не импортированы.

## Структура, QA и безопасность

Каждый SHORT имеет 2 вопроса и 4 терминала (6 узлов), DETAILED 8 вопросов и 4 терминала (12 узлов). Все вопросы относятся только к ранее записанным наблюдениям, `UNKNOWN → STOP`, опасность → STOP, причина не считается доказанной. Для каждого 5 самостоятельных расширений с привязкой к локатору и статусу: три архивных, два о современной области действия. `CANDIDATE`, `runtimeImport=false`, `executable=false`, `sourceAuthorityVerified=false`, `operationsAllowed=[]`, role/source/safety gates `NOT_APPROVED`. Расширенное предупреждение скрыто, требуется прочтение до конца и подтверждение, согласие сбрасывается; разрешения на операции не возникает.

`qa/validate_stage12_brakes_batch2.py`: донорские ID, профили, границы, полная достижимость графов, tri-state, источники расширений, запреты, 185 отрицательных мутаций и уникальность 40 подробных вопросов. Общий CI: Python QA, Kotlin/JVM, Android lint, assembleDebug, проверка APK. **CI нового коммита до завершения не считать PASS**. Device QA: NOT_RUN/DEFERRED.

Следующий цикл: только `uncommanded-braking` и `wheel-dragging`, разные опасные исходные неисправности, затем закрытие этапа 12 после полного CI.
