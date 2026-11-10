package ru.railbrake.calculator.assistant

import org.junit.Assert.*
import org.junit.Test
import ru.railbrake.calculator.domain.*
import ru.railbrake.calculator.runtime.*

/**
 * Stage 10: typed human/ASR query -> intent -> exact canonical hit -> verified source.
 * Synthetic fixtures prove routing/gates, not that a donor diagnostic was published.
 */
class AssistantLexicalCorpusTest {
    private val vl = ModelId("vl80s")
    private data class Probe(val phrase: String, val intent: TextIntent, val model: String? = null)

    @Test fun humanSpeechAndTypoCorpusHasDeterministicRouting() {
        val cases = listOf(
            Probe("ВЛ80С главник не включается", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("на вээл восемьдесят эс гэ вэ не включается", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С ГВ не выключается", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С компресор не работает", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С фазорасщипитель не работает", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С токоприемнек не поднимается", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С пантограф не опускается", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С групповик залип", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С мотор компрессор молчит", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С кран 395 травит", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С ТМ давление падает", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С сифонит компрессор", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("покажи схему ГВ на ВЛ80С", TextIntent.SCHEME, "vl80s"),
            Probe("приемка ВЛ80С снаружи", TextIntent.ACCEPTANCE, "vl80s"),
            Probe("человека ударило током", TextIntent.SAFETY),
            Probe("помощника машиниста шарахнуло током", TextIntent.SAFETY),
            Probe("пожар в машинном отделении", TextIntent.SAFETY),
            Probe("пожарная сигнализация не работает", TextIntent.DIAGNOSTICS),
            Probe("датчик тока", TextIntent.REFERENCE),
            Probe("удар предмета по локомотиву", TextIntent.REFERENCE),
            Probe("2 эс 5 к ГВ не включается", TextIntent.DIAGNOSTICS, "2es5k"),
            Probe("три эс пять ка компрессор не запускается", TextIntent.DIAGNOSTICS, "3es5k"),
            Probe("чмэ три тэ дизель заглох", TextIntent.DIAGNOSTICS, "chme3t"),
            Probe("чмэ три э дизель заглох", TextIntent.DIAGNOSTICS, "chme3e"),
            Probe("тэм два у двигатель глохнет", TextIntent.DIAGNOSTICS, "tem2u"),
            Probe("тэм два двигатель глохнет", TextIntent.DIAGNOSTICS, "tem2"),
            Probe("ЧМЭ3 дизель заглох", TextIntent.DIAGNOSTICS, "chme3"),
            Probe("ВЛ80С ТЭД искрит", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С АКБ не заряжается", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С ЭПК не срабатывает", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С ВР 483 травит", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С нет индикации", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С тягу не берет", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С компрессор не останавливается", TextIntent.DIAGNOSTICS, "vl80s"),
            Probe("ВЛ80С главный выключатель", TextIntent.REFERENCE, "vl80s"),
            Probe("что такое компрессор", TextIntent.REFERENCE),
            Probe("схема ТЭМ2", TextIntent.SCHEME, "tem2"),
            Probe("осмотр локомотива ЧМЭ3", TextIntent.ACCEPTANCE, "chme3"),
            Probe("человек без сознания", TextIntent.SAFETY),
            Probe("человек не дышит", TextIntent.SAFETY),
            Probe("первая помощь", TextIntent.SAFETY),
        )
        assertTrue(cases.size >= 25)
        cases.forEach { case ->
            val parsed = TextQueryParser.parse(case.phrase)
            assertEquals(case.phrase, case.intent, parsed.intent)
            assertEquals(case.phrase, case.model?.let { setOf(ModelId(it)) } ?: emptySet<ModelId>(),
                parsed.explicitModels)
        }
    }

    @Test fun modelBoundariesNegationAndAmbiguityArePreserved() {
        assertEquals(setOf(ModelId("chme3e")),
            TextQueryParser.parse("ЧМЭ3Э не запускается").explicitModels)
        assertEquals(setOf(ModelId("tem2u")),
            TextQueryParser.parse("ТЭМ2У не запускается").explicitModels)
        assertEquals(setOf(ModelId("2es5k"), ModelId("3es5k")),
            TextQueryParser.parse("2ЭС5К и 3ЭС5К компрессор").explicitModels)
        assertTrue(TextQueryParser.parse("Ермак компрессор").ermakUnspecified)
        assertFalse(TextQueryParser.parse("2ЭС5К Ермак компрессор").ermakUnspecified)
        assertNotEquals(TextQueryParser.normalize("ГВ не включается"),
            TextQueryParser.normalize("ГВ не выключается"))
        assertNotEquals(TextQueryParser.normalize("ТМ"), TextQueryParser.normalize("ПМ"))
        assertFalse(TextQueryParser.parse("датчик тока").intent == TextIntent.SAFETY)
    }

    private fun entry(
        id: String,
        title: String,
        type: ContentType,
        refs: Set<String> = emptySet(),
        owner: ContentOwner = ContentOwner.Model(vl),
        status: PublicationStatus = PublicationStatus.ACTIVE,
        disposition: ActionDisposition = ActionDisposition.INFORMATION_ONLY,
        sourceStatus: SourceStatus = SourceStatus.UNKNOWN,
        provenance: ProvenanceClass = ProvenanceClass.UNKNOWN,
    ) = ContentEntry(
        id = CanonicalId(id), type = type, owner = owner,
        applicability = Applicability(),
        publicationStatus = status, provenance = provenance, sourceStatus = sourceStatus,
        actionDisposition = disposition, title = title, sourceRefs = refs,
    )

    private fun fixture(vararg entries: ContentEntry): Pair<ContentRegistry, AssistantTextEngine> {
        val registry = ContentRegistry()
        val pack = ContentPack(
            ContentPackManifest(1, PackId("lexical"), "1.0", null, emptySet(),
                emptySet(), "ru-RU", entries.map { it.id }.toSet(), "1", "test", emptyMap()),
            entries.toList()
        )
        assertTrue(registry.install(pack).isEmpty())
        return registry to AssistantTextEngine(registry, setOf(vl))
    }

    @Test fun fullRouteChecksCanonicalCardAndSourceWithoutInventingAdvice() {
        val source = entry("source-official", "Руководство завода", ContentType.SOURCE,
            sourceStatus = SourceStatus.CURRENT, provenance = ProvenanceClass.MANUFACTURER)
        val pantograph = entry("pantograph-no-rise", "Токоприемник не поднимается",
            ContentType.DIAGNOSTIC_SCENARIO, refs = setOf("source-official"))
        val other = entry("pantograph-no-lower", "Токоприемник не опускается",
            ContentType.DIAGNOSTIC_SCENARIO, refs = setOf("source-official"))
        val (registry, engine) = fixture(source, pantograph, other)
        val probes = listOf("ВЛ80С пантограф не поднимается",
            "вл 80 с токоприемнек не поднимается",
            "ВЛ80С токоприемник не поднимается")
        probes.forEach { phrase ->
            val result = engine.query(phrase, vl)
            assertTrue("$phrase => $result", result is TextAssistantResult.Matches)
            result as TextAssistantResult.Matches
            assertEquals(TextIntent.DIAGNOSTICS, result.intent)
            assertEquals("pantograph-no-rise", result.hits.first().entry.id.value)
            assertTrue("$phrase: contradictory result leaked",
                result.hits.none { it.entry.id.value == "pantograph-no-lower" })
            assertEquals(setOf("source-official"), result.hits.first().sourceIds)
            assertTrue(result.hits.first().sourceVerified)
            val opened = AssistantUiNavigationGate.openHit(result,
                ContentTarget(pantograph.id, pantograph.type), registry, setOf(vl))
            assertEquals("pantograph-no-rise", opened?.id?.value)
            assertNull(result.recommended) // Never auto-open a diagnostic card.
        }
    }

    @Test fun lexicalExpansionCannotBypassQuarantineOrInventSources() {
        val source = entry("unverified", "Неизвестная схема", ContentType.SOURCE)
        val diagnostic = entry("candidate", "Главный выключатель не включается",
            ContentType.DIAGNOSTIC_SCENARIO, refs = setOf("unverified"))
        val candidate = entry("research", "Токоприемник не поднимается",
            ContentType.DIAGNOSTIC_SCENARIO, status = PublicationStatus.CANDIDATE)
        val equipment = entry("equipment", "Главный выключатель", ContentType.EQUIPMENT)
        val (_, engine) = fixture(source, diagnostic, candidate, equipment)
        assertTrue(engine.query("ВЛ80С главник не включается", vl) is TextAssistantResult.NoMatches)
        assertTrue(engine.query("ВЛ80С пантограф не поднимается", vl) is TextAssistantResult.NoMatches)
        assertTrue(engine.query("ВЛ80С не работает", vl) is TextAssistantResult.NoMatches)
        assertEquals(TextAssistantResult.UnpublishedModel(ModelId("2es5k")),
            engine.query("2ЭС5К главник", vl))
        assertTrue(engine.query("ВЛ80С и ЧМЭ3 главный выключатель", vl)
            is TextAssistantResult.ClarifyModel)
    }

    @Test fun everyUnpublishedFamilyFailsClosedEvenWithRecognizedSynonyms() {
        val (_, engine) = fixture(entry("breaker", "Главный выключатель", ContentType.EQUIPMENT))
        val cases = mapOf(
            "2ЭС5К главник" to "2es5k",
            "3ЭС5К ГВ" to "3es5k",
            "ЧМЭ3 компрессор" to "chme3",
            "ЧМЭ3Т компрессор" to "chme3t",
            "ЧМЭ3Э компрессор" to "chme3e",
            "ТЭМ2 компрессор" to "tem2",
            "ТЭМ2У компрессор" to "tem2u"
        )
        cases.forEach { (query, id) ->
            assertEquals(query, TextAssistantResult.UnpublishedModel(ModelId(id)),
                engine.query(query, vl))
        }
    }

    @Test fun referenceSynonymsFindTheSamePublishedCard() {
        val (_, engine) = fixture(entry("breaker", "Главный выключатель", ContentType.EQUIPMENT))
        listOf("ВЛ80С главник", "ВЛ80С ГВ", "вээл восемьдесят эс гэ вэ",
            "ВЛ80С главный выключатель").forEach { phrase ->
            val result = engine.query(phrase, vl)
            assertTrue("$phrase => $result", result is TextAssistantResult.Matches)
            assertEquals("breaker", (result as TextAssistantResult.Matches).hits.first().entry.id.value)
        }
    }
}
