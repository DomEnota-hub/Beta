from pathlib import Path

ROOT = Path('.')


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one occurrence, found {count}')
    return text.replace(old, new, 1)


# Beta23: the interactive Ermak atlas deliberately keeps a dark canvas even
# when the application uses the light theme. Several Material controls inside
# that canvas were still inheriting the light app color scheme, which made
# secondary text and inactive controls dark-on-dark. Give those controls
# explicit high-contrast colors while leaving the rest of the light theme
# untouched.
for path in [
    'app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt',
]:
    text = read(path)

    text = replace_once(
        text,
        '''            Text(\n                "Функциональная карта по встроенным данным компоновки. Зоны показывают принадлежность оборудования, но не заменяют заводской монтажный чертёж.",\n                style = MaterialTheme.typography.bodySmall,\n                color = MaterialTheme.colorScheme.onSurfaceVariant\n            )''',
        '''            Text(\n                "Функциональная карта по встроенным данным компоновки. Зоны показывают принадлежность оборудования, но не заменяют заводской монтажный чертёж.",\n                style = MaterialTheme.typography.bodySmall,\n                color = InteractiveSchemeMuted\n            )''',
        f'{path}: Ermak atlas description contrast',
    )

    text = replace_once(
        text,
        '''                    FilterChip(\n                        selected = entry.id == id,\n                        onClick = { target?.let(onOpen) },\n                        enabled = target != null,\n                        label = { Text(label) }\n                    )''',
        '''                    FilterChip(\n                        selected = entry.id == id,\n                        onClick = { target?.let(onOpen) },\n                        enabled = target != null,\n                        colors = FilterChipDefaults.filterChipColors(\n                            containerColor = Color.Transparent,\n                            labelColor = InteractiveSchemeMuted,\n                            selectedContainerColor = InteractiveSchemeAccent.copy(alpha = 0.18f),\n                            selectedLabelColor = InteractiveSchemeOnSurface,\n                            disabledContainerColor = Color.Transparent,\n                            disabledLabelColor = InteractiveSchemeMuted.copy(alpha = 0.72f)\n                        ),\n                        label = { Text(label) }\n                    )''',
        f'{path}: Ermak atlas variant chips',
    )

    text = replace_once(
        text,
        '''            OutlinedTextField(\n                value = query,\n                onValueChange = { query = it },\n                modifier = Modifier.fillMaxWidth(),\n                singleLine = true,\n                label = { Text("Найти аппарат на карте") }\n            )''',
        '''            OutlinedTextField(\n                value = query,\n                onValueChange = { query = it },\n                modifier = Modifier.fillMaxWidth(),\n                singleLine = true,\n                textStyle = MaterialTheme.typography.bodyLarge.copy(color = InteractiveSchemeOnSurface),\n                label = { Text("Найти аппарат на карте", color = InteractiveSchemeMuted) },\n                colors = androidx.compose.material3.OutlinedTextFieldDefaults.colors(\n                    focusedTextColor = InteractiveSchemeOnSurface,\n                    unfocusedTextColor = InteractiveSchemeOnSurface,\n                    cursorColor = InteractiveSchemeAccent,\n                    focusedBorderColor = InteractiveSchemeAccent,\n                    unfocusedBorderColor = InteractiveSchemeMuted.copy(alpha = 0.62f),\n                    focusedLabelColor = InteractiveSchemeAccent,\n                    unfocusedLabelColor = InteractiveSchemeMuted\n                )\n            )''',
        f'{path}: Ermak atlas search contrast',
    )

    write(path, text)


# Beta23 identity.
for path in ['app/build.gradle.kts', 'patch/app/build.gradle.kts']:
    text = read(path)
    text = replace_once(
        text,
        '// Beta22: first-class light/dark theme with light mode as default.',
        '// Beta23: improve contrast of dark interactive atlas controls in light mode.',
        f'{path}: beta comment',
    )
    text = replace_once(text, 'versionCode = 167', 'versionCode = 168', f'{path}: versionCode')
    text = replace_once(
        text,
        'versionName = "1.2.2-dev14-beta22"',
        'versionName = "1.2.2-dev14-beta23"',
        f'{path}: versionName',
    )
    write(path, text)


# Contract assertions.
app_ui = read('app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt')
patch_ui = read('patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt')
assert app_ui == patch_ui
assert 'color = InteractiveSchemeMuted' in app_ui
assert 'selectedLabelColor = InteractiveSchemeOnSurface' in app_ui
assert 'focusedTextColor = InteractiveSchemeOnSurface' in app_ui
assert 'unfocusedBorderColor = InteractiveSchemeMuted.copy(alpha = 0.62f)' in app_ui
assert read('app/build.gradle.kts') == read('patch/app/build.gradle.kts')
