package ru.railbrake.calculator.core

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
