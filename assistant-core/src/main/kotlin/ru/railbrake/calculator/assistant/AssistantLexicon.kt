package ru.railbrake.calculator.assistant

/**
 * Deterministic, conservative lexicon adapted from the pinned Test- assistant.
 *
 * This normalizes terminology for retrieval only. It never establishes source
 * provenance, locomotive applicability, an execution profile or permission to act.
 * No fuzzy matching of arbitrary railway identifiers is permitted.
 */
object AssistantLexicon {
    private val spokenAndModel = listOf(
        "вээл восемьдесят эс" to "вл80с",
        "вээл восемьдесят с" to "вл80с",
        "в эл восемьдесят эс" to "вл80с",
        "вл восемьдесят с" to "вл80с",
        "вл восемьдесят эс" to "вл80с",
        "вл 80 эс" to "вл80с", "вл 80 с" to "вл80с",
        "вээл 80 эс" to "вл80с", "вээл 80 с" to "вл80с",
        "два э с пять ка" to "2эс5к", "два эс пять ка" to "2эс5к",
        "два эс пять к" to "2эс5к", "2 эс 5 ка" to "2эс5к",
        "2 эс 5 к" to "2эс5к", "двух эс пять ка" to "2эс5к",
        "три э с пять ка" to "3эс5к", "три эс пять ка" to "3эс5к",
        "три эс пять к" to "3эс5к", "3 эс 5 ка" to "3эс5к",
        "3 эс 5 к" to "3эс5к", "трех эс пять ка" to "3эс5к",
        "чмэ три тэ" to "чмэ3т", "чмэ три т" to "чмэ3т",
        "чмэ три э" to "чмэ3э", "чмэ три" to "чмэ3",
        "чмэ 3 т" to "чмэ3т", "чмэ 3 э" to "чмэ3э",
        "чмэ 3" to "чмэ3", "тэм два у" to "тэм2у",
        "тэм два" to "тэм2", "тэм 2 у" to "тэм2у",
        "тэм 2" to "тэм2"
    )

    // Exact phrase/word boundaries: a short alias must not match a substring
    // of a different model, component or safety term.
    private val componentAndSpeech = listOf(
        "главник" to "главный выключатель",
        "гэвэ" to "главный выключатель",
        "гэ вэ" to "главный выключатель",
        "гв" to "главный выключатель",
        "групповик" to "групповой переключатель",
        "фазник" to "фазорасщепитель",
        "фазорасщипитель" to "фазорасщепитель",
        "компресор" to "компрессор",
        "трансфарматор" to "трансформатор",
        "токоприемнек" to "токоприемник",
        "токо приемник" to "токоприемник",
        "пантограф" to "токоприемник",
        "э ка гэ" to "экг", "э к гэ" to "экг",
        "тэ дэ" to "тэд", "тэд" to "тяговый двигатель",
        "э пэ ка" to "эпк", "э ка гэ" to "экг",
        "вэ эр 483" to "вр 483", "вр483" to "вр 483",
        "акб" to "аккумуляторная батарея",
        "гр" to "главные резервуары",
        "вр 483" to "воздухораспределитель 483",
        "эпк" to "электропневматический клапан",
        "гэвэ" to "главный выключатель",
        "мотор компрессор" to "компрессор",
        "мк" to "компрессор",
        "тэ эм" to "тм", "тм" to "тормозная магистраль",
        "пэ эм" to "пм", "пм" to "питательная магистраль",
        "тэ цэ" to "тц", "тц" to "тормозной цилиндр",
        "ка эм 395" to "кран машиниста 395",
        "кран 395" to "кран машиниста 395",
        "машинистский кран" to "кран машиниста",
        "сифонит" to "утечка воздуха",
        "травит" to "утечка воздуха",
        "не пашет" to "не работает",
        "не фурычит" to "не работает",
        "не горит экран" to "нет индикации",
        "экран не горит" to "нет индикации",
        "тягу не берет" to "нет тяги",
        "не берет тягу" to "нет тяги",
        "тормоз не отпускает" to "тормоз не отпускается",
        "вырубило" to "самопроизвольно отключило",
        "вырубился" to "самопроизвольно отключился",
        "отрубился" to "самопроизвольно отключился",
        "отвалился" to "самопроизвольно отключился",
        "залип" to "заклинил",
        "залипает" to "заклинивает"
    )

    // Precompile once: every indexed title/term is normalized during search.
    private fun compile(substitutions: List<Pair<String, String>>): List<Pair<Regex, String>> =
        substitutions.sortedByDescending { it.first.length }.map { (from, to) ->
            Regex("(?<![\\p{L}\\p{N}])" + Regex.escape(from) + "(?![\\p{L}\\p{N}])") to to
        }

    private val modelPatterns by lazy { compile(spokenAndModel) }
    private val componentPatterns by lazy { compile(componentAndSpeech) }

    private fun replacePhrases(input: String, substitutions: List<Pair<Regex, String>>): String {
        var text = input
        for ((pattern, to) in substitutions) text = text.replace(pattern, to)
        return text
    }

    fun normalize(input: String): String {
        val cleaned = input.lowercase().replace('ё', 'е')
            .replace(Regex("[^\\p{L}\\p{N}\\s]"), " ")
            .replace(Regex("\\s+"), " ").trim()
        return replacePhrases(replacePhrases(cleaned, modelPatterns), componentPatterns)
            .replace(Regex("\\s+"), " ").trim()
    }

    private val faultCues = listOf(
        "не включ", "не выключ", "не поднима", "не опуска",
        "не запуска", "не старт", "не работает", "не срабаты",
        "не набира", "не кач", "не тормоз", "не отпуска",
        "не заряжа", "не держ", "не тян", "не горит", "молчит",
        "нет индикации", "нет зарядки", "нет воздуха",
        "нет тяги", "тяги нет", "пропала тяга", "тяга пропала",
        "нет давления", "давление пада", "неисправ", "отказ",
        "выбива", "отключился", "отключило", "самопроизвольно",
        "заклин", "застрял", "глох", "заглох", "перегрев",
        "греется", "искрит", "дымит", "утечка", "течет",
        "шумит", "стучит", "не останавлива", "не светится"
    )

    private val humanSafety = Regex(
        "(?:человек\\p{L}*|машинист\\p{L}*|помощник\\p{L}*|рабоч\\p{L}*)" +
            "(?: +\\p{L}+){0,5} +(удар\\p{L}*|тряхнул\\p{L}*|шарахнул\\p{L}*)" +
            "(?: +\\p{L}+){0,3} +(ток\\p{L}*|электричеств\\p{L}*)"
    )

    /**
     * Distinguish opposite failure directions even if the equipment name is
     * identical. Only explicit contradictory fault phrases are excluded.
     */
    fun contradictsFault(query: String, candidate: String): Boolean {
        val opposites = listOf(
            "не включ" to "не выключ",
            "не поднима" to "не опуска",
            "не заряжа" to "не разряжа",
            "не тормоз" to "не отпуска"
        )
        return opposites.any { (left, right) ->
            (left in query && right in candidate) || (right in query && left in candidate)
        }
    }

    fun intent(normalized: String): TextIntent {
        val safetyEmergency = listOf("первая помощь", "охрана труда", "электротравм",
            "поражение током", "поражение электрическим", "кровотеч",
            "без сознания", "не дышит", "ожог человека", "отравился",
            "человека ударило током", "ударило током человека",
            "пожар в", "горит локомотив", "пахнет гарью в")
            .any(normalized::contains) || humanSafety.containsMatchIn(normalized)
        return when {
            safetyEmergency -> TextIntent.SAFETY
            listOf("схем", "чертеж", "электроцеп", "цепи управления",
                "пневмосхем").any(normalized::contains) -> TextIntent.SCHEME
            listOf("приемк", "осмотр локомотива", "принимать локомотив",
                "начать осмотр").any(normalized::contains) -> TextIntent.ACCEPTANCE
            faultCues.any(normalized::contains) -> TextIntent.DIAGNOSTICS
            else -> TextIntent.REFERENCE
        }
    }
}
