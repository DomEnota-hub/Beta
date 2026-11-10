package ru.railbrake.calculator.shell

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.navigation.ShellHomeDestination

class FamilyCatalogLoadPolicyTest {
    private val families = listOf(
        "2es5k", "3es5k", "chme3", "chme3t", "chme3e", "tem2", "tem2u",
    )

    @Test fun noFamilyAssetsLoadBeforeExecutionSelection() {
        for (id in families) {
            val profile = FamilyProfiles.forModel(ModelId(id))!!
            for (destination in listOf(
                ShellHomeDestination.ATLAS,
                ShellHomeDestination.ACCEPTANCE,
                ShellHomeDestination.DIAGNOSTICS,
            )) {
                assertFalse("$id $destination", FamilyCatalogLoadPolicy.shouldLoad(
                    profile, null, destination))
            }
        }
    }

    @Test fun onlyRegisteredExecutionCanLoadInformationalSections() {
        for (id in families) {
            val profile = FamilyProfiles.forModel(ModelId(id))!!
            for (execution in profile.executions) {
                assertTrue("$id ${execution.id.value} atlas",
                    FamilyCatalogLoadPolicy.shouldLoad(profile, execution.id,
                        ShellHomeDestination.ATLAS))
                assertTrue("$id ${execution.id.value} acceptance",
                    FamilyCatalogLoadPolicy.shouldLoad(profile, execution.id,
                        ShellHomeDestination.ACCEPTANCE))
            }
            assertFalse("$id foreign execution",
                FamilyCatalogLoadPolicy.shouldLoad(profile, VariantId("not-a-real-variant"),
                    ShellHomeDestination.ATLAS))
        }
    }

    @Test fun diagnosticsNeverReadUnpublishedFamilyPacks() {
        for (id in families) {
            val profile = FamilyProfiles.forModel(ModelId(id))!!
            for (execution in profile.executions) {
                assertFalse("$id diagnostics",
                    FamilyCatalogLoadPolicy.shouldLoad(profile, execution.id,
                        ShellHomeDestination.DIAGNOSTICS))
            }
        }
        val tem2 = FamilyProfiles.forModel(ModelId("tem2"))!!
        assertFalse(FamilyCatalogLoadPolicy.shouldLoad(tem2, VariantId("tem2u"),
            ShellHomeDestination.ATLAS))
        val ermak = FamilyProfiles.forModel(ModelId("2es5k"))!!
        assertFalse(FamilyCatalogLoadPolicy.shouldLoad(ermak, VariantId("3es5k_msud_n"),
            ShellHomeDestination.ACCEPTANCE))
    }
}
