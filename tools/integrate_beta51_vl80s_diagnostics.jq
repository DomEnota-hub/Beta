(.scenarios[] | select(.id == "ekg-position-mismatch")) as $base
| ($base
    | .id = "vl80s-ekg-section-desync"
    | .runtimeStatus = "VISIBLE_CURRENT_DIAGNOSTIC_REPOSITORY"
    | .originLayer = "DiagnosticResearchIntegration.kt"
    | .title = "Рассогласование позиций ЭКГ между секциями"
    | .summary = "Указатели или фактически подтверждённые положения ЭКГ разных секций не совпадают при одной команде управления."
    | .severity = "RESTRICT_OPERATION"
    | .questionCount = 3
    | .checkCount = 3
    | .dangerCount = 3
    | .relatedScenarioIds = ["ekg-position-mismatch", "ekg-slow-transition", "ekg-stuck", "section-control-loss", "traction-current-imbalance", "traction-one-section-low", "traction-no-assemble"]
    | .linkProvenance = "BETA51_RESEARCH_INTEGRATION"
  ) as $new
| .scenarios += [$new]
| .scenarios |= map(
    if (.id as $id | $new.relatedScenarioIds | index($id)) != null
    then .relatedScenarioIds = ((.relatedScenarioIds + [$new.id]) | unique)
    else . end
  )
