package ru.railbrake.calculator.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.core.TechnicalFamily

@Composable
fun LocomotiveDiagnosticsScreen(initialScenarioId:String?=null,initialEquipmentId:String?=null){
    val initialFamily=diagnosticInitialFamily(initialScenarioId,initialEquipmentId)
    var familyName by rememberSaveable { mutableStateOf(initialFamily.name) }
    val family=runCatching{TechnicalFamily.valueOf(familyName)}.getOrDefault(TechnicalFamily.VL80S)
    Column(Modifier.fillMaxSize()){
        Row(Modifier.fillMaxWidth().padding(horizontal=16.dp,vertical=8.dp),horizontalArrangement=Arrangement.spacedBy(8.dp)){
            FilterChip(family==TechnicalFamily.VL80S,{familyName=TechnicalFamily.VL80S.name},label={Text("ВЛ80С")})
            FilterChip(family==TechnicalFamily.ERMAK,{familyName=TechnicalFamily.ERMAK.name},label={Text("Ермак")})
            Text("Алгоритмы разделены по серии",style=MaterialTheme.typography.labelMedium,color=MaterialTheme.colorScheme.onSurfaceVariant,fontWeight=FontWeight.Bold,modifier=Modifier.padding(top=10.dp))
        }
        Box(Modifier.fillMaxWidth().weight(1f)){
            if(family==TechnicalFamily.VL80S) DiagnosticScreen(diagnosticScenarioForFamily(initialScenarioId,family),diagnosticEquipmentForFamily(initialEquipmentId,family))
            else ErmakDiagnosticsScreen(
                initialScenarioId=diagnosticScenarioForFamily(initialScenarioId,family),
                initialEquipmentId=diagnosticEquipmentForFamily(initialEquipmentId,family)
            )
        }
    }
}

internal fun diagnosticInitialFamily(scenarioId:String?,equipmentId:String?):TechnicalFamily =
    if(scenarioId?.startsWith("ER-DIAG-")==true||equipmentId?.startsWith("ER-EQ-")==true) TechnicalFamily.ERMAK else TechnicalFamily.VL80S

internal fun diagnosticScenarioForFamily(id:String?,family:TechnicalFamily):String? = when(family){
    TechnicalFamily.VL80S -> id?.takeUnless{it.startsWith("ER-")}
    TechnicalFamily.ERMAK -> id?.takeIf{it.startsWith("ER-DIAG-")}
}

internal fun diagnosticEquipmentForFamily(id:String?,family:TechnicalFamily):String? = when(family){
    TechnicalFamily.VL80S -> id?.takeUnless{it.startsWith("ER-")}
    TechnicalFamily.ERMAK -> id?.takeIf{it.startsWith("ER-EQ-")}
}
