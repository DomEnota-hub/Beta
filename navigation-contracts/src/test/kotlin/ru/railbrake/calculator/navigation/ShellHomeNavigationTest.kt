package ru.railbrake.calculator.navigation

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ModelId

class ShellHomeNavigationTest {
    @Test fun onlyPublishedVl80sCanOpenExistingRuntimeFeatures() {
        listOf(
            ShellHomeDestination.ATLAS,
            ShellHomeDestination.DIAGNOSTICS,
            ShellHomeDestination.ACCEPTANCE,
        ).forEach { destination ->
            assertEquals(
                ShellHomeRoute.PublishedModelFeature(ModelId("vl80s"), destination),
                ShellHomeNavigationPolicy.resolve("vl80s", destination),
            )
        }
    }

    @Test fun everyUnpublishedModelFailsClosedForAllRuntimeRoutes() {
        WorkingModelCatalog.models.filterNot { it.runtimePublished }.forEach { model ->
            listOf(
                ShellHomeDestination.ATLAS,
                ShellHomeDestination.DIAGNOSTICS,
                ShellHomeDestination.ACCEPTANCE,
                ShellHomeDestination.ASSISTANT,
            ).forEach { destination ->
                assertEquals(
                    ShellHomeRoute.Unavailable(destination, model.id),
                    ShellHomeNavigationPolicy.resolve(model.id.value, destination),
                )
            }
        }
    }

    @Test fun unimplementedFeaturesNeverClaimToBePublished() {
        listOf(
            ShellHomeDestination.ASSISTANT,
            ShellHomeDestination.CALCULATIONS,
            ShellHomeDestination.RECORDS,
            ShellHomeDestination.KNOWLEDGE,
            ShellHomeDestination.TRAFFIC_SAFETY,
            ShellHomeDestination.OCCUPATIONAL_SAFETY,
            ShellHomeDestination.FIRST_AID,
            ShellHomeDestination.APPEARANCE,
            ShellHomeDestination.SETTINGS,
            ShellHomeDestination.ABOUT,
        ).forEach { destination ->
            assertTrue(
                ShellHomeNavigationPolicy.resolve("vl80s", destination) is ShellHomeRoute.Unavailable
            )
        }
    }

    @Test fun missingOrUnknownModelCannotEnterModelFeatures() {
        listOf(null, "", "VL80S", "chme3x").forEach { model ->
            assertEquals(
                ShellHomeRoute.ModelSelectionRequired,
                ShellHomeNavigationPolicy.resolve(model, ShellHomeDestination.ATLAS),
            )
        }
    }

    @Test fun commonSectionsNeverGuessModel() {
        assertEquals(
            ShellHomeRoute.Unavailable(ShellHomeDestination.KNOWLEDGE, null),
            ShellHomeNavigationPolicy.resolve(null, ShellHomeDestination.KNOWLEDGE),
        )
    }
}
