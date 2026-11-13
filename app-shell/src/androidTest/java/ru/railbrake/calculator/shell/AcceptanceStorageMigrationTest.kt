package ru.railbrake.calculator.shell

import android.content.Context
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.Assert.*
import org.junit.runner.RunWith
import ru.railbrake.calculator.acceptance.AcceptanceCheckState
import ru.railbrake.calculator.acceptance.AcceptanceItemState
import ru.railbrake.calculator.acceptance.SharedPreferencesAcceptanceStateStore
import ru.railbrake.calculator.domain.CanonicalId

@RunWith(AndroidJUnit4::class)
class AcceptanceStorageMigrationTest {
    // Instrumentation package, never the user's target application preferences.
    private val context = InstrumentationRegistry.getInstrumentation().context
    private val legacy get() = context.getSharedPreferences("technical_acceptance_states", Context.MODE_PRIVATE)
    private val beta get() = context.getSharedPreferences("railbrake_acceptance_state_v1", Context.MODE_PRIVATE)
    private val first = CanonicalId("VL80-ACC-001")
    private val second = CanonicalId("VL80-ACC-002")

    @Before fun setup() {
        assertNotEquals(InstrumentationRegistry.getInstrumentation().targetContext.packageName, context.packageName)
        reset()
    }

    @After fun reset() {
        assertTrue(legacy.edit().clear().commit())
        assertTrue(beta.edit().clear().commit())
    }

    @Test fun migrationWriteAndClearAcrossInstances() {
        assertTrue(legacy.edit().putString(first.value, "OK")
            .putString("note:${first.value}", "old")
            .putString(second.value, "BLOCKING").commit())
        val a = SharedPreferencesAcceptanceStateStore(context)
        val b = SharedPreferencesAcceptanceStateStore(context)
        assertEquals(AcceptanceItemState(AcceptanceCheckState.CHECKED, "old"), a.read(first))
        val updated = AcceptanceItemState(AcceptanceCheckState.NOTE, "new")
        b.write(first, updated)
        assertEquals(updated, a.read(first))
        a.clear(first)
        assertEquals(AcceptanceItemState(), b.read(first))
        assertEquals(AcceptanceItemState(), SharedPreferencesAcceptanceStateStore(context).read(first))
        assertTrue(beta.getBoolean("legacy_imported:${first.value}", false))
        assertEquals("OK", legacy.getString(first.value, null))
        assertEquals(AcceptanceCheckState.NOTE, b.read(second).state)
    }

    @Test fun existingAndMalformedBetaValuesAreNotOverwritten() {
        assertTrue(legacy.edit().putString(first.value, "OK").putString(second.value, "OK").commit())
        assertTrue(beta.edit().putString("note:${first.value}", "existing")
            .putInt("state:${second.value}", 42).commit())
        val store = SharedPreferencesAcceptanceStateStore(context)
        assertEquals(AcceptanceItemState(AcceptanceCheckState.NOT_CHECKED, "existing"), store.read(first))
        assertEquals(AcceptanceItemState(), store.read(second))
        assertEquals(42, beta.getInt("state:${second.value}", -1))
        assertFalse(beta.contains("legacy_imported:${second.value}"))
    }
}
