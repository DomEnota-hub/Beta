package ru.railbrake.calculator.core

import org.junit.Assert.assertTrue
import org.junit.Test

class DiagnosticGenericRouteRegressionTest {
    @Test
    fun strictGenericRoutesStayBelowReworkCheckpoint() {
        val genericRoot = "Признак относится только к одной секции, тележке или группе?"
        val strictGeneric = DiagnosticRepository.scenarios.count { scenario ->
            scenario.questions.firstOrNull()?.text == genericRoot
        }
        println("VL80S_STRICT_GENERIC_ROUTES=$strictGeneric")
        assertTrue("strict generic routes regressed: $strictGeneric", strictGeneric <= 30)
    }
}
