package ru.railbrake.calculator.shell

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.assertEquals
import org.junit.Test
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.navigation.ShellHomeDestination

class FamilyReferencePreviewPolicyTest {
    private val tem2 = FamilyProfiles.forModel(ModelId("tem2"))!!
    private val base = FamilyReferencePreview(
        id = "donor-summary.tem2", modelId = "tem2", executionId = "tem2",
        scope = ReferenceScope.DONOR_VARIANT, title = "Маслоотделитель",
        summary = "Подготовка воздуха", donorPath = "app/src/main/assets/technical/tem2_tem2_catalog.json",
        donorBlobSha = "c7a94c1cd2687b84de4358b80773e3156c6b93d7",
    )
    private fun show(
        entry: FamilyReferencePreview = base,
        model: FamilyModelProfile = tem2,
        execution: VariantId? = VariantId("tem2"),
        destination: ShellHomeDestination = ShellHomeDestination.ATLAS,
    ) = FamilyReferencePreviewPolicy.canShow(entry, model, execution, destination)

    @Test fun exactDonorVariantIsReferenceOnlyAfterExplicitSelection() {
        assertTrue(show())
        assertFalse(show(execution = null))
        assertFalse(show(execution = VariantId("tem2u")))
        assertFalse(show(model = FamilyProfiles.forModel(ModelId("tem2u"))!!))
        assertFalse(show(destination = ShellHomeDestination.DIAGNOSTICS))
        assertFalse(show(destination = ShellHomeDestination.ACCEPTANCE))
    }

    @Test fun unknownExecutionAndForeignModelFailClosed() {
        assertFalse(show(execution = VariantId("not-a-variant")))
        assertFalse(show(entry = base.copy(modelId = "chme3")))
        assertFalse(show(entry = base.copy(executionId = "tem2u")))
        assertFalse(show(entry = base.copy(donorBlobSha = "unverified")))
        assertFalse(show(entry = base.copy(summary = "")))
    }

    @Test fun searchIsScopedBeforeMatchingAndDoesNotLeakOtherModels() {
        val other = base.copy(id = "donor-summary.tem2u", modelId = "tem2u",
            executionId = "tem2u", title = "Скрытый реверсор")
        val candidates = listOf(base, other, base.copy(id = "donor-summary.tem2.second",
            title = "Тормозной резервуар", summary = "Пневматическая система"))
        val matches = FamilyReferencePreviewPolicy.search(candidates, tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS, "масло")
        assertEquals(listOf(base.id), matches.map { it.id })
        assertTrue(FamilyReferencePreviewPolicy.search(candidates, tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS, "скрытый").isEmpty())
        assertTrue(FamilyReferencePreviewPolicy.search(candidates, tem2,
            null, ShellHomeDestination.ATLAS, "").isEmpty())
        assertTrue(FamilyReferencePreviewPolicy.search(candidates, tem2,
            VariantId("tem2"), ShellHomeDestination.ACCEPTANCE, "").isEmpty())
        assertEquals(2, FamilyReferencePreviewPolicy.search(candidates, tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS, "").size)
    }

    @Test fun normalizedMultiwordSearchUsesOnlyVisibleSummaryAndKeepsExecutionGate() {
        val matches = FamilyReferencePreviewPolicy.search(listOf(base), tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS, "воздуха подготовка")
        assertEquals(listOf(base.id), matches.map { it.id })
        assertTrue(FamilyReferencePreviewPolicy.search(listOf(base), tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS,
            "подготовка воздуха несуществующий").isEmpty())
        assertTrue(FamilyReferencePreviewPolicy.search(listOf(base), tem2,
            VariantId("tem2u"), ShellHomeDestination.ATLAS,
            "воздуха подготовка").isEmpty())
    }


    @Test fun singleExecutionReferenceReadableBeforeSelectionButNotExecutable() {
        assertTrue(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            base, tem2, ShellHomeDestination.ATLAS))
        assertFalse(show(execution = null)) // Published/execution-scoped path stays closed.
        assertFalse(FamilyCatalogLoadPolicy.shouldLoad(
            tem2, null, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            base, tem2, ShellHomeDestination.ACCEPTANCE))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            base.copy(modelId = "tem2u"), tem2, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            base.copy(donorBlobSha = "unverified"), tem2, ShellHomeDestination.ATLAS))
        assertEquals(listOf(base.id), FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(base), tem2, ShellHomeDestination.ATLAS, "воздуха подготовка"
        ).map { it.id })
    }

    @Test fun multiExecutionUnknownOnlyExposesGeneralUnverifiedSummaries() {
        val ermak = FamilyProfiles.forModel(ModelId("2es5k"))!!
        val general = base.copy(
            id = "ermak-general", modelId = "2es5k", executionId = null,
            scope = ReferenceScope.EXECUTION_UNVERIFIED,
        )
        val msudN = general.copy(
            id = "ermak-n", scope = ReferenceScope.DONOR_VARIANT,
            executionId = "2es5k_msud_n",
        )
        assertTrue(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            general, ermak, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            msudN, ermak, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            general.copy(modelId = "3es5k"), ermak, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            general.copy(executionId = "2es5k_msud_n"), ermak,
            ShellHomeDestination.ATLAS))
        assertEquals(listOf(general.id), FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(general, msudN), ermak, ShellHomeDestination.ATLAS, ""
        ).map { it.id })
        assertFalse(FamilyReferencePreviewPolicy.canShow(
            general, ermak, null, ShellHomeDestination.ATLAS))
        assertFalse(FamilyCatalogLoadPolicy.shouldLoad(
            ermak, null, ShellHomeDestination.ATLAS))
    }

    @Test fun chme3tSerialSplitCannotLeakVariantSummaryWithoutSelection() {
        val chme3t = FamilyProfiles.forModel(ModelId("chme3t"))!!
        val before = base.copy(
            id = "chme3t-before", modelId = "chme3t",
            executionId = "chme3t_pre6245",
        )
        val after = before.copy(
            id = "chme3t-after", executionId = "chme3t_from6245",
        )
        assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(before, after), chme3t, ShellHomeDestination.ATLAS, ""
        ).isEmpty())
        assertEquals(listOf(before.id), FamilyReferencePreviewPolicy.search(
            listOf(before, after), chme3t, VariantId("chme3t_pre6245"),
            ShellHomeDestination.ATLAS, ""
        ).map { it.id })
    }

    @Test fun familyGeneralReferenceIsNeverPresentedAsVerifiedExecution() {
        val ermak = FamilyProfiles.forModel(ModelId("2es5k"))!!
        val general = base.copy(
            modelId = "2es5k", executionId = null,
            scope = ReferenceScope.EXECUTION_UNVERIFIED,
        )
        assertTrue(show(general, ermak, VariantId("2es5k_msud_n")))
        assertTrue(show(general, ermak, VariantId("2es5k_msud_015")))
        assertFalse(show(general, ermak, VariantId("3es5k_msud_n")))
        assertFalse(show(general.copy(executionId = "2es5k_msud_n"),
            ermak, VariantId("2es5k_msud_n")))
        assertFalse(show(general.copy(scope = ReferenceScope.DONOR_VARIANT),
            ermak, VariantId("2es5k_msud_n")))
    }
    @Test fun ermakSystemDetailsRemainReferenceOnlyAndSearchable() {
        val profile = FamilyProfiles.forModel(ModelId("2es5k"))!!
        val entry = base.copy(modelId = "2es5k", executionId = null,
            scope = ReferenceScope.EXECUTION_UNVERIFIED,
            donorPath = "app/src/main/assets/technical/ermak_knowledge.json.gz",
            donorBlobSha = "08d164fc11c33c241d04ad6ad60c13a3aec996c8",
            donorId = "ER-KB-SYS-20")
        assertTrue(FamilyReferenceDetails.forEntry(entry)!!.sourceIds.contains("ER-SRC-001"))
        assertEquals(null, FamilyReferenceDetails.forEntry(entry.copy(modelId = "tem2")))
        assertEquals(null, FamilyReferenceDetails.forEntry(entry.copy(donorBlobSha = "wrong")))
        assertEquals(null, FamilyReferenceDetails.forEntry(entry.copy(executionId = "2es5k_msud_n")))
        assertEquals(listOf(entry.id), FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(entry), profile, ShellHomeDestination.ATLAS, "реакторы").map { it.id })
        assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(entry), profile, ShellHomeDestination.DIAGNOSTICS, "реакторы").isEmpty())
    }

    @Test fun allErmakSystemPrinciplesAreAvailableForBothModelsOnly() {
        val ids = listOf("10", "20", "21", "30", "40", "50", "60", "70", "71", "80", "90", "91")
        for (model in listOf("2es5k", "3es5k")) {
            val profile = FamilyProfiles.forModel(ModelId(model))!!
            val entries = ids.map { id ->
                base.copy(id = "$model-$id", modelId = model, executionId = null,
                    scope = ReferenceScope.EXECUTION_UNVERIFIED,
                    donorPath = "app/src/main/assets/technical/ermak_knowledge.json.gz",
                    donorBlobSha = "08d164fc11c33c241d04ad6ad60c13a3aec996c8",
                    donorId = "ER-KB-SYS-$id")
            }
            assertEquals(12, entries.count { FamilyReferenceDetails.forEntry(it)?.description?.isNotBlank() == true })
            assertTrue(entries.all { FamilyReferenceDetails.forEntry(it)!!.sourceIds.isNotEmpty() })
            assertEquals(12, FamilyReferencePreviewPolicy.searchBeforeExecution(
                entries, profile, ShellHomeDestination.ATLAS, "").size)
            assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(
                entries, profile, ShellHomeDestination.ACCEPTANCE, "").isEmpty())
            assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(
                entries, profile, ShellHomeDestination.DIAGNOSTICS, "").isEmpty())
            assertEquals(listOf("$model-70"), FamilyReferencePreviewPolicy.searchBeforeExecution(
                entries, profile, ShellHomeDestination.ATLAS, "программное обеспечение").map { it.id })
            assertEquals(null, FamilyReferenceDetails.forEntry(entries.first().copy(donorId = "unknown")))
            assertEquals(null, FamilyReferenceDetails.forEntry(entries.first().copy(donorPath = "other")))
        }
    }
    @Test fun ermakEquipmentPrinciplesAreSearchableAndNeverExecutionApproved() {
        val ids = (1..10).flatMap { n -> listOf("ER-EQ-HV-%03d".format(n), "ER-EQ-TR-%03d".format(n)) }
        for (model in listOf("2es5k", "3es5k")) {
            val profile = FamilyProfiles.forModel(ModelId(model))!!
            val entries = ids.map { id -> base.copy(id = "$model-$id", modelId = model,
                executionId = null, scope = ReferenceScope.EXECUTION_UNVERIFIED,
                donorPath = "app/src/main/assets/technical/ermak_equipment.json.gz",
                donorBlobSha = "47a8d2424d69943fba9747746aa6ad8c8f4e2e98", donorId = id) }
            assertEquals(20, entries.count { FamilyReferenceDetails.forEntry(it)?.sourceIds?.isNotEmpty() == true })
            assertEquals(20, FamilyReferencePreviewPolicy.searchBeforeExecution(entries, profile,
                ShellHomeDestination.ATLAS, "").size)
            assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(entries, profile,
                ShellHomeDestination.DIAGNOSTICS, "").isEmpty())
            assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(entries, profile,
                ShellHomeDestination.ACCEPTANCE, "").isEmpty())
            assertEquals(listOf("$model-ER-EQ-HV-002"), FamilyReferencePreviewPolicy.searchBeforeExecution(
                entries, profile, ShellHomeDestination.ATLAS, "катушка").map { it.id })
            assertEquals(null, FamilyReferenceDetails.forEntry(entries.first().copy(donorBlobSha = "wrong")))
            assertEquals(null, FamilyReferenceDetails.forEntry(entries.first().copy(executionId = "${model}_msud_n")))
            assertEquals(null, FamilyReferenceDetails.forEntry(entries.first().copy(modelId = "tem2")))
        }
    }

    @Test fun remainingBaseErmakEquipmentHasReferenceOnlyDetails() {
        val ids = listOf("ER-EQ-TR-011", "ER-EQ-TR-012", "ER-EQ-AU-001", "ER-EQ-AU-002", "ER-EQ-AU-003", "ER-EQ-AU-004", "ER-EQ-AU-005", "ER-EQ-AU-006", "ER-EQ-AU-007", "ER-EQ-AU-008", "ER-EQ-AU-009", "ER-EQ-CT-001", "ER-EQ-CT-002", "ER-EQ-CT-003", "ER-EQ-CT-004", "ER-EQ-CT-005", "ER-EQ-CT-006", "ER-EQ-CT-007", "ER-EQ-CT-008", "ER-EQ-CT-010", "ER-EQ-CT-011", "ER-EQ-CT-012", "ER-EQ-CT-013", "ER-EQ-PN-001", "ER-EQ-PN-002", "ER-EQ-PN-003", "ER-EQ-PN-004", "ER-EQ-PN-005", "ER-EQ-PN-006", "ER-EQ-PN-007", "ER-EQ-PN-008", "ER-EQ-PN-009", "ER-EQ-PN-010", "ER-EQ-PN-011", "ER-EQ-PN-012", "ER-EQ-BR-001", "ER-EQ-BR-002", "ER-EQ-BR-004", "ER-EQ-BR-005", "ER-EQ-BR-006", "ER-EQ-BR-007", "ER-EQ-BR-011", "ER-EQ-BR-012", "ER-EQ-BR-013", "ER-EQ-SF-001", "ER-EQ-SF-002", "ER-EQ-SF-003", "ER-EQ-SF-004", "ER-EQ-SF-005", "ER-EQ-SF-006", "ER-EQ-SF-008", "ER-EQ-SF-009", "ER-EQ-PR-001", "ER-EQ-PR-002", "ER-EQ-PR-003", "ER-EQ-PR-004", "ER-EQ-PR-005", "ER-EQ-PR-006", "ER-EQ-PR-007", "ER-EQ-FR-001", "ER-EQ-FR-002", "ER-EQ-FR-003", "ER-EQ-FR-004", "ER-EQ-MC-001", "ER-EQ-MC-002", "ER-EQ-MC-003", "ER-EQ-MC-004", "ER-EQ-MC-006", "ER-EQ-MC-007", "ER-EQ-MC-008", "ER-EQ-MC-009", "ER-EQ-MC-010", "ER-EQ-MC-012", "ER-EQ-CB-001", "ER-EQ-CB-002", "ER-EQ-CB-003", "ER-EQ-CB-004", "ER-EQ-CB-005", "ER-EQ-CB-006")
        val excluded = listOf("ER-EQ-TR-013", "ER-EQ-CT-009", "ER-EQ-BR-003", "ER-EQ-BR-008", "ER-EQ-BR-009", "ER-EQ-BR-010", "ER-EQ-BR-014", "ER-EQ-BR-015", "ER-EQ-SF-007", "ER-EQ-SF-010", "ER-EQ-MC-005", "ER-EQ-MC-011")
        for (model in listOf("2es5k", "3es5k")) {
            val profile = FamilyProfiles.forModel(ModelId(model))!!
            fun entry(id: String) = base.copy(id = "$model-$id", modelId = model,
                executionId = null, scope = ReferenceScope.EXECUTION_UNVERIFIED,
                donorPath = "app/src/main/assets/technical/ermak_equipment.json.gz",
                donorBlobSha = "47a8d2424d69943fba9747746aa6ad8c8f4e2e98", donorId = id)
            val entries = ids.map { entry(it) }
            assertEquals(79, entries.count { FamilyReferenceDetails.forEntry(it)?.sourceIds?.isNotEmpty() == true })
            assertEquals(79, FamilyReferencePreviewPolicy.searchBeforeExecution(entries, profile, ShellHomeDestination.ATLAS, "").size)
            assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(entries, profile, ShellHomeDestination.DIAGNOSTICS, "").isEmpty())
            assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(entries, profile, ShellHomeDestination.ACCEPTANCE, "").isEmpty())
            assertTrue(excluded.filter { it !in setOf("ER-EQ-TR-013", "ER-EQ-CT-009", "ER-EQ-SF-010") }.all { FamilyReferenceDetails.forEntry(entry(it)) != null })
            for (id in listOf("ER-EQ-TR-013", "ER-EQ-CT-009")) {
                val late = entry(id).copy(scope = ReferenceScope.DONOR_VARIANT, executionId = "${model}_msud_015")
                assertEquals(null, FamilyReferenceDetails.forEntry(entry(id)))
                assertTrue(FamilyReferenceDetails.forEntry(late) != null)
                assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(late, profile, ShellHomeDestination.ATLAS))
                assertFalse(FamilyReferencePreviewPolicy.canShow(late, profile, VariantId("${model}_msud_n"), ShellHomeDestination.ATLAS))
                assertTrue(FamilyReferencePreviewPolicy.canShow(late, profile, VariantId("${model}_msud_015"), ShellHomeDestination.ATLAS))
            }
            assertEquals(model == "2es5k", FamilyReferenceDetails.forEntry(entry("ER-EQ-SF-010")) != null)
            assertTrue(FamilyReferenceDetails.forEntry(entry("ER-EQ-CB-001"))!!.description.contains("не к бустерной"))
        }
    }
}
