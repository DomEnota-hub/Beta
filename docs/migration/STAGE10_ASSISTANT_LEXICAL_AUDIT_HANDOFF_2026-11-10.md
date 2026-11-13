# Этап 10/15 — лексический аудит текстового ассистента (10.11.2026)

Ветка: `audit/information-block-gaps-20261014`. Донор `Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff` использовался **только для чтения**.

## Проверенный инженерный результат

1. `assistant-core/AssistantLexicon.kt`: детерминированная нормализация русских словоформ, профессиональных сокращений, разговорных названий, ASR-вариантов серий и ограниченного списка опечаток. Запрещён произвольный fuzzy-match идентификаторов и автоматический выбор исполнения.
2. `AssistantTextEngine.kt`: одинаковая нормализация запроса и индексируемых полей; диагностические карточки не подбираются по единственному совпавшему названию узла; противоположные направления неисправности не подмешиваются друг к другу.
3. `AssistantLexicalCorpusTest.kt`: **41 текстовый/речевой запрос** по всем восьми сериям, отдельные проверки неоднозначности, противоположных симптомов, карантина, source provenance, семи неопубликованных моделей и UI navigation gate. Есть проверка **реального опубликованного** VL80S equipment pack и **реального неопубликованного** diagnostic candidate pack. Дополнительно синтетический позитивный сценарий проверяет сквозной переход к карточке с валидным заводским SOURCE.
4. `.github/workflows/stage10-assistant-lexicon.yml`: Kotlin unit tests + Android lint + Debug APK. Тесты на телефоне не проводились по договорённости.

Проверенные донорские исходники: `AssistantQueryParser.kt`, `AssistantIndex.kt`, `AssistantHumanQueryCorpusTest.kt`, `AssistantScenarioSpeechCorpusTest.kt`, `AssistantDieselStallRoutingTest.kt`, `AssistantSafetyRoutingTest.kt`. Это **контролируемое расширение Beta**, а не заявление о полном 1:1 переносе всех донорских эвристик.

## Матрица запрос → намерение → canonical ID → SOURCE → маршрут

| Запрос | Намерение | Результат / ID | SOURCE | Маршрут и статус |
|---|---|---|---|---|
| «ВЛ80С главник», «ВЛ80С ГВ», «вээл восемьдесят эс гэ вэ» | REFERENCE | `VL-EQ-HV-001` из настоящего `hv.pack.json` | `VL-SRC-001`, `VL-SRC-006`, `VL-SRC-008` | Карточка опубликована, но в изолированном тесте SOURCE-пакет не установлен: `sourceVerified=false`, `recommended=null` |
| «ВЛ80С пантограф» | REFERENCE | `VL-EQ-HV-002` из настоящего `hv.pack.json` | `VL-SRC-001`, `VL-SRC-006`, `VL-SRC-008`, `VL80S-PANTO-S02`, `VL80S-PANTO-S04` | Карточка опубликована; атрибуция не считается подтверждением |
| «ВЛ80С пантограф не поднимается» | DIAGNOSTICS | `vl80s.diag.pantograph-no-rise` в настоящем `high-voltage.pack.json` имеет `CANDIDATE` / `CONDITIONAL_ACTION` | `sourceRefs=[]` | `NoMatches`, переход запрещён |
| «ВЛ80С главник не включается» | DIAGNOSTICS | `vl80s.diag.gv-no-close` в том же pack: `CANDIDATE` / `CONDITIONAL_ACTION` | `sourceRefs=[]` | `NoMatches`, переход запрещён |
| «2ЭС5К главник» и запросы по 3ЭС5К, ЧМЭ3/Т/Э, ТЭМ2/У | REFERENCE | Нет опубликованного runtime соответствующей модели | Не подменяется ВЛ80С | `UnpublishedModel`, fail-closed |
| «ВЛ80С пантограф не поднимается» (синтетический published fixture) | DIAGNOSTICS | `pantograph-no-rise` | `source-official`, `CURRENT`, `MANUFACTURER` | `sourceVerified=true`; повторная проверка `AssistantUiNavigationGate.openHit` разрешает карточку, **автооткрытия диагностики нет** |
| Та же синтетическая пара «не поднимается» / «не опускается» | DIAGNOSTICS | `pantograph-no-lower` | Тот же fixture SOURCE | Противоположный сценарий исключён из результатов |

**Принцип:** строка SOURCE, ссылка или похожее слово сами по себе не доказывают применимость/безопасность. В runtime действуют `ContentRegistry.resolve`, source provenance, model/variant и safety gate. Синтетические позитивные тесты не являются разрешением на публикацию реальных кандидатов.

## Коммиты и проверки

- Первое расширение словаря: `ea69a83c94986ee1a66711fe8cd6d47a1d4645cb`.
- Кодовый HEAD с проверкой настоящих пакетов: `7296fd5dd91a4928f988a915e91b8db54d35e869`.
- [Stage 10 assistant lexical corpus and source gates #42857609088](https://github.com/DomEnota-hub/Beta/actions/runs/42857609088): **SUCCESS (terminal)**; `:assistant-core:test`, `:app-shell:lintDebug`, `:app-shell:assembleDebug`; `BUILD SUCCESSFUL` за 3m49s.
- [Stage 8 text engine #42857609228](https://github.com/DomEnota-hub/Beta/actions/runs/42857609228): SUCCESS на том же кодовом SHA.
- [Stage 9 UI #42857609774](https://github.com/DomEnota-hub/Beta/actions/runs/42857609774): SUCCESS на том же кодовом SHA.
- Первая проверка нового корпуса выявила неверное ожидание теста «компрессор молчит»: должно быть DIAGNOSTICS, а не REFERENCE. Исправлено `614d2c5`; последующие проверки успешны.
- Донорский Kotlin crosswalk на одном из запусков временно получал HTTP 403 от GitHub API; повторная попытка завершилась SUCCESS. Это не ошибка Kotlin-кода.

## Неподтверждённое и backlog

- Реальный опубликованный каталог для текстового ассистента пока ограничен ВЛ80С. Проверки по другим семействам подтверждают **fail-closed**, а не готовность их контента. Включение подтверждённых пакетов — этапы 12–13.
- 55+ донорских речевых диагностических сценариев не могут быть объявлены полностью эквивалентными runtime Beta, пока их конкретные source/variant/safety-gate и статус публикации не подтверждены. Не включать исследовательские `CANDIDATE` ради зелёных тестов.
- Изолированный реальный pack-тест проверяет точные SOURCE ID и отсутствие ложного `sourceVerified`, а не доступность каждого внешнего первоисточника по сети. Полная проверка ссылок остаётся в source-review и итоговой QA.
- Аппаратные тесты поиска, карточек, навигации и ввода речи выполняются только на финальной ручной приёмке.

## Следующее действие

Этап **11/15 — офлайн-голос**: проверить лицензию/доступность Sherpa-ONNX + Zipformer/Silero VAD, интеграцию и fallback, разрешения микрофона, отмену и ошибочные распознавания; речевой текст пропускать через тот же `TextQueryParser` и все source/profile/safety gates. Не представлять поисковую систему как генеративную LLM.
