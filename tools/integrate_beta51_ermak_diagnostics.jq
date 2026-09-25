def add_unique($value): (. + [$value] | unique);
def related_ids: ["ER-DIAG-015", "ER-DIAG-016", "ER-DIAG-017", "ER-DIAG-041", "ER-DIAG-045", "ER-DIAG-046", "ER-DIAG-047", "ER-DIAG-050", "ER-DIAG-052", "ER-DIAG-055"];

(.scenarios[] | select(.id == "ER-DIAG-050")) as $base
| ($base
    | .id = "ER-DIAG-136"
    | .title = "Секции развивают разную тягу / токи"
    | .symptom = "При одинаковой команде тяговые токи или тяговое усилие секций заметно различаются"
    | .observations = ["При одинаковой команде тяговые токи или тяговое усилие секций заметно различаются"]
    | .actions = [{"summary":"Не увеличивать тягу до сравнения индикации, токов, сообщений МСУД и поведения каждой секции; при опасных признаках прекратить обычную диагностику.","sourceBound":false,"riskClass":"normal","userFacingPolicy":"TRIAGE_ONLY_NO_REPAIR"}]
    | .outcome = "Маршрут помогает выбрать подтверждённую ветвь: потеря нагрузки секции, ошибка индикации/связи, поосная неравномерность либо последствия боксования. Действия выполнять только в профильном сценарии."
    | .possibleCauses = [{"summary":"Потеря нагрузки или ограничение тяги одной секции."},{"summary":"Нарушение межсекционной связи или недостоверная индикация."},{"summary":"Неравномерность по группе/оси либо продолжающееся ограничение после боксования."}]
    | .relatedScenarioIds = related_ids
    | .graph.nodes |= map(if .id == "custom-check" then .prompt = "Различие сопровождается потерей нагрузки секции, сообщением МСУД или продолжается после прекращения боксования?" else . end)
    | .vl80sUiProjection.title = "Секции развивают разную тягу / токи"
    | .vl80sUiProjection.summary = "При одинаковой команде тяговые токи или тяговое усилие секций заметно различаются"
    | .vl80sUiProjection.immediateActions = ["Не увеличивать тягу до сравнения индикации, токов, сообщений МСУД и поведения каждой секции; при опасных признаках прекратить обычную диагностику."]
    | .vl80sUiProjection.questions |= map(if .key == "custom-check" then .text = "Различие сопровождается потерей нагрузки секции, сообщением МСУД или продолжается после прекращения боксования?" else . end)
    | .vl80sUiProjection.observableSigns = ["При одинаковой команде тяговые токи или тяговое усилие секций заметно различаются"]
    | .vl80sUiProjection.probableCauses = ["Потеря нагрузки или ограничение тяги одной секции.", "Нарушение межсекционной связи или недостоверная индикация.", "Неравномерность по группе/оси либо продолжающееся ограничение после боксования."]
    | .vl80sUiProjection.relatedScenarioIds = related_ids
  ) as $new
| .scenarios += [$new]
| .scenarios |= map(
    .id as $scenarioId
    | if (related_ids | index($scenarioId)) != null
    then .relatedScenarioIds = ((.relatedScenarioIds + [$new.id]) | unique)
      | .vl80sUiProjection.relatedScenarioIds = ((.vl80sUiProjection.relatedScenarioIds + [$new.id]) | unique)
    else . end
  )
| .statistics.totalScenarios += 1
| .statistics.mainScenarios += 1
| .statistics.graphNodes += ($new.graph.nodes | length)
| .indexes.byCategory[$new.category] |= add_unique($new.id)
| reduce $new.equipmentRefs[] as $key (. ; .indexes.byEquipment[$key] |= add_unique($new.id))
| reduce $new.systemIds[] as $key (. ; .indexes.bySystem[$key] |= add_unique($new.id))
| reduce $new.entryModes[] as $key (. ; .indexes.byMode[$key] |= add_unique($new.id))
| .indexes.byStatus[$new.status] |= add_unique($new.id)
| .indexes.mainScenarioIds |= add_unique($new.id)
