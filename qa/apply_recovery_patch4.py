#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

def read(rel): return (root / rel).read_text(encoding="utf-8")
def write(rel, text):
    p=root/rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")
def rep(text, old, new, label):
    n=text.count(old)
    if n != 1: raise SystemExit(f"{label}: expected exactly one match, got {n}")
    return text.replace(old,new,1)

core = r'''package ru.railbrake.calculator.core

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

data class CanonicalSchemeVariantOption(val id: String, val title: String)
data class CanonicalSchemeNode(
    val id: String,
    val label: String,
    val targetId: String,
    val subtitle: String,
    val x: Float,
    val y: Float,
    val width: Float = 185f,
    val height: Float = 78f
)
data class CanonicalSchemeEdge(val from: String, val to: String, val kind: String)
data class CanonicalSchemeFlow(val id: String, val title: String, val path: List<String>, val note: String = "")
data class CanonicalSchemeGraph(
    val id: String,
    val title: String,
    val nodes: List<CanonicalSchemeNode>,
    val edges: List<CanonicalSchemeEdge>,
    val flows: List<CanonicalSchemeFlow>,
    val modelOptions: List<CanonicalSchemeVariantOption> = emptyList(),
    val profileOptions: List<CanonicalSchemeVariantOption> = emptyList(),
    val selectionRequired: Boolean = false,
    val applicabilityText: String = "",
    val boundaryText: String = "",
    val canvasWidth: Float,
    val canvasHeight: Float
)

class CanonicalSchemeRepository(private val context: Context) {
    private val vlVariants by lazy { json("technical/vl80s_variants.json") }
    private val vlElectrical by lazy { json("technical/vl80s_electrical.json") }
    private val vlPneumatic by lazy { json("technical/vl80s_pneumatic.json") }
    private val ermakSchemes by lazy { json("technical/ermak_schemes.json") }

    fun graph(entry: TechnicalEntry): CanonicalSchemeGraph? = when {
        entry.family == TechnicalFamily.VL80S && entry.section == TechnicalSection.ELECTRICAL -> vlElectrical(entry.id)
        entry.family == TechnicalFamily.VL80S && entry.section == TechnicalSection.PNEUMATIC -> vlPneumatic(entry.id)
        entry.family == TechnicalFamily.ERMAK && entry.section in listOf(TechnicalSection.ELECTRICAL, TechnicalSection.PNEUMATIC) -> ermak(entry.id)
        else -> null
    }

    private fun vlProfileOptions(ids: List<String>, generic: Boolean): List<CanonicalSchemeVariantOption> {
        val buckets = vlVariants.array("physicalBuckets").objects()
        val selected = if (generic) buckets else buckets.filter { it.optString("id") in ids }
        return selected.map { item ->
            val id=item.optString("id")
            val range=item.optString("range").ifBlank { id }
            CanonicalSchemeVariantOption(id, when(id) {
                "vl80s_unknown" -> "Исполнение не определено"
                "vl80s_modified_or_mixed" -> "После ремонта / смешанное исполнение"
                else -> "Секция $range"
            })
        }
    }

    private fun autoNodes(items: List<JSONObject>): List<CanonicalSchemeNode> = items.mapIndexedNotNull { index, node ->
        val id=node.optString("equipmentId").ifBlank { node.optString("virtualNodeId") }
        if(id.isBlank()) return@mapIndexedNotNull null
        val cols=5
        val x=20f+(index%cols)*205f
        val y=20f+(index/cols)*105f
        CanonicalSchemeNode(
            id=id,
            label=node.optString("label").ifBlank{id},
            targetId=node.optString("equipmentId"),
            subtitle=node.optString("domain"),
            x=x,y=y
        )
    }

    private fun vlElectrical(id: String): CanonicalSchemeGraph? {
        val scheme=vlElectrical.array("baseSchemes").objects().firstOrNull{it.optString("id")==id} ?: return null
        val nodes=autoNodes(scheme.array("nodes").objects())
        val edges=scheme.array("semanticEdges").objects().mapNotNull { edge ->
            val from=edge.optString("fromEquipmentId"); val to=edge.optString("toEquipmentId")
            if(from.isBlank()||to.isBlank()) null else CanonicalSchemeEdge(from,to,edge.optString("relationType"))
        }
        val flows=vlElectrical.array("modeOverlays").objects().filter{it.optString("schemeId")==id}.flatMap { overlay ->
            overlay.array("paths").objects().mapIndexedNotNull { index, path ->
                val ids=path.array("equipmentIds").strings()
                if(ids.isEmpty()) null else CanonicalSchemeFlow(
                    id="${overlay.optString("id")}:$index",
                    title=overlay.optString("title") + path.optString("kind").takeIf(String::isNotBlank)?.let{" · $it"}.orEmpty(),
                    path=ids,
                    note=overlay.optString("note")
                )
            }
        }
        val profiles=scheme.array("profiles").strings()
        val generic=profiles.any{it.contains("base_section_aware") || it.contains("unknown")}
        val options=vlProfileOptions(profiles,generic)
        return CanonicalSchemeGraph(
            id=id,title=scheme.optString("title"),nodes=nodes,edges=edges,flows=flows,
            profileOptions=options,selectionRequired=true,
            applicabilityText="Перед подробным отображением подтвердите исполнение секции. Неизвестный профиль не подменяется другим исполнением.",
            boundaryText=vlElectrical.optString("finalBoundary"),
            canvasWidth=(nodes.maxOfOrNull{it.x+it.width}?:800f)+20f,
            canvasHeight=(nodes.maxOfOrNull{it.y+it.height}?:400f)+20f
        )
    }

    private fun vlPneumatic(id: String): CanonicalSchemeGraph? {
        val view=vlPneumatic.array("views").objects().firstOrNull{it.optString("id")==id} ?: return null
        val nodes=autoNodes(view.array("nodes").objects())
        val edges=view.array("edges").objects().mapNotNull { edge ->
            val from=edge.optString("from"); val to=edge.optString("to")
            if(from.isBlank()||to.isBlank()) null else CanonicalSchemeEdge(from,to,edge.optString("kind"))
        }
        val flows=vlPneumatic.array("states").objects().filter{it.optString("viewId")==id}.flatMap { state ->
            state.array("paths").objects().mapIndexedNotNull { index,path ->
                val seq=path.array("sequence").strings()
                if(seq.isEmpty()) null else CanonicalSchemeFlow(
                    id="${state.optString("id")}:$index",
                    title=state.optString("title") + path.optString("kind").takeIf(String::isNotBlank)?.let{" · $it"}.orEmpty(),
                    path=seq,
                    note=state.optString("summary")
                )
            }
        }
        return CanonicalSchemeGraph(
            id=id,title=view.optString("title"),nodes=nodes,edges=edges,flows=flows,
            profileOptions=vlProfileOptions(emptyList(),true),selectionRequired=true,
            applicabilityText="Точный вариант пневмосистемы зависит от фактического исполнения секции; профиль выбирается до подробного просмотра.",
            boundaryText=vlPneumatic.obj("runtimeContract").optString("boundary"),
            canvasWidth=(nodes.maxOfOrNull{it.x+it.width}?:800f)+20f,
            canvasHeight=(nodes.maxOfOrNull{it.y+it.height}?:400f)+20f
        )
    }

    private fun ermak(id: String): CanonicalSchemeGraph? {
        val scheme=ermakSchemes.array("schemes").objects().firstOrNull{it.optString("id")==id} ?: return null
        val layers=scheme.obj("layers")
        val hotspots=layers.array("hotspotLayer").objects()
        val nodes=hotspots.mapNotNull { hs ->
            val hid=hs.optString("hotspotId"); if(hid.isBlank()) return@mapNotNull null
            val hint=hs.obj("layoutHint")
            CanonicalSchemeNode(
                id=hid,
                label=hs.optString("label").ifBlank{hid},
                targetId=hs.optString("equipmentId"),
                subtitle=hs.optString("schemeDesignation"),
                x=hint.optDouble("x",20.0).toFloat(), y=hint.optDouble("y",20.0).toFloat(),
                width=hint.optDouble("width",185.0).toFloat(), height=hint.optDouble("height",78.0).toFloat()
            )
        }
        val edges=layers.obj("semanticGraph").array("edges").objects().mapNotNull { edge ->
            val from=edge.optString("from"); val to=edge.optString("to")
            if(from.isBlank()||to.isBlank()) null else CanonicalSchemeEdge(from,to,edge.optString("relationType"))
        }
        val flows=layers.array("flowLayer").objects().mapNotNull { flow ->
            val path=flow.array("path").strings(); if(path.isEmpty()) null else CanonicalSchemeFlow(
                id=flow.optString("id"), title=flow.optString("title"), path=path, note=flow.optString("note")
            )
        }
        val rules=scheme.obj("variantRules")
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
        )
    }

    private fun json(asset:String):JSONObject=context.assets.open(asset).bufferedReader().use{JSONObject(it.readText())}
}

private fun JSONObject.array4(key:String):JSONArray=optJSONArray(key)?:JSONArray()
private fun JSONObject.obj4(key:String):JSONObject=optJSONObject(key)?:JSONObject()
private fun JSONArray.objects4():List<JSONObject> = buildList { for(i in 0 until length()) optJSONObject(i)?.let(::add) }
private fun JSONArray.strings4():List<String> = buildList { for(i in 0 until length()) optString(i).takeIf(String::isNotBlank)?.let(::add) }

// Local aliases keep the repository implementation readable without leaking helpers to other files.
private fun JSONObject.array(key:String)=array4(key)
private fun JSONObject.obj(key:String)=obj4(key)
private fun JSONArray.objects()=objects4()
private fun JSONArray.strings()=strings4()
'''
write("app/src/main/java/ru/railbrake/calculator/core/CanonicalSchemeRepository.kt", core)

ui = r'''package ru.railbrake.calculator.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.core.CanonicalSchemeGraph
import ru.railbrake.calculator.core.CanonicalSchemeRepository
import ru.railbrake.calculator.core.TechnicalDataRepository
import ru.railbrake.calculator.core.TechnicalEntry
import ru.railbrake.calculator.core.technicalEntryTitle

@Composable
internal fun CanonicalSchemeRuntime(
    entry: TechnicalEntry,
    technicalRepository: TechnicalDataRepository,
    onOpen: (TechnicalEntry) -> Unit
) {
    val context=LocalContext.current
    val graphRepository=remember { CanonicalSchemeRepository(context.applicationContext) }
    val graph=remember(entry.id){graphRepository.graph(entry)} ?: return
    var selectedModel by rememberSaveable("${entry.id}-model"){ mutableStateOf("") }
    var selectedProfile by rememberSaveable("${entry.id}-profile"){ mutableStateOf("") }
    val unlocked = !graph.selectionRequired ||
        (graph.modelOptions.isEmpty() || selectedModel.isNotBlank()) &&
        (graph.profileOptions.isEmpty() || selectedProfile.isNotBlank())

    Card(
        modifier=Modifier.fillMaxWidth(),
        shape=RoundedCornerShape(18.dp),
        border=BorderStroke(1.dp,MaterialTheme.colorScheme.primary.copy(alpha=.45f)),
        colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surfaceVariant.copy(alpha=.35f))
    ) {
        Column(Modifier.padding(14.dp),verticalArrangement=Arrangement.spacedBy(10.dp)) {
            Text("Интерактивная функциональная схема",style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Black)
            if(graph.applicabilityText.isNotBlank()) Text(graph.applicabilityText,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
            if(graph.modelOptions.isNotEmpty()) {
                Text("Модель",fontWeight=FontWeight.Bold)
                LazyRow(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                    items(graph.modelOptions){ option -> FilterChip(selected=selectedModel==option.id,onClick={selectedModel=option.id},label={Text(option.title)}) }
                }
            }
            if(graph.profileOptions.isNotEmpty()) {
                Text("Исполнение / профиль",fontWeight=FontWeight.Bold)
                LazyRow(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                    items(graph.profileOptions){ option -> FilterChip(selected=selectedProfile==option.id,onClick={selectedProfile=option.id},label={Text(option.title)}) }
                }
            }
            if(!unlocked) {
                Text("Схема заблокирована до выбора требуемого исполнения. Приложение не подставляет профиль молча.",color=MaterialTheme.colorScheme.error,fontWeight=FontWeight.Bold)
            } else {
                CanonicalGraphCanvas(graph,technicalRepository,onOpen)
            }
            if(graph.boundaryText.isNotBlank()) Text(graph.boundaryText,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun CanonicalGraphCanvas(
    graph: CanonicalSchemeGraph,
    technicalRepository: TechnicalDataRepository,
    onOpen: (TechnicalEntry) -> Unit
) {
    var query by rememberSaveable(graph.id){ mutableStateOf("") }
    var zoomIndex by rememberSaveable("${graph.id}-zoom"){ mutableIntStateOf(1) }
    val zoomLevels=listOf(.75f,1f,1.25f,1.5f)
    val zoom=zoomLevels[zoomIndex.coerceIn(zoomLevels.indices)]
    var selectedFlowId by rememberSaveable("${graph.id}-flow"){ mutableStateOf("") }
    var flowStep by rememberSaveable("${graph.id}-flow-step"){ mutableIntStateOf(0) }
    var selectedNodeId by rememberSaveable("${graph.id}-node"){ mutableStateOf<String?>(null) }
    val selectedFlow=graph.flows.firstOrNull{it.id==selectedFlowId}
    val activePath=selectedFlow?.path?.take((flowStep+1).coerceAtMost(selectedFlow.path.size)).orEmpty()
    val activeNodes=activePath.toSet()
    val horizontal=rememberScrollState(); val vertical=rememberScrollState()
    val selectedNode=graph.nodes.firstOrNull{it.id==selectedNodeId}

    OutlinedTextField(
        value=query,onValueChange={query=it},modifier=Modifier.fillMaxWidth(),singleLine=true,
        label={Text("Поиск аппарата / обозначения")}
    )
    Row(horizontalArrangement=Arrangement.spacedBy(6.dp),verticalAlignment=Alignment.CenterVertically) {
        Text("Масштаб",fontWeight=FontWeight.Bold)
        OutlinedButton(onClick={zoomIndex=(zoomIndex-1).coerceAtLeast(0)},enabled=zoomIndex>0){Text("−")}
        Text("${(zoom*100).toInt()}%")
        OutlinedButton(onClick={zoomIndex=(zoomIndex+1).coerceAtMost(zoomLevels.lastIndex)},enabled=zoomIndex<zoomLevels.lastIndex){Text("+")}
    }
    if(graph.flows.isNotEmpty()) {
        Text("Рабочее состояние / функциональный путь",fontWeight=FontWeight.Bold)
        LazyRow(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
            item { FilterChip(selected=selectedFlowId.isBlank(),onClick={selectedFlowId="";flowStep=0},label={Text("Без подсветки")}) }
            items(graph.flows){ flow -> FilterChip(
                selected=selectedFlowId==flow.id,
                onClick={selectedFlowId=flow.id;flowStep=0},
                label={Text(flow.title)}
            ) }
        }
        selectedFlow?.let { flow ->
            Text("Шаг ${flowStep+1} из ${flow.path.size}",color=MaterialTheme.colorScheme.primary,fontWeight=FontWeight.Bold)
            if(flow.note.isNotBlank()) Text(flow.note,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick={flowStep=(flowStep-1).coerceAtLeast(0)},enabled=flowStep>0){Text("Назад")}
                Button(onClick={flowStep=(flowStep+1).coerceAtMost(flow.path.lastIndex)},enabled=flowStep<flow.path.lastIndex){Text("Дальше")}
            }
        }
    }

    Box(
        Modifier.fillMaxWidth().height(520.dp)
            .background(MaterialTheme.colorScheme.surface, RoundedCornerShape(14.dp))
            .border(1.dp,MaterialTheme.colorScheme.outlineVariant,RoundedCornerShape(14.dp))
            .horizontalScroll(horizontal).verticalScroll(vertical)
    ) {
        Box(Modifier.width((graph.canvasWidth*zoom).dp).height((graph.canvasHeight*zoom).dp)) {
            Box(
                Modifier.width(graph.canvasWidth.dp).height(graph.canvasHeight.dp)
                    .graphicsLayer(scaleX=zoom,scaleY=zoom,transformOrigin=TransformOrigin(0f,0f))
            ) {
                Canvas(Modifier.size(graph.canvasWidth.dp,graph.canvasHeight.dp)) {
                    graph.edges.forEach { edge ->
                        val from=graph.nodes.firstOrNull{it.id==edge.from}; val to=graph.nodes.firstOrNull{it.id==edge.to}
                        if(from!=null && to!=null) {
                            val start=Offset((from.x+from.width/2f).dp.toPx(),(from.y+from.height/2f).dp.toPx())
                            val end=Offset((to.x+to.width/2f).dp.toPx(),(to.y+to.height/2f).dp.toPx())
                            val active=edge.from in activeNodes && edge.to in activeNodes
                            drawLine(if(active) Color(0xFF1976D2) else Color(0xFF78909C).copy(alpha=.45f),start,end,strokeWidth=(if(active)4.dp else 2.dp).toPx())
                        }
                    }
                }
                graph.nodes.forEach { node ->
                    val searchHit=query.isNotBlank() && (node.label.contains(query,true)||node.subtitle.contains(query,true))
                    val active=node.id in activeNodes
                    Card(
                        modifier=Modifier.offset(node.x.dp,node.y.dp).size(node.width.dp,node.height.dp)
                            .border(if(active||searchHit)2.dp else 1.dp,if(active)MaterialTheme.colorScheme.primary else if(searchHit)MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.outlineVariant,RoundedCornerShape(12.dp)),
                        onClick={selectedNodeId=node.id},shape=RoundedCornerShape(12.dp),
                        colors=CardDefaults.cardColors(containerColor=if(active)MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface)
                    ) {
                        Column(Modifier.padding(7.dp).fillMaxWidth(),horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center) {
                            Text(node.label,style=MaterialTheme.typography.labelMedium,fontWeight=FontWeight.Bold,textAlign=TextAlign.Center)
                            if(node.subtitle.isNotBlank()) Text(node.subtitle,style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.onSurfaceVariant,textAlign=TextAlign.Center)
                        }
                    }
                }
            }
        }
    }
    Text("Узлов: ${graph.nodes.size} • связей: ${graph.edges.size} • путей/состояний: ${graph.flows.size}",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)

    selectedNode?.let { node ->
        Card(modifier=Modifier.fillMaxWidth(),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.primaryContainer)) {
            Column(Modifier.padding(12.dp),verticalArrangement=Arrangement.spacedBy(7.dp)) {
                Text(node.label,fontWeight=FontWeight.Black)
                if(node.subtitle.isNotBlank()) Text(node.subtitle,color=MaterialTheme.colorScheme.onSurfaceVariant)
                val target=node.targetId.takeIf(String::isNotBlank)?.let(technicalRepository::entry)
                if(target!=null) {
                    OutlinedButton(onClick={onOpen(target)},modifier=Modifier.fillMaxWidth()){Text("Открыть: ${technicalEntryTitle(target)}")}
                    val related=target.relatedIds.mapNotNull(technicalRepository::entry).distinctBy{it.id}.take(12)
                    related.forEach { linked -> OutlinedButton(onClick={onOpen(linked)},modifier=Modifier.fillMaxWidth()){Text("${technicalEntryTitle(linked)} →")} }
                } else Text("Виртуальный узел функциональной схемы",style=MaterialTheme.typography.bodySmall)
            }
        }
    }
}
'''
write("app/src/main/java/ru/railbrake/calculator/ui/CanonicalSchemeRuntime.kt", ui)

rel="app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"
t=read(rel)
t=rep(t, '''                } else TechnicalSequence(entry, repository, onOpen)
''', '''                } else if (entry.sequenceKind == "SCHEME") {
                    CanonicalSchemeRuntime(entry, repository, onOpen)
                } else TechnicalSequence(entry, repository, onOpen)
''', "scheme runtime dispatcher")
write(rel,t)

grel="app/build.gradle.kts"
g=read(grel).replace('versionName = "1.2.2-beta-recovery3"','versionName = "1.2.2-beta-recovery4"',1)
write(grel,g)
print("Recovery patch 4 applied")
