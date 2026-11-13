# Этап 11/51: тяговые цепи ВЛ80С, пакет 1

Дата 05.11.2026; база `82548f5224593fe37db1523655df967a828beaa5`; предыдущий CI №41975107784 completed/success. Рабочая ветка `audit/information-block-gaps-20261014`; донор `DomEnota-hub/Test-@3176d6ee228f0ed4b78371f45209e10c1c724eff` только для чтения.

| Исходный ID | Граница | SHORT | DETAILED | Расширения |
|---|---|---:|---:|---:|
| `field-weakening-fault` | FIELD_WEAKENING_NOT_CONFIRMED | 6 | 12 | 5 |
| `reverser-no-confirm` | DIRECTION_COMMAND_FEEDBACK_MISMATCH | 6 | 12 | 5 |
| `traction-current-surge` | TRACTION_CURRENT_SURGE | 6 | 12 | 5 |
| `traction-intermittent` | INTERMITTENT_TRACTION_LOSS | 6 | 12 | 5 |
| `rectifier-overheat` | RECTIFIER_THERMAL_SIGNS | 6 | 12 | 5 |

Все пять исходных ID, заголовков, категорий и описаний сверены с миграционным каталогом 103 сценариев и с `Seed` из закреплённого `DiagnosticExtendedCatalog.kt`, blob `090d448d0e9de20d002edf07361764e524298bf8`. Донорские три вопроса общие; специализированные графы созданы отдельно, а не объявлены цитатами из донора. Донорские эксплуатационные операции не импортированы.

Источники: Васько Н. М. и др., *Электровоз ВЛ80С*, 2-е изд., 1990, https://djvu.online/file/wXVHhRmTUUuqq; Николаев А. Ю., Сесявин Н. В., *Устройство и работа электровоза ВЛ80С*, 2006, https://djvu.online/file/pqNFfrSxFsGWi. Для каждого сценария отдельно сохранены четыре печатных локатора и пять разных информационных расширений. Оба источника исторические: конкретное исполнение, современный норматив, причина отказа и эксплуатационные полномочия НЕ подтверждены.

Каждый SHORT: 2 вопроса + 4 терминала; DETAILED: 8 специализированных вопросов + 4 терминала. YES/NO/UNKNOWN, неизвестность немедленно STOP; опасный признак STOP; вопросы только о ранее записанных наблюдениях. `CANDIDATE`, `runtimeImport=false`, `executable=false`, `sourceAuthorityVerified=false`, `roleGate/sourceGate/safetyGate=NOT_APPROVED`, неизвестный профиль `BLOCKED`. Расширения скрыты до прокрутки предупреждения и подтверждения, которое не даёт права на операции.

Негативные QA включены в CI, Kotlin/JVM, Android lint, assembleDebug и APK проверяются общим workflow. **До зелёного CI не заявлять PASS.** Физическое устройство: NOT_RUN/DEFERRED. Следующий пакет этапа 11: остальные тяговые ID без повторения этапов 5–6.
