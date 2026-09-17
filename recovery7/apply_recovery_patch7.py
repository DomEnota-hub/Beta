#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")


def read(rel):
    return (root / rel).read_text(encoding="utf-8")


def write(rel, text):
    (root / rel).write_text(text, encoding="utf-8")


def rep(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Core scheme model: expose the canonical global Ermak variant selector and
# per-scheme requirements. Unknown/blank dimensions never silently default.
# ---------------------------------------------------------------------------
rel = "app/src/main/java/ru/railbrake/calculator/core/CanonicalSchemeRepository.kt"
t = read(rel)

t = rep(t, '''data class CanonicalSchemeVariantOption(val id: String, val title: String)
data class CanonicalSchemeNode(''', '''data class CanonicalSchemeVariantOption(val id: String, val title: String)
data class CanonicalSchemeSelectorDimension(
    val id: String,
    val title: String,
    val options: List<CanonicalSchemeVariantOption>,
    val required: Boolean = false,
    val requiredWhenModel: String = ""
)
data class CanonicalSchemeNode(''', "selector dimension model")

t = rep(t, '''    val selectionRequired: Boolean = false,
    val applicabilityText: String = "",
    val boundaryText: String = "",
    val canvasWidth: Float,''', '''    val selectionRequired: Boolean = false,
    val selectorDimensions: List<CanonicalSchemeSelectorDimension> = emptyList(),
    val selectorRequirements: Map<String, List<String>> = emptyMap(),
    val hardRules: List<String> = emptyList(),
    val applicabilityText: String = "",
    val boundaryText: String = "",
    val canvasWidth: Float,''', "selector fields")

# Insert helpers before ermak().
marker = '''    private fun ermak(id: String): CanonicalSchemeGraph? {'''
helpers = r'''    private fun ermakSelectorDimensions(): List<CanonicalSchemeSelectorDimension> =
        ermakSchemes.obj("variantSelector").array("dimensions").objects().map { dim ->
            val requiredWhen = dim.obj("requiredWhen").optString("model")
            CanonicalSchemeSelectorDimension(
                id = dim.optString("id"),
                title = dim.optString("title"),
                options = dim.array("values").strings().map { value ->
                    CanonicalSchemeVariantOption(value, ermakVariantLabel(dim.optString("id"), value))
                },
                required = dim.optBoolean("required", false),
                requiredWhenModel = requiredWhen
            )
        }

    private fun ermakVariantLabel(dimension: String, value: String): String = when (dimension to value) {
        "model" to "2ES5K" -> "2ЭС5К"
        "model" to "3ES5K" -> "3ЭС5К"
        "sectionKind" to "head" -> "Головная секция"
        "sectionKind" to "booster" -> "Бустерная секция"
        "tractionControl" to "group_base" -> "Групповое, базовое"
        "tractionControl" to "axle_control_modern" -> "Поосное, современное"
        "tractionControl" to "3es5k_434_experimental" -> "3ЭС5К №434, экспериментальное"
        "tractionControl" to "3es5k_896plus" -> "3ЭС5К №896+"
        "controlSystem" to "MSUD-N" -> "МСУД-Н"
        "controlSystem" to "MSUD-015" -> "МСУД-015"
        "brakeVariant" to "395" -> "Кран №395"
        "brakeVariant" to "130_UKTOL" -> "№130 / УКТОЛ"
        "brakeVariant" to "130-2_BTO-010-3" -> "№130-2 / БТО-010-3"
        "safetyProfile" to "KLUB-U_SAUT-TSKBM" -> "КЛУБ-У / САУТ / ТСКБМ"
        "safetyProfile" to "BLOK_2ES5K" -> "БЛОК / БЛОК-М, 2ЭС5К"
        "motorAxleBearing" to "plain" -> "МОП скольжения"
        "motorAxleBearing" to "rolling" -> "МОП качения"
        else -> if (value == "unknown") "Не подтверждено" else value.replace('_', ' ')
    }

    private fun ermakSelectorRequirements(schemeId: String, profiles: List<String>, models: List<String>): Map<String, List<String>> {
        val result = linkedMapOf<String, List<String>>()
        if (models.isNotEmpty()) result["model"] = models

        when {
            schemeId.contains("3ES5K-BOOSTER") -> result["sectionKind"] = listOf("booster")
            schemeId.contains("3ES5K-HEAD") -> result["sectionKind"] = listOf("head")
        }

        if ("traction_axle_control_modern" in profiles) result["tractionControl"] = listOf("axle_control_modern")
        if ("3es5k_axle_control_434_experimental" in profiles) result["tractionControl"] = listOf("3es5k_434_experimental")
        if ("3es5k_axle_control_896plus" in profiles) result["tractionControl"] = listOf("3es5k_896plus")

        if (schemeId == "ER-SCH-EL-BASE-CONTROL") result["controlSystem"] = listOf("MSUD-N")
        if ("msud_015_extended" in profiles) result["controlSystem"] = listOf("MSUD-015")

        if ("brake_395" in profiles) result["brakeVariant"] = listOf("395")
        if (profiles.any { it == "brake_130_uktol" || it == "base_remote_brake_control" }) result["brakeVariant"] = listOf("130_UKTOL")
        if ("brake_130_2_uktol" in profiles) result["brakeVariant"] = listOf("130-2_BTO-010-3")

        if (schemeId == "ER-SCH-SAFETY-BASE") result["safetyProfile"] = listOf("KLUB-U_SAUT-TSKBM")
        if ("safety_blok_confirmed_2es5k" in profiles) result["safetyProfile"] = listOf("BLOK_2ES5K")

        if ("motor_axle_bearing_plain" in profiles) result["motorAxleBearing"] = listOf("plain")
        if ("motor_axle_bearing_rolling" in profiles) result["motorAxleBearing"] = listOf("rolling")
        return result
    }

'''
if t.count(marker) != 1:
    raise SystemExit("ermak helper insertion point not found")
t = t.replace(marker, helpers + marker, 1)

# Replace Ermak variant preparation and graph return fragment.
old = '''        val rules=scheme.obj("variantRules")
        val models=rules.array("models").strings().map{CanonicalSchemeVariantOption(it,it.replace("ES","ЭС"))}
        val profiles=rules.array("includeProfiles").strings().map{ idv -> CanonicalSchemeVariantOption(idv, idv.replace('_',' ')) }
        val required=rules.optBoolean("selectionRequired")
        return CanonicalSchemeGraph(
            id=id,title=scheme.optString("title"),nodes=nodes,edges=edges,flows=flows,
            modelOptions=models,profileOptions=profiles,selectionRequired=required,
            applicabilityText=buildList{
                if(models.isNotEmpty()) add("Модели: ${models.joinToString{it.title}}")
                if(profiles.isNotEmpty()) add("Профили: ${profiles.joinToString{it.title}}")
                rules.optString("notes").takeIf(String::isNotBlank)?.let(::add)
            }.joinToString(" • "),
            boundaryText="Функциональная интерактивная проекция канонического графа; не заменяет заводской монтажный чертёж конкретного исполнения.",
            canvasWidth=(nodes.maxOfOrNull{it.x+it.width}?:1120f)+20f,
            canvasHeight=(nodes.maxOfOrNull{it.y+it.height}?:700f)+20f
        )'''
new = '''        val rules=scheme.obj("variantRules")
        val modelIds=rules.array("models").strings()
        val profileIds=rules.array("includeProfiles").strings()
        val models=modelIds.map{CanonicalSchemeVariantOption(it,ermakVariantLabel("model",it))}
        val profiles=profileIds.map{ idv -> CanonicalSchemeVariantOption(idv, idv.replace('_',' ')) }
        val selectorDimensions=ermakSelectorDimensions()
        val selectorRequirements=ermakSelectorRequirements(id, profileIds, modelIds)
        val hardRules=ermakSchemes.obj("variantSelector").array("hardRules").strings()
        return CanonicalSchemeGraph(
            id=id,title=scheme.optString("title"),nodes=nodes,edges=edges,flows=flows,
            modelOptions=models,profileOptions=profiles,selectionRequired=true,
            selectorDimensions=selectorDimensions,
            selectorRequirements=selectorRequirements,
            hardRules=hardRules,
            applicabilityText=buildList{
                if(models.isNotEmpty()) add("Модели: ${models.joinToString{it.title}}")
                if(profiles.isNotEmpty()) add("Профили: ${profiles.joinToString{it.title}}")
                rules.optString("notes").takeIf(String::isNotBlank)?.let(::add)
            }.joinToString(" • "),
            boundaryText=ermakSchemes.obj("variantSelector").optString("rule") + " Функциональная интерактивная проекция не заменяет заводской монтажный чертёж конкретного исполнения.",
            canvasWidth=(nodes.maxOfOrNull{it.x+it.width}?:1120f)+20f,
            canvasHeight=(nodes.maxOfOrNull{it.y+it.height}?:700f)+20f
        )'''
t = rep(t, old, new, "Ermak canonical selector")
write(rel, t)

# ---------------------------------------------------------------------------
# UI: use one shared Ermak selector across schemes and lock incompatible graph.
# ---------------------------------------------------------------------------
rel = "app/src/main/java/ru/railbrake/calculator/ui/CanonicalSchemeRuntime.kt"
t = read(rel)

t = rep(t, '''    var selectedModel by rememberSaveable("${entry.id}-model"){ mutableStateOf("") }
    var selectedProfile by rememberSaveable("${entry.id}-profile"){ mutableStateOf("") }
    val unlocked = !graph.selectionRequired ||
        (graph.modelOptions.isEmpty() || selectedModel.isNotBlank()) &&
        (graph.profileOptions.isEmpty() || selectedProfile.isNotBlank())
''', '''    var selectedModel by rememberSaveable("${entry.id}-model"){ mutableStateOf("") }
    var selectedProfile by rememberSaveable("${entry.id}-profile"){ mutableStateOf("") }
    val ermakSelectorPrefs = remember { context.getSharedPreferences("ermak_scheme_variant", android.content.Context.MODE_PRIVATE) }
    var ermakSelection by remember(entry.family) {
        mutableStateOf(graph.selectorDimensions.associate { dim -> dim.id to (ermakSelectorPrefs.getString(dim.id, "") ?: "") })
    }
    val isErmakSelector = graph.selectorDimensions.isNotEmpty()
    val missingRequiredDimensions = if (!isErmakSelector) emptyList() else graph.selectorDimensions.filter { dim ->
        val model = ermakSelection["model"].orEmpty()
        val requiredNow = dim.required || (dim.requiredWhenModel.isNotBlank() && dim.requiredWhenModel == model) || graph.selectorRequirements[dim.id].orEmpty().isNotEmpty()
        requiredNow && ermakSelection[dim.id].orEmpty().isBlank()
    }
    val incompatibleDimensions = if (!isErmakSelector) emptyList() else graph.selectorRequirements.mapNotNull { (dimension, allowed) ->
        val selected = ermakSelection[dimension].orEmpty()
        if (selected.isNotBlank() && selected !in allowed) dimension else null
    }
    val unlocked = if (isErmakSelector) {
        missingRequiredDimensions.isEmpty() && incompatibleDimensions.isEmpty()
    } else {
        !graph.selectionRequired ||
            (graph.modelOptions.isEmpty() || selectedModel.isNotBlank()) &&
            (graph.profileOptions.isEmpty() || selectedProfile.isNotBlank())
    }
''', "shared Ermak selector state")

# Insert selector UI before legacy model/profile UI.
needle = '''            if(graph.applicabilityText.isNotBlank()) Text(graph.applicabilityText,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
            if(graph.modelOptions.isNotEmpty()) {'''
replacement = '''            if(graph.applicabilityText.isNotBlank()) Text(graph.applicabilityText,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
            if(isErmakSelector) {
                Text("Исполнение Ермака",fontWeight=FontWeight.Black)
                graph.selectorDimensions.forEach { dimension ->
                    val model = ermakSelection["model"].orEmpty()
                    val requiredNow = dimension.required || (dimension.requiredWhenModel.isNotBlank() && dimension.requiredWhenModel == model) || graph.selectorRequirements[dimension.id].orEmpty().isNotEmpty()
                    if (dimension.requiredWhenModel.isBlank() || dimension.requiredWhenModel == model || dimension.id != "sectionKind") {
                        Text(dimension.title + if(requiredNow) " • обязательно" else "",fontWeight=FontWeight.Bold)
                        LazyRow(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                            items(dimension.options){ option ->
                                FilterChip(
                                    selected=ermakSelection[dimension.id]==option.id,
                                    onClick={
                                        val updated=ermakSelection.toMutableMap().apply { put(dimension.id,option.id) }
                                        if(dimension.id=="model" && option.id!="3ES5K") updated["sectionKind"]=""
                                        ermakSelection=updated
                                        val editor=ermakSelectorPrefs.edit()
                                        updated.forEach { (key,value) -> if(value.isBlank()) editor.remove(key) else editor.putString(key,value) }
                                        editor.apply()
                                    },
                                    label={Text(option.title)}
                                )
                            }
                        }
                    }
                }
                if(missingRequiredDimensions.isNotEmpty()) {
                    Text("Нужно подтвердить: ${missingRequiredDimensions.joinToString { it.title }}.",color=MaterialTheme.colorScheme.error,fontWeight=FontWeight.Bold)
                }
                if(incompatibleDimensions.isNotEmpty()) {
                    val titles=graph.selectorDimensions.filter { it.id in incompatibleDimensions }.joinToString { it.title }
                    Text("Выбранное исполнение несовместимо с этой схемой: $titles. Канонический граф заблокирован, подмена другой схемой не выполняется.",color=MaterialTheme.colorScheme.error,fontWeight=FontWeight.Bold)
                }
            }
            if(!isErmakSelector && graph.modelOptions.isNotEmpty()) {'''
t = rep(t, needle, replacement, "Ermak selector UI")

t = rep(t, '''            if(graph.profileOptions.isNotEmpty()) {''', '''            if(!isErmakSelector && graph.profileOptions.isNotEmpty()) {''', "legacy profile selector only for non-Ermak")

t = rep(t, '''            if(!unlocked) {
                Text("Схема заблокирована до выбора требуемого исполнения. Приложение не подставляет профиль молча.",color=MaterialTheme.colorScheme.error,fontWeight=FontWeight.Bold)
            } else {''', '''            if(!unlocked) {
                Text("Схема заблокирована до выбора совместимого исполнения. Приложение не подставляет профиль молча.",color=MaterialTheme.colorScheme.error,fontWeight=FontWeight.Bold)
            } else {''', "lock message")

write(rel, t)

gradle_rel = "app/build.gradle.kts"
g = read(gradle_rel)
g, count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.2.2-beta-recovery7"', g, count=1)
if count != 1:
    raise SystemExit("versionName not found")
write(gradle_rel, g)

print("Recovery patch 7 applied")
