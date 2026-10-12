package ru.railbrake.calculator.shell

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
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
import ru.railbrake.calculator.runtime.ContentPackIndexJsonLoader
import ru.railbrake.calculator.runtime.ContentPackJsonLoader
import ru.railbrake.calculator.runtime.ContentRegistry
import ru.railbrake.calculator.runtime.ModelProfileCatalogJsonLoader
import ru.railbrake.calculator.safety.SafetyContentScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val bootstrap = runCatching { loadVl80sVerticalSlice() }
            .onFailure { Log.e("RailBrake", "VL80S vertical slice bootstrap failed", it) }

        setContent {
            MaterialTheme {
                val loaded = bootstrap.getOrNull()
                if (loaded == null) {
                    Text("Не удалось загрузить модуль ВЛ80С.")
                    return@MaterialTheme
                }

                var currentScreen by remember { mutableStateOf(Vl80sScreen.LAYOUT) }
                var returnFromEntry by remember { mutableStateOf(Vl80sScreen.LAYOUT) }
                var currentId by remember { mutableStateOf(CanonicalId("VL-EQ-HV-002")) }
                var notice by remember { mutableStateOf<String?>(null) }
                var selectedRoute by remember { mutableStateOf<ResolvedAcceptanceRoute?>(null) }
                val entryHistory = remember { mutableStateListOf<CanonicalId>() }

                if (currentScreen != Vl80sScreen.ENTRY) {
                    BackHandler(enabled = currentScreen != Vl80sScreen.LAYOUT) {
                        currentScreen = when (currentScreen) {
                            Vl80sScreen.ACCEPTANCE_ROUTE -> Vl80sScreen.ACCEPTANCE_ROUTES
                            else -> Vl80sScreen.LAYOUT
                        }
                    }
                    when (currentScreen) {
                        Vl80sScreen.LAYOUT -> AtlasLayoutScreen(
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
                            modelTitle = "ВЛ80С",
                            onBack = { currentScreen = Vl80sScreen.LAYOUT },
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

                BackHandler {
                    notice = null
                    if (entryHistory.isNotEmpty()) {
                        currentId = entryHistory.removeAt(entryHistory.lastIndex)
                    } else {
                        currentScreen = returnFromEntry
                    }
                }

                val entry = loaded.registry.find(currentId)
                if (entry == null) {
                    Text("Связанный материал временно недоступен.")
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
                    )

                    FeatureDestination.SAFETY -> SafetyContentScreen(
                        entry = entry,
                        modelTitle = "ВЛ80С",
                        notice = notice,
                        onLink = handleLink,
                    )

                    else -> RailContentEntryScreen(
                        entry = entry,
                        destination = entry.type.featureDestination(),
                        modelTitle = "ВЛ80С",
                        notice = notice,
                        onLink = handleLink,
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
        val routeResolver = AcceptanceRouteResolver(registry)
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

        return Vl80sVerticalSlice(
            registry = registry,
            linkResolver = LinkResolver(registry),
            atlasLayout = atlasLayout,
            pneumaticFlow = pneumaticFlow,
            electricalFlow = electricalFlow,
            diagnosticCatalog = diagnosticCatalog,
            acceptanceRoutes = acceptanceRoutes,
            context = context,
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
    val acceptanceRoutes: List<ResolvedAcceptanceRoute>,
    val context: RuntimeContext,
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
