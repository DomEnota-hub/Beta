#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1])

def read(rel): return (root/rel).read_text(encoding='utf-8')
def write(rel,s): (root/rel).write_text(s,encoding='utf-8')
def rep(s,a,b,label):
    c=s.count(a)
    if c!=1: raise SystemExit(f'{label}: expected 1 match, got {c}')
    return s.replace(a,b,1)

# The interactive runtime is the canonical graph presentation. Keeping every graph
# node duplicated inside the static TechnicalEntry blocks creates a second large
# object/string projection for all 135 scenarios and is not user-visible value.
rel='app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt'
t=read(rel)
t=rep(t,'                    block("Ветвление диагностики", item.obj("graph").array("nodes").stringsOrSummaries()),\n','', 'remove duplicated Ermak graph projection')
write(rel,t)

rel='app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticRuntime.kt'
t=read(rel)
t=rep(t,'import androidx.compose.material3.CardDefaults\n','import androidx.compose.material3.CardDefaults\nimport androidx.compose.material3.CircularProgressIndicator\n','progress import')
t=rep(t,'import androidx.compose.runtime.remember\n','import androidx.compose.runtime.remember\nimport androidx.compose.runtime.produceState\n','produceState import')
t=rep(t,'import androidx.compose.ui.unit.dp\n','import androidx.compose.ui.unit.dp\nimport kotlinx.coroutines.Dispatchers\nimport kotlinx.coroutines.withContext\n','coroutine imports')

old='''internal class ErmakDiagnosticRuntimeRepository(context: Context) {
    private val appContext = context.applicationContext
    private val root by lazy {
        appContext.assets.open("technical/ermak_diagnostics.json").bufferedReader().use { JSONObject(it.readText()) }
    }

    fun scenario(id: String): ErmakDiagScenarioRuntime? {
        val scenarios = root.optJSONArray("scenarios") ?: return null
'''
new='''internal class ErmakDiagnosticRuntimeRepository(context: Context) {
    private val appContext = context.applicationContext

    companion object {
        private val cacheLock = Any()
        private val scenarioCache = mutableMapOf<String, ErmakDiagScenarioRuntime?>()
    }

    fun scenario(id: String): ErmakDiagScenarioRuntime? {
        synchronized(cacheLock) {
            if (scenarioCache.containsKey(id)) return scenarioCache[id]
        }
        // Parse off the UI thread (caller guarantees this) and do not retain the
        // complete JSONObject after extracting the one requested graph.
        val root = appContext.assets.open("technical/ermak_diagnostics.json").bufferedReader().use { JSONObject(it.readText()) }
        val scenarios = root.optJSONArray("scenarios") ?: return null
'''
t=rep(t,old,new,'runtime repository non-retained root')
old='''        return ErmakDiagScenarioRuntime(
            id = source.optString("id"),
            title = source.optString("title"),
            startNodeId = graph.optString("startNodeId"),
            nodes = nodes,
            families = applicability.optJSONArray("families").strings(),
            profiles = applicability.optJSONArray("profiles").strings(),
            lateProfiles = applicability.optString("lateProfiles"),
            explicitVariantSelectionRequired = applicability.optBoolean("variantSelectionRequired", false)
        )
    }
}'''
new='''        val runtime = ErmakDiagScenarioRuntime(
            id = source.optString("id"),
            title = source.optString("title"),
            startNodeId = graph.optString("startNodeId"),
            nodes = nodes,
            families = applicability.optJSONArray("families").strings(),
            profiles = applicability.optJSONArray("profiles").strings(),
            lateProfiles = applicability.optString("lateProfiles"),
            explicitVariantSelectionRequired = applicability.optBoolean("variantSelectionRequired", false)
        )
        synchronized(cacheLock) { scenarioCache[id] = runtime }
        return runtime
    }
}'''
t=rep(t,old,new,'cache extracted scenario only')
old='''    val context = androidx.compose.ui.platform.LocalContext.current
    val runtimeRepository = remember { ErmakDiagnosticRuntimeRepository(context) }
    val scenario = remember(entry.id) { runtimeRepository.scenario(entry.id) } ?: return

    var family by rememberSaveable(entry.id) { mutableStateOf("") }
'''
new='''    val context = androidx.compose.ui.platform.LocalContext.current
    val runtimeRepository = remember { ErmakDiagnosticRuntimeRepository(context) }
    val loadedScenario by produceState<ErmakDiagScenarioRuntime?>(initialValue = null, key1 = entry.id) {
        value = withContext(Dispatchers.Default) { runtimeRepository.scenario(entry.id) }
    }
    if (loadedScenario == null) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
        ) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                CircularProgressIndicator()
                Text("Подготовка интерактивного маршрута диагностики…")
            }
        }
        return
    }
    val scenario = loadedScenario ?: return

    var family by rememberSaveable(entry.id) { mutableStateOf("") }
'''
t=rep(t,old,new,'async scenario runtime load')
write(rel,t)
print('Stage 3 scenario performance fix applied')
