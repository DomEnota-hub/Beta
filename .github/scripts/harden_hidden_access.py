from pathlib import Path

ROOT = Path('.')
APP_REPO = ROOT / 'app/src/main/java/ru/railbrake/calculator/data/SecretAccessRepository.kt'
PATCH_REPO = ROOT / 'patch/app/src/main/java/ru/railbrake/calculator/data/SecretAccessRepository.kt'
APP_UI = ROOT / 'app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt'
PATCH_UI = ROOT / 'patch/app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt'
APP_TEST = ROOT / 'app/src/test/java/ru/railbrake/calculator/ui/DeveloperEasterEggTest.kt'
PATCH_TEST = ROOT / 'patch/app/src/test/java/ru/railbrake/calculator/ui/DeveloperEasterEggTest.kt'

repo_text = '''package ru.railbrake.calculator.data

import android.content.Context

class SecretAccessRepository(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_FILE, Context.MODE_PRIVATE)
    private val stateMarker = mix64(context.packageName.hashCode().toLong() xor MARKER_SEED)

    init {
        migrateLegacyState(context)
    }

    fun isUnlocked(): Boolean = preferences.getLong(KEY_GATE, Long.MIN_VALUE) == stateMarker

    /**
     * Records a completed direct-calculation input and returns true only when it also matches
     * the private local feature signature. The unlock values are not stored as readable literals.
     */
    fun recordDirectCalculation(massTons: Double, axleCount: Int?): Boolean {
        if (!matchesLocalFeatureSignature(massTons, axleCount)) return false
        preferences.edit().putLong(KEY_GATE, stateMarker).apply()
        return true
    }

    fun showExamMaterialsInKnowledge(): Boolean =
        preferences.getBoolean(KEY_SHOW_IN_KNOWLEDGE, false)

    fun setShowExamMaterialsInKnowledge(show: Boolean) {
        preferences.edit().putBoolean(KEY_SHOW_IN_KNOWLEDGE, show).apply()
    }

    fun hide() {
        preferences.edit().remove(KEY_GATE).apply()
    }

    private fun migrateLegacyState(context: Context) {
        val legacy = context.getSharedPreferences(legacyPrefsName(), Context.MODE_PRIVATE)
        val oldGate = legacyUnlockKey()
        val oldShow = legacyShowKey()
        if (!isUnlocked() && legacy.getBoolean(oldGate, false)) {
            preferences.edit().putLong(KEY_GATE, stateMarker).apply()
        }
        if (!preferences.contains(KEY_SHOW_IN_KNOWLEDGE) && legacy.contains(oldShow)) {
            preferences.edit().putBoolean(KEY_SHOW_IN_KNOWLEDGE, legacy.getBoolean(oldShow, false)).apply()
        }
        if (legacy.contains(oldGate) || legacy.contains(oldShow)) {
            legacy.edit().remove(oldGate).remove(oldShow).apply()
        }
    }

    companion object {
        private const val PREFS_FILE = "local_feature_state_v2"
        private const val KEY_GATE = "s1"
        private const val KEY_SHOW_IN_KNOWLEDGE = "s2"
        private const val MARKER_SEED = -4942790177534073029L

        private fun legacyPrefsName(): String = charArrayOf(
            's', 'e', 'c', 'r', 'e', 't', '_', 'a', 'c', 'c', 'e', 's', 's'
        ).concatToString()

        private fun legacyUnlockKey(): String = charArrayOf(
            'e', 'x', 'a', 'm', '_', 'q', 'u', 'e', 's', 't', 'i', 'o', 'n', 's', '_',
            'u', 'n', 'l', 'o', 'c', 'k', 'e', 'd'
        ).concatToString()

        private fun legacyShowKey(): String = charArrayOf(
            'e', 'x', 'a', 'm', '_', 'm', 'a', 't', 'e', 'r', 'i', 'a', 'l', 's', '_',
            'i', 'n', '_', 'k', 'n', 'o', 'w', 'l', 'e', 'd', 'g', 'e'
        ).concatToString()
    }
}

internal fun matchesLocalFeatureSignature(massTons: Double, axleCount: Int?): Boolean {
    if (!massTons.isFinite() || axleCount == null) return false
    val folded = java.lang.Double.doubleToRawLongBits(massTons) xor
        (axleCount.toLong() * -2960836687051489901L) xor
        7640891576956012809L
    return mix64(folded) == -4380884985364558404L
}

private fun mix64(input: Long): Long {
    var value = input - 7046029254386353131L
    value = (value xor (value ushr 30)) * -4658895280553007687L
    value = (value xor (value ushr 27)) * -7723592293110705685L
    return value xor (value ushr 31)
}
'''

for target in (APP_REPO, PATCH_REPO):
    target.write_text(repo_text, encoding='utf-8')

for target in (APP_UI, PATCH_UI):
    text = target.read_text(encoding='utf-8')
    old_helper = '''internal fun isSecretExamAccessCode(massTons: Double, axleCount: Int?): Boolean =\n    abs(massTons - 1000.0) < 1e-9 && axleCount == 2381\n\n'''
    if old_helper not in text:
        raise SystemExit(f'Old secret helper not found in {target}')
    text = text.replace(old_helper, '', 1)
    text = text.replace(
        'var examQuestionsUnlocked by remember { mutableStateOf(secretAccessRepository.isUnlocked()) }',
        'var auxiliaryToolsVisible by remember { mutableStateOf(secretAccessRepository.isUnlocked()) }',
        1,
    )
    text = text.replace(
        'if (examQuestionsUnlocked) add(AppScreen.EXAM_QUESTIONS)',
        'if (auxiliaryToolsVisible) add(AppScreen.EXAM_QUESTIONS)',
        1,
    )
    old_callback = '''                        onExamQuestionsUnlocked = {\n                            secretAccessRepository.unlock()\n                            examQuestionsUnlocked = true\n                        }'''
    new_callback = '''                        onDirectCalculation = { massTons, axleCount ->\n                            if (secretAccessRepository.recordDirectCalculation(massTons, axleCount)) {\n                                auxiliaryToolsVisible = true\n                            }\n                        }'''
    if old_callback not in text:
        raise SystemExit(f'Old app callback not found in {target}')
    text = text.replace(old_callback, new_callback, 1)
    text = text.replace(
        'onExamQuestionsUnlocked: () -> Unit',
        'onDirectCalculation: (Double, Int?) -> Unit',
        1,
    )
    old_trigger = '''            if (source == MassSource.DIRECT && isSecretExamAccessCode(massValue, axleCount)) {\n                onExamQuestionsUnlocked()\n            }'''
    new_trigger = '''            if (source == MassSource.DIRECT) {\n                onDirectCalculation(massValue, axleCount)\n            }'''
    if old_trigger not in text:
        raise SystemExit(f'Old calculator trigger not found in {target}')
    text = text.replace(old_trigger, new_trigger, 1)
    text = text.replace(
        'examQuestionsUnlocked = false',
        'auxiliaryToolsVisible = false',
    )
    target.write_text(text, encoding='utf-8')

for target in (APP_TEST, PATCH_TEST):
    text = target.read_text(encoding='utf-8')
    if 'import ru.railbrake.calculator.data.matchesLocalFeatureSignature' not in text:
        text = text.replace(
            'import org.junit.Test\n',
            'import org.junit.Test\nimport ru.railbrake.calculator.data.matchesLocalFeatureSignature\n',
            1,
        )
    old = '''    @Test\n    fun examQuestionsCodeIsSeparateAndExact() {\n        assertTrue(isSecretExamAccessCode(massTons = 1000.0, axleCount = 2381))\n        assertFalse(isSecretExamAccessCode(massTons = 2381.0, axleCount = 999))\n        assertFalse(isSecretExamAccessCode(massTons = 1000.0, axleCount = 2380))\n        assertFalse(isSecretExamAccessCode(massTons = 999.9, axleCount = 2381))\n    }'''
    new = '''    @Test\n    fun localFeatureSignatureIsSeparateAndExact() {\n        assertTrue(matchesLocalFeatureSignature(massTons = 1000.0, axleCount = 2381))\n        assertFalse(matchesLocalFeatureSignature(massTons = 2381.0, axleCount = 999))\n        assertFalse(matchesLocalFeatureSignature(massTons = 1000.0, axleCount = 2380))\n        assertFalse(matchesLocalFeatureSignature(massTons = 999.9, axleCount = 2381))\n        assertFalse(matchesLocalFeatureSignature(massTons = Double.NaN, axleCount = 2381))\n        assertFalse(matchesLocalFeatureSignature(massTons = 1000.0, axleCount = null))\n    }'''
    if old not in text:
        raise SystemExit(f'Old access test not found in {target}')
    target.write_text(text.replace(old, new, 1), encoding='utf-8')

# Contract checks.
assert APP_REPO.read_text(encoding='utf-8') == PATCH_REPO.read_text(encoding='utf-8')
assert APP_UI.read_text(encoding='utf-8') == PATCH_UI.read_text(encoding='utf-8')
assert APP_TEST.read_text(encoding='utf-8') == PATCH_TEST.read_text(encoding='utf-8')
for target in (APP_UI, PATCH_UI):
    text = target.read_text(encoding='utf-8')
    assert 'isSecretExamAccessCode' not in text
    assert 'onExamQuestionsUnlocked' not in text
    assert 'auxiliaryToolsVisible' in text
for target in (APP_REPO, PATCH_REPO):
    text = target.read_text(encoding='utf-8')
    assert 'putBoolean(KEY_UNLOCKED' not in text
    assert 'recordDirectCalculation' in text
    assert 'matchesLocalFeatureSignature' in text

print('Hidden access hardening patch applied to app + patch mirrors.')
