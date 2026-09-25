package ru.railbrake.calculator.core

import java.io.File
import java.io.FileInputStream
import java.util.zip.GZIPInputStream
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Test

class DiagnosticCanonicalRuntimeContractTest {
    @Test
    fun vl80sRuntimeIdsExactlyMatchCanonicalAsset() {
        val root = loadTechnicalJson("vl80s_diagnostics")
        val canonical = DiagnosticCanonicalGraphLoader.parse(DiagnosticCanonicalFamily.VL80S, root)
        val runtimeIds = DiagnosticRepository.scenarios.map { it.id }

        assertEquals("VL80S runtime scenario IDs must be unique", runtimeIds.size, runtimeIds.toSet().size)
        assertEquals("VL80S runtime/canonical scenario IDs differ", canonical.scenarioIds, runtimeIds.toSet())
    }

    @Test
    fun ermakRuntimeIdsExactlyMatchCanonicalAsset() {
        val root = loadTechnicalJson("ermak_diagnostics")
        val canonical = DiagnosticCanonicalGraphLoader.parse(DiagnosticCanonicalFamily.ERMAK, root)
        val runtimeIds = parseErmakDiagnostics(root).map { it.id }

        assertEquals("Ermak runtime scenario IDs must be unique", runtimeIds.size, runtimeIds.toSet().size)
        assertEquals("Ermak runtime/canonical scenario IDs differ", canonical.scenarioIds, runtimeIds.toSet())
    }

    private fun loadTechnicalJson(baseName: String): JSONObject {
        val roots = listOf(
            File("app/src/main/assets/technical"),
            File("src/main/assets/technical")
        )
        val file = roots.asSequence()
            .flatMap { root ->
                sequenceOf(
                    File(root, "$baseName.json"),
                    File(root, "$baseName.json.gz")
                )
            }
            .firstOrNull(File::isFile)
            ?: error("Cannot find canonical technical asset $baseName from ${File(".").absolutePath}")

        val text = if (file.extension == "gz") {
            GZIPInputStream(FileInputStream(file)).bufferedReader(Charsets.UTF_8).use { it.readText() }
        } else {
            file.bufferedReader(Charsets.UTF_8).use { it.readText() }
        }
        return JSONObject(text)
    }
}
