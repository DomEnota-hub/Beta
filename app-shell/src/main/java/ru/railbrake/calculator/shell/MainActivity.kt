package ru.railbrake.calculator.shell

import android.os.Bundle
import android.os.SystemClock
import ru.railbrake.calculator.history.HistoryRecord
import ru.railbrake.calculator.assistant.AssistantTextEngine
import ru.railbrake.calculator.assistant.AssistantUiNavigationGate
import ru.railbrake.calculator.assistant.TextQueryParser
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.ContentLayer
import android.util.Log
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.produceState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import ru.railbrake.calculator.acceptance.AcceptanceFeatureIndexJsonLoader
import ru.railbrake.calculator.acceptance.AcceptanceItemScreen
import ru.railbrake.calculator.acceptance.AcceptanceRouteResolution
import ru.railbrake.calculator.acceptance.AcceptanceRouteResolver
import ru.railbrake.calculator.acceptance.AcceptanceRouteScreen
import ru.railbrake.calculator.acceptance.AcceptanceRoutesScreen
import ru.railbrake.calculator.acceptance.ResolvedAcceptanceRoute
import ru.railbrake.calculator.atlas.AtlasElectricalFlowScreen
import ru.railbrake.calculator.atlas.AtlasPneumaticFlowScreen
import ru.railbrake.calculator.atlas.ElectricalFunctionalFlowDocument
import ru.railbrake.calculator.atlas.ElectricalFunctionalFlowJsonLoader
import ru.railbrake.calculator.atlas.PneumaticFlowDocument
import ru.railbrake.calculator.atlas.PneumaticFlowJsonLoader
import ru.railbrake.calculator.atlas.AtlasFeatureIndexJsonLoader
import ru.railbrake.calculator.atlas.AtlasLayoutJsonLoader
import ru.railbrake.calculator.atlas.AtlasLayoutMap
import ru.railbrake.calculator.atlas.AtlasLayoutScreen
import ru.railbrake.calculator.designsystem.RailContentEntryScreen
import ru.railbrake.calculator.diagnostics.DiagnosticCatalogScreen
import ru.railbrake.calculator.diagnostics.DiagnosticFeatureIndexJsonLoader
import ru.railbrake.calculator.diagnostics.ExecutableDiagnosticFlowJsonLoader
import ru.railbrake.calculator.diagnostics.PublishedDiagnosticCatalog
import ru.railbrake.calculator.diagnostics.DiagnosticReferenceCatalog
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentLink
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.link.LinkNavigationResult
import ru.railbrake.calculator.link.LinkResolver
import ru.railbrake.calculator.navigation.FeatureDestination
import ru.railbrake.calculator.navigation.featureDestination
import ru.railbrake.calculator.navigation.ShellNavigationPolicy
import ru.railbrake.calculator.navigation.ShellHomeDestination
import ru.railbrake.calculator.navigation.ShellHomeNavigationPolicy
import ru.railbrake.calculator.navigation.ShellHomeRoute
import ru.railbrake.calculator.navigation.WorkingModelResolution
import ru.railbrake.calculator.runtime.ContentPackIndexJsonLoader
import ru.railbrake.calculator.runtime.ContentPackJsonLoader
import ru.railbrake.calculator.runtime.ContentRegistry
import ru.railbrake.calculator.runtime.ModelProfileCatalogJsonLoader
import ru.railbrake.calculator.safety.CommonReferenceScreen
import ru.railbrake.calculator.safety.SafetyContentScreen
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val historyStore = AndroidHistoryStore(applicationContext)
        val notesStore = AndroidWorkNotesStore(applicationContext)
        val legacyDiagnosticStore = AndroidLegacyDiagnosticSessionStore(applicationContext)

        // Do not parse VL80S packs on the UI thread before model selection.
        // The validated runtime is loaded only for the explicitly selected VL80S.
        setContent {
            MaterialTheme {
                // A fresh launch never assumes VL80S (or any other working model).
                // Saved instance state preserves an explicit selection on recreation only.
                var selectedModelId by rememberSaveable { mutableStateOf<String?>(null) }
                var shellDestinationName by rememberSaveable(selectedModelId) {
                    mutableStateOf(ShellHomeDestination.HOME.name)
                }
                val workingModel = when (val selection = ShellNavigationPolicy.resolve(selectedModelId)) {
                    WorkingModelResolution.NotSelected -> {
                        WorkingModelSelectionScreen { selectedModelId = it.id.value }
                        return@MaterialTheme
                    }
                    is WorkingModelResolution.Unknown -> {
                        BackHandler { selectedModelId = null }
                        Column {
                            Text("Неизвестная модель: доступ к материалам закрыт.")
                            TextButton(onClick = { selectedModelId = null }) {
                                Text("← Сменить локомотив")
                            }
                        }
                        return@MaterialTheme
                    }
                    is WorkingModelResolution.Selected -> selection.model
                }
                val bootstrap by produceState<Result<Vl80sVerticalSlice>?>(
                    initialValue = null,
                    key1 = workingModel.id.value,
                ) {
                    if (Vl80sBootstrapPolicy.shouldLoad(workingModel.id.value)) {
                        val startedAt = SystemClock.elapsedRealtime()
                        val loaded = withContext(Dispatchers.IO) {
                            runCatching { loadVl80sVerticalSlice() }
                        }
                        val durationMs = SystemClock.elapsedRealtime() - startedAt
                        Log.i("RailBrake", "VL80S runtime load ms=$durationMs success=${loaded.isSuccess}")
                        loaded.exceptionOrNull()?.let {
                            Log.e("RailBrake", "VL80S vertical slice bootstrap failed", it)
                        }
                        value = loaded
                    }
                }
                val shellDestination = ShellHomeDestination.entries.firstOrNull { it.name == shellDestinationName }
                    ?: ShellHomeDestination.HOME
                if (shellDestination == ShellHomeDestination.HOME) {
                    BackHandler { selectedModelId = null }
                    ShellHomeScreen(
                        model = workingModel,
                        onChangeModel = { selectedModelId = null },
                        onOpen = { shellDestinationName = it.name },
                    )
                    return@MaterialTheme
                }
                // Stage 9: keep query while opening a result card and returning.
                var assistantDraft by rememberSaveable(selectedModelId) { mutableStateOf("") }
                var assistantSubmitted by rememberSaveable(selectedModelId) { mutableStateOf("") }
                var assistantCategory by rememberSaveable(selectedModelId) {
                    mutableStateOf<AssistantSearchCategory?>(null)
                }
                var assistantVisibleCount by rememberSaveable(selectedModelId) { mutableStateOf(5) }
                var assistantOpenedTarget by remember(selectedModelId) {
                    mutableStateOf<ContentTarget?>(null)
                }
                var assistantCommonTarget by remember(selectedModelId) {
                    mutableStateOf<Pair<ShellHomeDestination, String>?>(null)
                }
                var assistantFamilyTarget by remember(selectedModelId) {
                    mutableStateOf<Triple<ModelId, VariantId, String>?>(null)
                }
                var assistantViewedModel by remember(selectedModelId) {
                    mutableStateOf<ModelId?>(null)
                }
                var assistantNotice by remember(selectedModelId) { mutableStateOf<String?>(null) }
                val assistantHistory = remember(selectedModelId) {
                    mutableStateListOf<ContentTarget>()
                }
                if (shellDestination == ShellHomeDestination.ASSISTANT) {
                    val loaded = bootstrap?.getOrNull()
                    val opened = assistantOpenedTarget
                    if (assistantFamilyTarget != null) {
                        val (model, execution, cardId) = requireNotNull(assistantFamilyTarget)
                        FamilyContentScreen(
                            modelId = model,
                            modelTitle = ShellNavigationPolicy.resolve(model.value).let {
                                if (it is WorkingModelResolution.Selected) it.model.title
                                else "Неизвестная модель"
                            },
                            destination = ShellHomeDestination.ATLAS,
                            assets = assets,
                            initialExecutionId = execution.value,
                            initialReferenceId = cardId,
                            onBack = { assistantFamilyTarget = null },
                        )
                    } else if (assistantCommonTarget != null) {
                        val (section, cardId) = requireNotNull(assistantCommonTarget)
                        CommonReferenceScreen(
                            destination = section,
                            assets = assets,
                            initialCardId = cardId,
                            onBack = { assistantCommonTarget = null },
                        )
                    } else if (opened == null) {
                        BackHandler { shellDestinationName = ShellHomeDestination.HOME.name }
                        AssistantSearchScreen(
                            engine = loaded?.assistantEngine,
                            publishedCatalogLoading = workingModel.id == ModelId("vl80s") &&
                                bootstrap == null,
                            assets = assets,
                            workingModelId = workingModel.id,
                            workingModelTitle = workingModel.title,
                            draft = assistantDraft,
                            submitted = assistantSubmitted,
                            category = assistantCategory,
                            visibleCount = assistantVisibleCount,
                            notice = assistantNotice,
                            onDraftChange = { assistantDraft = it },
                            onSubmit = {
                                assistantSubmitted = assistantDraft.trim()
                                assistantVisibleCount = 5
                                assistantNotice = null
                            },
                            onCategoryChange = {
                                assistantCategory = it
                                assistantVisibleCount = 5
                                assistantNotice = null
                            },
                            onShowMore = {
                                assistantVisibleCount = (assistantVisibleCount + 5).coerceAtMost(50)
                            },
                            onClarify = { model ->
                                assistantSubmitted =
                                    TextQueryParser.parse(assistantSubmitted).searchText +
                                        " " + model.value
                                assistantDraft = assistantSubmitted
                                assistantVisibleCount = 5
                            },
                            onOpen = { result, target ->
                                val allowed = loaded?.let {
                                    AssistantUiNavigationGate.openHit(
                                        result, target, it.registry, setOf(ModelId("vl80s")))
                                }
                                if (allowed == null) {
                                    assistantNotice = "Материал недоступен: проверка применимости не пройдена."
                                } else {
                                    assistantOpenedTarget = target
                                    assistantViewedModel = result.scope.modelId
                                    assistantHistory.clear()
                                    assistantNotice = null
                                }
                            },
                            onOpenCommon = { section, cardId ->
                                assistantCommonTarget = section to cardId
                                assistantNotice = null
                            },
                            onOpenFamily = { model, execution, cardId ->
                                assistantFamilyTarget = Triple(model, execution, cardId)
                                assistantNotice = null
                            },
                            onBack = { shellDestinationName = ShellHomeDestination.HOME.name },
                        )
                    } else {
                        val context = RuntimeContext(
                            workingModelId = workingModel.id,
                            viewedModelId = assistantViewedModel,
                            activeVariantId = null,
                            allowedLayers = setOf(ContentLayer.STANDARD),
                        )
                        val entry = loaded?.let {
                            AssistantUiNavigationGate.resolveSafeTarget(
                                opened, it.registry, context, setOf(ModelId("vl80s")))
                        }
                        val goBack: () -> Unit = {
                            assistantNotice = null
                            assistantOpenedTarget = if (assistantHistory.isNotEmpty()) {
                                assistantHistory.removeAt(assistantHistory.lastIndex)
                            } else null
                        }
                        BackHandler(onBack = goBack)
                        if (entry == null || loaded == null) {
                            ShellUnavailableScreen(
                                title = "Материал недоступен",
                                explanation = "Проверка публикации или исполнения не пройдена.",
                                onBack = goBack,
                            )
                        } else {
                            val handleLink: (ContentLink) -> Unit = { link ->
                                when (val resolved = loaded.linkResolver.resolve(
                                    sourceId = entry.id, link = link, context = context)) {
                                    is LinkNavigationResult.Found -> {
                                        val next = ContentTarget(
                                            resolved.target.id, resolved.target.contentType)
                                        if (AssistantUiNavigationGate.resolveSafeTarget(
                                                next, loaded.registry, resolved.targetContext,
                                                setOf(ModelId("vl80s"))) != null) {
                                            assistantHistory.add(opened)
                                            assistantOpenedTarget = next
                                            assistantNotice = null
                                        } else {
                                            assistantNotice = "Переход закрыт: источник или профиль не подтверждён."
                                        }
                                    }
                                    else -> {
                                        assistantNotice = "Связанный материал не опубликован или неприменим."
                                    }
                                }
                            }
                            when (entry.type.featureDestination()) {
                                FeatureDestination.ACCEPTANCE -> AcceptanceItemScreen(
                                    entry = entry, modelTitle = "ВЛ80С",
                                    notice = assistantNotice, onLink = handleLink, onBack = goBack)
                                FeatureDestination.SAFETY -> SafetyContentScreen(
                                    entry = entry, modelTitle = "ВЛ80С",
                                    notice = assistantNotice, onLink = handleLink, onBack = goBack)
                                else -> RailContentEntryScreen(
                                    entry = entry,
                                    destination = entry.type.featureDestination(),
                                    modelTitle = "ВЛ80С",
                                    notice = assistantNotice, onLink = handleLink, onBack = goBack)
                            }
                        }
                    }
                    return@MaterialTheme
                }
                // Stage 6: two independent calculation tools behind one common hub.
                // Both are arithmetic previews, never operational approval.
                if (shellDestination == ShellHomeDestination.CALCULATIONS) {
                    var calculationsPage by rememberSaveable(selectedModelId) { mutableStateOf("HUB") }
                    BackHandler {
                        if (calculationsPage == "HUB") {
                            shellDestinationName = ShellHomeDestination.HOME.name
                        } else {
                            calculationsPage = "HUB"
                        }
                    }
                    when (calculationsPage) {
                        "VU45" -> Vu45VerificationScreen(onBack = { calculationsPage = "HUB" }, onSave = { record ->
                            runCatching { historyStore.add(record) }.isSuccess
                        })
                        "SECURING" -> SecuringScreen(onBack = { calculationsPage = "HUB" }, onSave = { record ->
                            runCatching { historyStore.add(record) }.isSuccess
                        })
                        else -> CalculationsHomeScreen(
                            onBack = { shellDestinationName = ShellHomeDestination.HOME.name },
                            onOpenVu45 = { calculationsPage = "VU45" },
                            onOpenSecuring = { calculationsPage = "SECURING" },
                        )
                    }
                    return@MaterialTheme
                }
                if (shellDestination == ShellHomeDestination.RECORDS) {
                    BackHandler { shellDestinationName = ShellHomeDestination.HOME.name }
                    HistoryAndNotesScreen(
                        historyStore = historyStore,
                        notesStore = notesStore,
                        diagnosticStore = legacyDiagnosticStore,
                        modelId = workingModel.id.value,
                        modelTitle = workingModel.title,
                        onBack = { shellDestinationName = ShellHomeDestination.HOME.name },
                    )
                    return@MaterialTheme
                }
                // Stage 14: common reference sections are independent of the
                // working locomotive. Candidate knowledge is readable with
                // provenance warnings, but not promoted to executable actions.
                if (shellDestination in setOf(
                        ShellHomeDestination.KNOWLEDGE,
                        ShellHomeDestination.TRAFFIC_SAFETY,
                        ShellHomeDestination.OCCUPATIONAL_SAFETY,
                        ShellHomeDestination.FIRST_AID,
                    )
                ) {
                    CommonReferenceScreen(
                        destination = shellDestination,
                        assets = assets,
                        onBack = { shellDestinationName = ShellHomeDestination.HOME.name },
                    )
                    return@MaterialTheme
                }
                // Stage 13: family-specific execution is selected inside the section.
                // Unverified family candidates are never routed through VL80S runtime.
                if (workingModel.id != ModelId("vl80s") &&
                    shellDestination in setOf(
                        ShellHomeDestination.ATLAS,
                        ShellHomeDestination.ACCEPTANCE,
                        ShellHomeDestination.DIAGNOSTICS,
                    )
                ) {
                    FamilyContentScreen(
                        modelId = workingModel.id,
                        modelTitle = workingModel.title,
                        destination = shellDestination,
                        assets = assets,
                        onBack = { shellDestinationName = ShellHomeDestination.HOME.name },
                    )
                    return@MaterialTheme
                }
                val shellRoute = ShellHomeNavigationPolicy.resolve(selectedModelId, shellDestination)
                if (shellRoute !is ShellHomeRoute.PublishedModelFeature) {
                    BackHandler { shellDestinationName = ShellHomeDestination.HOME.name }
                    val explanation = when (shellRoute) {
                        is ShellHomeRoute.Unavailable -> {
                            if (shellRoute.modelId != null && !workingModel.runtimePublished) {
                                "Материалы этой модели пока не опубликованы. " +
                                    "Непроверенные источники и исполнения не открываются."
                            } else {
                                "Раздел ещё не подключён к рабочему приложению. " +
                                    "Его материалы будут доступны после отдельной проверки."
                            }
                        }
                        ShellHomeRoute.ModelSelectionRequired ->
                            "Сначала выберите рабочий локомотив."
                        is ShellHomeRoute.PublishedModelFeature -> error("Unreachable")
                    }
                    ShellUnavailableScreen(
                        title = shellDestination.title,
                        explanation = explanation,
                        onBack = { shellDestinationName = ShellHomeDestination.HOME.name },
                    )
                    return@MaterialTheme
                }
                val loaded = bootstrap?.getOrNull()
                if (loaded == null) {
                    BackHandler { shellDestinationName = ShellHomeDestination.HOME.name }
                    Column {
                        Text(if (bootstrap == null) "Загрузка материалов ВЛ80С…"
                            else "Не удалось загрузить модуль ВЛ80С. Проверка данных не пройдена.")
                        TextButton(onClick = {
                            shellDestinationName = ShellHomeDestination.HOME.name
                        }) {
                            Text("← На главную")
                        }
                        TextButton(onClick = { selectedModelId = null }) {
                            Text("Сменить локомотив")
                        }
                    }
                    return@MaterialTheme
                }

                val initialScreen = when (shellDestination) {
                    ShellHomeDestination.DIAGNOSTICS -> Vl80sScreen.DIAGNOSTICS
                    ShellHomeDestination.ACCEPTANCE -> Vl80sScreen.ACCEPTANCE_ROUTES
                    else -> Vl80sScreen.LAYOUT
                }
                var currentScreen by remember(shellDestination) { mutableStateOf(initialScreen) }
                var returnFromEntry by remember { mutableStateOf(Vl80sScreen.LAYOUT) }
                var currentId by remember { mutableStateOf(CanonicalId("VL-EQ-HV-002")) }
                var notice by remember { mutableStateOf<String?>(null) }
                var selectedRoute by remember { mutableStateOf<ResolvedAcceptanceRoute?>(null) }
                val entryHistory = remember { mutableStateListOf<CanonicalId>() }

                if (currentScreen != Vl80sScreen.ENTRY) {
                    BackHandler {
                        currentScreen = when (currentScreen) {
                            Vl80sScreen.LAYOUT -> {
                                shellDestinationName = ShellHomeDestination.HOME.name
                                Vl80sScreen.LAYOUT
                            }
                            Vl80sScreen.DIAGNOSTICS -> {
                                if (shellDestination == ShellHomeDestination.DIAGNOSTICS) {
                                    shellDestinationName = ShellHomeDestination.HOME.name
                                }
                                Vl80sScreen.LAYOUT
                            }
                            Vl80sScreen.ACCEPTANCE_ROUTES -> {
                                if (shellDestination == ShellHomeDestination.ACCEPTANCE) {
                                    shellDestinationName = ShellHomeDestination.HOME.name
                                }
                                Vl80sScreen.LAYOUT
                            }
                            Vl80sScreen.ACCEPTANCE_ROUTE -> Vl80sScreen.ACCEPTANCE_ROUTES
                            else -> Vl80sScreen.LAYOUT
                        }
                    }
                    when (currentScreen) {
                        Vl80sScreen.LAYOUT -> Column {
                            TextButton(onClick = { shellDestinationName = ShellHomeDestination.HOME.name }) {
                                Text("← На главную")
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                AtlasLayoutScreen(
                            layout = loaded.atlasLayout,
                            modelTitle = "ВЛ80С",
                            onEquipmentTarget = { target ->
                                currentId = target.id
                                entryHistory.clear()
                                notice = null
                                returnFromEntry = Vl80sScreen.LAYOUT
                                currentScreen = Vl80sScreen.ENTRY
                            },
                            onPneumaticFlow = {
                                currentScreen = Vl80sScreen.PNEUMATIC
                            },
                            onElectricalFlow = {
                                currentScreen = Vl80sScreen.ELECTRICAL
                            },
                            onDiagnosticsCatalog = {
                                currentScreen = Vl80sScreen.DIAGNOSTICS
                            },
                            onAcceptanceRoutes = {
                                currentScreen = Vl80sScreen.ACCEPTANCE_ROUTES
                            },
                                )
                            }
                        }

                        Vl80sScreen.PNEUMATIC -> AtlasPneumaticFlowScreen(
                            document = loaded.pneumaticFlow,
                            modelTitle = "ВЛ80С",
                            onBack = { currentScreen = Vl80sScreen.LAYOUT },
                        )

                        Vl80sScreen.ELECTRICAL -> AtlasElectricalFlowScreen(
                            document = loaded.electricalFlow,
                            modelTitle = "ВЛ80С",
                            onBack = { currentScreen = Vl80sScreen.LAYOUT },
                            onEquipmentTarget = { target ->
                                currentId = target.id
                                entryHistory.clear()
                                notice = null
                                returnFromEntry = Vl80sScreen.ELECTRICAL
                                currentScreen = Vl80sScreen.ENTRY
                            },
                        )

                        Vl80sScreen.DIAGNOSTICS -> DiagnosticCatalogScreen(
                            catalog = loaded.diagnosticCatalog,
                            referenceCatalog = loaded.diagnosticReferenceCatalog,
                            modelTitle = "ВЛ80С",
                            onBack = {
                                if (shellDestination == ShellHomeDestination.DIAGNOSTICS) {
                                    shellDestinationName = ShellHomeDestination.HOME.name
                                } else {
                                    currentScreen = Vl80sScreen.LAYOUT
                                }
                            },
                        )

                        Vl80sScreen.ACCEPTANCE_ROUTES -> AcceptanceRoutesScreen(
                            routes = loaded.acceptanceRoutes,
                            modelTitle = "ВЛ80С",
                            onOpenRoute = { route ->
                                selectedRoute = route
                                currentScreen = Vl80sScreen.ACCEPTANCE_ROUTE
                            },
                        )

                        Vl80sScreen.ACCEPTANCE_ROUTE -> selectedRoute?.let { route ->
                            AcceptanceRouteScreen(
                                route = route,
                                modelTitle = "ВЛ80С",
                                onOpenItem = { id ->
                                    currentId = id
                                    entryHistory.clear()
                                    notice = null
                                    returnFromEntry = Vl80sScreen.ACCEPTANCE_ROUTE
                                    currentScreen = Vl80sScreen.ENTRY
                                },
                            )
                        }

                        Vl80sScreen.ENTRY -> Unit
                    }
                    return@MaterialTheme
                }

                val backFromEntry: () -> Unit = {
                    notice = null
                    if (entryHistory.isNotEmpty()) {
                        currentId = entryHistory.removeAt(entryHistory.lastIndex)
                    } else {
                        currentScreen = returnFromEntry
                    }
                }
                BackHandler(onBack = backFromEntry)

                val entry = Vl80sEntryGate.open(loaded.registry, currentId, loaded.context)
                if (entry == null) {
                    ShellUnavailableScreen(
                        title = "Материал недоступен",
                        explanation = "Карточка не опубликована, не соответствует исполнению или требует отдельного допуска.",
                        onBack = backFromEntry,
                    )
                    return@MaterialTheme
                }

                val handleLink: (ContentLink) -> Unit = { link ->
                    when (
                        val result = loaded.linkResolver.resolve(
                            sourceId = entry.id,
                            link = link,
                            context = loaded.context,
                        )
                    ) {
                        is LinkNavigationResult.Found -> {
                            if (currentId != result.target.id) {
                                entryHistory.add(currentId)
                                currentId = result.target.id
                            }
                            notice = null
                        }

                        LinkNavigationResult.TargetNotPublished -> {
                            notice =
                                "Связанная диагностика пока не опубликована: сценарий остаётся кандидатом до отдельного GOLDEN REFERENCE PASS."
                        }

                        LinkNavigationResult.LayerDenied -> {
                            notice = "Этот слой информации сейчас отключён."
                        }

                        LinkNavigationResult.TargetInapplicable,
                        LinkNavigationResult.LinkNotApplicable -> {
                            notice = "Материал не применим к выбранному исполнению."
                        }

                        LinkNavigationResult.ScopeDenied -> {
                            notice = "Связь между этими модельными блоками запрещена."
                        }

                        LinkNavigationResult.SourceNotFound,
                        LinkNavigationResult.TargetNotFound,
                        LinkNavigationResult.TypeMismatch -> {
                            notice = "Связанный материал временно недоступен."
                        }
                    }
                }

                when (entry.type.featureDestination()) {
                    FeatureDestination.ACCEPTANCE -> AcceptanceItemScreen(
                        entry = entry,
                        modelTitle = "ВЛ80С",
                        notice = notice,
                        onLink = handleLink,
                        onBack = backFromEntry,
                    )

                    FeatureDestination.SAFETY -> SafetyContentScreen(
                        entry = entry,
                        modelTitle = "ВЛ80С",
                        notice = notice,
                        onLink = handleLink,
                        onBack = backFromEntry,
                    )

                    else -> RailContentEntryScreen(
                        entry = entry,
                        destination = entry.type.featureDestination(),
                        modelTitle = "ВЛ80С",
                        notice = notice,
                        onLink = handleLink,
                        onBack = backFromEntry,
                    )
                }
            }
        }
    }

    private fun loadVl80sVerticalSlice(): Vl80sVerticalSlice {
        val loader = ContentPackJsonLoader()
        val registry = ContentRegistry()

        val indexJson = assets.open("electric/vl80s/runtime-index.json")
            .bufferedReader()
            .use { it.readText() }
        val index = ContentPackIndexJsonLoader().parse(indexJson)
        check(index.modelId == "vl80s") {
            "Unexpected model content index: ${index.modelId}"
        }

        val profileCatalogPath = requireNotNull(index.profileCatalog) {
            "VL80S profile catalog is not configured"
        }
        val profileJson = assets.open(profileCatalogPath)
            .bufferedReader()
            .use { it.readText() }
        val profileCatalog = ModelProfileCatalogJsonLoader().parse(profileJson)
        check(profileCatalog.modelId == ModelId("vl80s")) {
            "Unexpected profile catalog: ${profileCatalog.modelId.value}"
        }

        val atlasIndexPath = requireNotNull(index.featureIndexes["atlas"]) {
            "VL80S atlas feature index is not configured"
        }
        val atlasIndexJson = assets.open(atlasIndexPath)
            .bufferedReader()
            .use { it.readText() }
        val atlasIndex = AtlasFeatureIndexJsonLoader().parse(atlasIndexJson)
        check(atlasIndex.modelId == "vl80s") {
            "Unexpected Atlas index model: ${atlasIndex.modelId}"
        }
        val layoutPath = atlasIndex.layoutMaps.firstOrNull()
            ?: error("VL80S atlas layout is not configured")
        val atlasLayoutJson = assets.open(layoutPath)
            .bufferedReader()
            .use { it.readText() }
        val atlasLayout = AtlasLayoutJsonLoader().parse(atlasLayoutJson)
        check(atlasLayout.modelId == "vl80s") {
            "Unexpected Atlas layout model: ${atlasLayout.modelId}"
        }

        val pneumaticFlow = atlasIndex.stepwiseFlows.map { path ->
            val json = assets.open(path).bufferedReader().use { it.readText() }
            PneumaticFlowJsonLoader().parse(json)
        }.single()
        check(pneumaticFlow.modelId == index.modelId) {
            "Atlas pneumatic flow belongs to another model"
        }
        check(pneumaticFlow.actionAuthority == "NONE") {
            "Atlas pneumatic flow unexpectedly claims operational authority"
        }

        val electricalFlow = atlasIndex.functionalFlows.map { path ->
            val json = assets.open(path).bufferedReader().use { it.readText() }
            ElectricalFunctionalFlowJsonLoader().parse(json)
        }.single()
        check(electricalFlow.modelId == index.modelId) {
            "Atlas electrical flow belongs to another model"
        }
        check(electricalFlow.actionAuthority == "NONE") {
            "Atlas electrical flow unexpectedly claims operational authority"
        }

        val installationIssues = index.packs.flatMap { path ->
            val json = assets.open(path).bufferedReader().use { it.readText() }
            registry.install(loader.parse(json))
        }

        check(
            electricalFlow.scenarios
                .flatMap { it.nodes }
                .mapNotNull { it.equipmentTarget() }
                .all { target ->
                    registry.find(target.id)?.let { entry ->
                        entry.type == target.expectedType &&
                            entry.owner == ContentOwner.Model(ModelId(index.modelId))
                    } == true
                }
        ) {
            "Electrical training flow contains unresolved model equipment"
        }

        val graphIssues = registry.validateGlobalLinks()
        check(installationIssues.isEmpty() && graphIssues.isEmpty()) {
            "VL80S vertical slice validation failed: ${installationIssues + graphIssues}"
        }

        val acceptanceIndexPath = requireNotNull(index.featureIndexes["acceptance"]) {
            "VL80S acceptance feature index is not configured"
        }
        val acceptanceIndexJson = assets.open(acceptanceIndexPath)
            .bufferedReader().use { it.readText() }
        val acceptanceIndex = AcceptanceFeatureIndexJsonLoader().parse(acceptanceIndexJson)
        check(acceptanceIndex.modelId == index.modelId) {
            "Acceptance index belongs to another model"
        }
        check(acceptanceIndex.itemPacks.all { it in index.packs }) {
            "Acceptance index references a pack outside the model runtime index"
        }
        val routeContext = RuntimeContext(
            workingModelId = ModelId("vl80s"),
            viewedModelId = ModelId("vl80s"),
            activeVariantId = profileCatalog.defaultVariantId,
        )
        val routeResolver = AcceptanceRouteResolver(registry, routeContext)
        val acceptanceRoutes = acceptanceIndex.routes.map { route ->
            val result = routeResolver.resolve(route)
            check(result is AcceptanceRouteResolution.Ready) {
                "Acceptance route contains unresolved or unpublished items: ${route.id}"
            }
            result.value.also { ready ->
                check(ready.items.all { it.owner == ContentOwner.Model(ModelId(index.modelId)) }) {
                    "Acceptance route contains an item from another model"
                }
            }
        }

        val context = RuntimeContext(
            workingModelId = ModelId("vl80s"),
            viewedModelId = ModelId("vl80s"),
            activeVariantId = profileCatalog.defaultVariantId,
        )
        val diagnosticsIndexPath = requireNotNull(index.featureIndexes["diagnostics"]) {
            "VL80S diagnostics feature index is not configured"
        }
        val diagnosticsIndexJson = assets.open(diagnosticsIndexPath)
            .bufferedReader()
            .use { it.readText() }
        val diagnosticsIndex = DiagnosticFeatureIndexJsonLoader().parse(diagnosticsIndexJson)
        check(diagnosticsIndex.modelId == index.modelId) {
            "Diagnostics index belongs to another model"
        }
        check(diagnosticsIndex.runtimeAvailability ==
            ru.railbrake.calculator.diagnostics.DiagnosticRuntimeAvailability.EXECUTABLE_FLOW_AVAILABLE) {
            "Executable diagnostic runtime is required for the preview shell"
        }
        val executableFlowPath = requireNotNull(diagnosticsIndex.executableFlow) {
            "Diagnostics runtime asset path is missing"
        }
        check(!executableFlowPath.startsWith("/") && ".." !in executableFlowPath) {
            "Invalid diagnostic runtime asset path"
        }
        val diagnosticRuntimeJson = assets.open(executableFlowPath)
            .bufferedReader()
            .use { it.readText() }
        val diagnosticRuntime = ExecutableDiagnosticFlowJsonLoader()
            .parse(diagnosticRuntimeJson)
        check(diagnosticRuntime.modelId == index.modelId) {
            "Diagnostic graph belongs to another model"
        }
        val diagnosticCatalog = PublishedDiagnosticCatalog(
            runtime = diagnosticRuntime,
            registry = registry,
            context = context,
        )
        // Reference-only donor candidates are not passed to the executable flow.
        val diagnosticReferenceCatalog = DiagnosticReferenceCatalog(
            runtime = diagnosticRuntime,
            registry = registry,
            context = context,
        )

        return Vl80sVerticalSlice(
            registry = registry,
            linkResolver = LinkResolver(registry),
            atlasLayout = atlasLayout,
            pneumaticFlow = pneumaticFlow,
            electricalFlow = electricalFlow,
            diagnosticCatalog = diagnosticCatalog,
            diagnosticReferenceCatalog = diagnosticReferenceCatalog,
            acceptanceRoutes = acceptanceRoutes,
            context = context,
            assistantEngine = AssistantTextEngine(registry, setOf(ModelId("vl80s"))),
        )
    }
}

private data class Vl80sVerticalSlice(
    val registry: ContentRegistry,
    val linkResolver: LinkResolver,
    val atlasLayout: AtlasLayoutMap,
    val pneumaticFlow: PneumaticFlowDocument,
    val electricalFlow: ElectricalFunctionalFlowDocument,
    val diagnosticCatalog: PublishedDiagnosticCatalog,
    val diagnosticReferenceCatalog: DiagnosticReferenceCatalog,
    val acceptanceRoutes: List<ResolvedAcceptanceRoute>,
    val context: RuntimeContext,
    /** Stage 8 text backend, wired to the validated published runtime; UI is stage 9. */
    val assistantEngine: AssistantTextEngine,
)

private enum class Vl80sScreen {
    LAYOUT,
    PNEUMATIC,
    ELECTRICAL,
    DIAGNOSTICS,
    ACCEPTANCE_ROUTES,
    ACCEPTANCE_ROUTE,
    ENTRY,
}
