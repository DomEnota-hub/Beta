"""Apply only stage 1: responsive Ermak diagnostics and indexed canonical links."""
from pathlib import Path
import shutil
import re
import sys

root = Path(sys.argv[1])
here = Path(__file__).parent
core = root / 'app/src/main/java/ru/railbrake/calculator/core'
ui = root / 'app/src/main/java/ru/railbrake/calculator/ui'
p = core / 'TechnicalDataRepository.kt'
t = p.read_text()
start = t.index('    private fun ermakCanonicalRelated(id: String): List<String> {')
end = t.index('    private fun sectionEntries(', start)
t = t[:start] + '''    private val ermakRelatedIndex by lazy { ErmakRelatedIndex(ermakStage7) }

    private fun ermakCanonicalRelated(id: String): List<String> = ermakRelatedIndex.relatedTo(id)

''' + t[end:]
# Normalization runs on every line while building the search index. Compile its
# identical patterns once, preserving the exact replacements and data output.
start = t.index('internal fun isInternalTechnicalReference')
tail = t[start:]
patterns = re.findall(r'Regex\("(?:\\.|[^"\\])*"(?:, RegexOption\.\w+)?\)', tail)
names = ['internalReferencePattern', 'variantProfilePattern', 'equipmentCardsPattern',
         'equipmentAbbreviationPattern', 'embeddedReferencePattern', 'multipleSpacesPattern', 'multipleBulletsPattern']
assert len(patterns) == len(names), patterns
for name, pattern in zip(names, patterns):
    tail = tail.replace(pattern, name, 1)
t = t[:start] + '\n'.join(f'private val {name} = {pattern}' for name, pattern in zip(names, patterns)) + '\n\n' + tail
p.write_text(t)
shutil.copyfile(here / 'ErmakRelatedIndex.kt', core / 'ErmakRelatedIndex.kt')
shutil.copyfile(here / 'ErmakRelatedIndexTest.kt', root / 'app/src/test/java/ru/railbrake/calculator/core/ErmakRelatedIndexTest.kt')

p = ui / 'LocomotiveDiagnosticsScreen.kt'
t = p.read_text()
t = t.replace('import androidx.compose.ui.Modifier', '''import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import ru.railbrake.calculator.core.TechnicalDataRepository''')
old = '            else TechnicalCatalogScreen('
assert t.count(old) == 1
t = t.replace(old, '            else ErmakDiagnosticsLoaded { TechnicalCatalogScreen(')
old = '''            )
        }
    }
}'''
assert t.count(old) == 1
t = t.replace(old, '''            ) }
        }
    }
}''')
t += '''
@Composable
private fun ErmakDiagnosticsLoaded(content: @Composable () -> Unit) {
    val appContext = LocalContext.current.applicationContext
    var attempt by remember { mutableIntStateOf(0) }
    val loaded by produceState<Result<Unit>?>(initialValue = null, key1 = attempt) {
        value = null
        value = withContext(Dispatchers.Default) {
            runCatching {
                TechnicalDataRepository(appContext).entries(TechnicalFamily.ERMAK, TechnicalSection.DIAGNOSTICS)
                Unit
            }
        }
    }
    when {
        loaded == null -> Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            CircularProgressIndicator()
            Text("Загрузка диагностики Ермака…")
        }
        loaded?.isSuccess == true -> content()
        else -> Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("Не удалось загрузить диагностику Ермака")
            Button(onClick = { attempt++ }) { Text("Повторить") }
        }
    }
}
'''
p.write_text(t)
print('Stage 1 series loading fix applied')
