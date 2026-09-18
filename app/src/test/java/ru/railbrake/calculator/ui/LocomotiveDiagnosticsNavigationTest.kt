package ru.railbrake.calculator.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
import ru.railbrake.calculator.core.TechnicalFamily

class LocomotiveDiagnosticsNavigationTest {
    @Test
    fun ermakDeepLinksSelectErmak() {
        assertEquals(TechnicalFamily.ERMAK, diagnosticInitialFamily("ER-DIAG-001", null))
        assertEquals(TechnicalFamily.ERMAK, diagnosticInitialFamily(null, "ER-EQ-001"))
    }

    @Test
    fun familySwitchNeverPassesForeignDeepLink() {
        assertNull(diagnosticScenarioForFamily("ER-DIAG-001", TechnicalFamily.VL80S))
        assertNull(diagnosticEquipmentForFamily("ER-EQ-001", TechnicalFamily.VL80S))
        assertNull(diagnosticScenarioForFamily("pantograph-down", TechnicalFamily.ERMAK))
        assertNull(diagnosticEquipmentForFamily("VL-EQ-PANTOGRAPH", TechnicalFamily.ERMAK))
    }

    @Test
    fun matchingDeepLinksArePreserved() {
        assertEquals("pantograph-down", diagnosticScenarioForFamily("pantograph-down", TechnicalFamily.VL80S))
        assertEquals("ER-DIAG-001", diagnosticScenarioForFamily("ER-DIAG-001", TechnicalFamily.ERMAK))
    }
}
