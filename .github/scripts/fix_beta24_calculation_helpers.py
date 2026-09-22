from pathlib import Path

ROOT = Path('.')


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding='utf-8')


helpers = '''@Composable
private fun Metric(label: String, value: String, strong: Boolean = false) {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.Top) {
        Text(label, modifier = Modifier.weight(1f), style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, modifier = Modifier.weight(0.7f), style = MaterialTheme.typography.bodyMedium, fontWeight = if (strong) FontWeight.Black else FontWeight.SemiBold)
    }
}

@Composable
private fun MiniMetric(label: String, value: String) {
    Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.48f)) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 10.dp), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(label, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(value, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun Formula(text: String) {
    Surface(shape = RoundedCornerShape(14.dp), color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.52f)) {
        Text(text, modifier = Modifier.fillMaxWidth().padding(12.dp), style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
    }
}

'''

marker = '@Composable\nprivate fun StatusText(text: String, success: Boolean) {'

for path in [
    'app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt',
]:
    text = read(path)
    if 'private fun Metric(' in text or 'private fun MiniMetric(' in text or 'private fun Formula(' in text:
        raise SystemExit(f'{path}: helper already present; refusing duplicate insertion')
    if text.count(marker) != 1:
        raise SystemExit(f'{path}: expected one StatusText marker')
    text = text.replace(marker, helpers + marker, 1)
    write(path, text)

if read('app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt') != read('patch/app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt'):
    raise SystemExit('BrakeCalculatorApp mirror mismatch after repair')

value = read('app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt')
for name in ['Metric', 'MiniMetric', 'Formula', 'WarningBox', 'HeroResult']:
    if f'private fun {name}' not in value:
        raise SystemExit(f'missing helper: {name}')
