from __future__ import annotations

import base64
import json
import secrets
import subprocess
from pathlib import Path

ASSET_PATHS = [
    Path("app/src/main/assets/exam_questions.json"),
    Path("patch/app/src/main/assets/exam_questions.json"),
]
REPOSITORY_PATHS = [
    Path("app/src/main/java/ru/railbrake/calculator/core/ExamQuestionRepository.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/core/ExamQuestionRepository.kt"),
]
TEST_PATHS = [
    Path("app/src/test/java/ru/railbrake/calculator/core/ExamQuestionAssetTest.kt"),
    Path("patch/app/src/test/java/ru/railbrake/calculator/core/ExamQuestionAssetTest.kt"),
]

# The runtime key is split into two byte arrays in Kotlin. This is deliberately
# not presented as perfect secrecy: the goal is to remove immediately readable
# Q&A text from the APK and raise the cost of casual extraction.
KEY_HEX = "497b185f7e9e781e8e82d6c835d50b470ce172b1fb13440a86665c17a0a33c68"

REPOSITORY_KT = r'''package ru.railbrake.calculator.core

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.util.Base64
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

data class ExamQuestion(
    val id: String,
    val blockId: String,
    val blockTitle: String,
    val sourceNumber: Int,
    val question: String,
    val correctAnswer: String,
    val category: String,
    val keywords: List<String>,
    val requiresImage: Boolean,
    val diagnosticScenarioIds: List<String>,
    val equipmentIds: List<String>,
    val knowledgeTopics: List<String>,
    val sourceVersion: String
)

internal object ExamPayloadCodec {
    private val keyPartA = byteArrayOf(
        -82, 81, 26, -123, -114, 18, 3, 0,
        -125, -37, -91, -42, -49, -26, 126, -73,
        16, 4, 20, 127, -124, -78, 65, -66,
        9, 88, -110, 105, -30, 32, -97, -59
    )
    private val keyPartB = byteArrayOf(
        -25, 42, 2, -38, -16, -116, 123, 30,
        13, 89, 115, 30, -6, 51, 117, -16,
        28, -27, 102, -50, 127, -95, 5, -76,
        -113, 62, -50, 126, 66, -125, -93, -83
    )

    private fun keyBytes(): ByteArray = ByteArray(keyPartA.size) { index ->
        ((keyPartA[index].toInt() xor keyPartB[index].toInt()) and 0xff).toByte()
    }

    fun decode(encoded: String): String {
        val packed = Base64.getMimeDecoder().decode(encoded)
        check(packed.size > IV_SIZE) { "Question payload is too short" }
        val iv = packed.copyOfRange(0, IV_SIZE)
        val ciphertext = packed.copyOfRange(IV_SIZE, packed.size)
        val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
        cipher.init(
            Cipher.DECRYPT_MODE,
            SecretKeySpec(keyBytes(), "AES"),
            IvParameterSpec(iv)
        )
        return cipher.doFinal(ciphertext).toString(Charsets.UTF_8)
    }

    private const val IV_SIZE = 16
}

class ExamQuestionRepository(context: Context) {
    val questions: List<ExamQuestion> by lazy {
        val encoded = context.assets.open("exam_questions.json").bufferedReader().use { it.readText() }
        val root = JSONObject(ExamPayloadCodec.decode(encoded))
        check(root.getInt("questionCount") == 329) { "Ожидалось 329 вопросов" }
        root.getJSONArray("questions").toExamQuestions().also { parsed ->
            check(parsed.size == 329) { "Фактически загружено ${parsed.size} вопросов" }
            check(parsed.map { it.id }.toSet().size == parsed.size) { "В базе есть повторяющиеся ID" }
            val scenarioIds = DiagnosticRepository.scenarios.map { it.id }.toSet()
            val equipmentIds = Vl80sObservationCatalog.equipment.map { it.id }.toSet()
            val missingScenarios = parsed.flatMap { it.diagnosticScenarioIds }.toSet() - scenarioIds
            val missingEquipment = parsed.flatMap { it.equipmentIds }.toSet() - equipmentIds
            check(missingScenarios.isEmpty()) { "Неизвестные сценарии в Q&A: $missingScenarios" }
            check(missingEquipment.isEmpty()) { "Неизвестное оборудование в Q&A: $missingEquipment" }
        }
    }

    val blocks: List<String> get() = questions.map { it.blockTitle }.distinct()
    val categories: List<String> get() = questions.map { it.category }.distinct().sorted()

    fun search(query: String, block: String? = null, category: String? = null): List<ExamQuestion> {
        val tokens = normalize(query).split(' ').filter(String::isNotBlank)
        return questions.filter { item ->
            (block == null || item.blockTitle == block) &&
                (category == null || item.category == category) &&
                tokens.all { token -> normalize(item.searchText).contains(token) }
        }
    }

    /** Facts shown in ordinary thematic UI; the full source registry remains on the unlocked screen. */
    fun thematicFacts(query: String, category: String?, limit: Int = 40): List<ExamQuestion> =
        search(query = query, category = category).filterNot { it.requiresImage }.take(limit)

    private val ExamQuestion.searchText: String
        get() = listOf(question, correctAnswer, category, keywords.joinToString(" ")).joinToString(" ")

    companion object {
        internal fun normalize(value: String): String = value
            .lowercase()
            .replace('ё', 'е')
            .replace(Regex("[^а-яa-z0-9]+"), " ")
            .trim()
    }
}

private fun JSONArray.toExamQuestions(): List<ExamQuestion> = (0 until length()).map { index ->
    val item = getJSONObject(index)
    ExamQuestion(
        id = item.getString("id"),
        blockId = item.getString("blockId"),
        blockTitle = item.getString("blockTitle"),
        sourceNumber = item.getInt("sourceNumber"),
        question = item.getString("question"),
        correctAnswer = item.getString("correctAnswer"),
        category = item.getString("category"),
        keywords = item.getJSONArray("keywords").toStrings(),
        requiresImage = item.getBoolean("requiresImage"),
        diagnosticScenarioIds = item.getJSONArray("diagnosticScenarioIds").toStrings(),
        equipmentIds = item.getJSONArray("equipmentIds").toStrings(),
        knowledgeTopics = item.getJSONArray("knowledgeTopics").toStrings(),
        sourceVersion = item.getString("sourceVersion")
    )
}

private fun JSONArray.toStrings(): List<String> = (0 until length()).map(::getString)
'''

TEST_KT = r'''package ru.railbrake.calculator.core

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class ExamQuestionAssetTest {
    private val encodedAsset by lazy {
        File("src/main/assets/exam_questions.json").readText()
    }

    private val root by lazy {
        JSONObject(ExamPayloadCodec.decode(encodedAsset))
    }

    @Test
    fun packagedAssetIsNotPlainQuestionJson() {
        val raw = encodedAsset.trim()
        assertFalse(raw.startsWith("{"))
        assertFalse(raw.contains("\"questions\""))
        assertFalse(raw.contains("Тепловозы классифицируются"))
        assertTrue(raw.length > 1000)
    }

    @Test
    fun assetContainsAllReviewedQuestions() {
        val questions = root.getJSONArray("questions")
        assertEquals(329, root.getInt("questionCount"))
        assertEquals(329, questions.length())
        val ids = (0 until questions.length()).map { questions.getJSONObject(it).getString("id") }
        assertEquals(329, ids.toSet().size)
    }

    @Test
    fun blockCountsMatchSource() {
        val questions = root.getJSONArray("questions")
        val counts = (0 until questions.length())
            .map { questions.getJSONObject(it).getString("blockId") }
            .groupingBy { it }
            .eachCount()
        assertEquals(mapOf("test-1" to 164, "test-2-1" to 29, "test-2-2" to 72, "test-2-3" to 64), counts)
    }

    @Test
    fun everyQuestionHasSearchAndDistributionMetadata() {
        val questions = root.getJSONArray("questions")
        for (index in 0 until questions.length()) {
            val item = questions.getJSONObject(index)
            assertTrue(item.getString("question").isNotBlank())
            assertTrue(item.getString("correctAnswer").isNotBlank())
            assertTrue(item.getString("category").isNotBlank())
            assertTrue(item.getJSONArray("knowledgeTopics").length() > 0)
            assertFalse(item.getString("sourceVersion").isBlank())
        }
    }

    @Test
    fun diagnosticAndEquipmentLinksAreValid() {
        val questions = root.getJSONArray("questions")
        val scenarioIds = DiagnosticRepository.scenarios.map { it.id }.toSet()
        val equipmentIds = Vl80sObservationCatalog.equipment.map { it.id }.toSet()
        var linkedToScenario = 0
        var linkedToEquipment = 0
        for (index in 0 until questions.length()) {
            val item = questions.getJSONObject(index)
            val scenarios = item.getJSONArray("diagnosticScenarioIds")
            val equipment = item.getJSONArray("equipmentIds")
            for (linkIndex in 0 until scenarios.length()) {
                assertTrue("Unknown scenario in ${item.getString("id")}", scenarios.getString(linkIndex) in scenarioIds)
                linkedToScenario++
            }
            for (linkIndex in 0 until equipment.length()) {
                assertTrue("Unknown equipment in ${item.getString("id")}", equipment.getString(linkIndex) in equipmentIds)
                linkedToEquipment++
            }
        }
        assertTrue(linkedToScenario >= 25)
        assertTrue(linkedToEquipment >= 50)
    }

    @Test
    fun searchNormalizationHandlesRussianYoAndPunctuation() {
        assertEquals("колесная пара", ExamQuestionRepository.normalize("Колёсная, пара!"))
    }
}
'''


def encrypt_payload(raw: bytes) -> str:
    iv = secrets.token_bytes(16)
    result = subprocess.run(
        [
            "openssl", "enc", "-aes-256-cbc",
            "-K", KEY_HEX,
            "-iv", iv.hex(),
            "-nosalt",
        ],
        input=raw,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    packed = iv + result.stdout
    return "\n".join(
        base64.b64encode(packed).decode("ascii")[index:index + 76]
        for index in range(0, len(base64.b64encode(packed).decode("ascii")), 76)
    ) + "\n"


def verify_plain(raw: bytes) -> None:
    root = json.loads(raw.decode("utf-8"))
    assert root["questionCount"] == 329
    assert len(root["questions"]) == 329
    assert len({item["id"] for item in root["questions"]}) == 329


def main() -> None:
    current = ASSET_PATHS[0].read_bytes()
    if current.lstrip().startswith(b"{"):
        verify_plain(current)
        encoded = encrypt_payload(current)
        for path in ASSET_PATHS:
            path.write_text(encoded, encoding="utf-8")
    else:
        encoded = ASSET_PATHS[0].read_text(encoding="utf-8")
        base64.b64decode(encoded)
        for path in ASSET_PATHS:
            path.write_text(encoded, encoding="utf-8")

    for path in REPOSITORY_PATHS:
        path.write_text(REPOSITORY_KT, encoding="utf-8")
    for path in TEST_PATHS:
        path.write_text(TEST_KT, encoding="utf-8")

    assert ASSET_PATHS[0].read_bytes() == ASSET_PATHS[1].read_bytes()
    assert REPOSITORY_PATHS[0].read_bytes() == REPOSITORY_PATHS[1].read_bytes()
    assert TEST_PATHS[0].read_bytes() == TEST_PATHS[1].read_bytes()

    protected = ASSET_PATHS[0].read_text(encoding="utf-8")
    assert not protected.lstrip().startswith("{")
    assert '"questions"' not in protected
    assert "Тепловозы классифицируются" not in protected
    print("Protected 329-question payload and updated runtime decoder/tests")


if __name__ == "__main__":
    main()
