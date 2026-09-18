from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f'Expected block not found: {label}')
    return text.replace(old, new, 1)

# Persist the "show exam-derived materials in knowledge base" preference.
for path in [
    Path('app/src/main/java/ru/railbrake/calculator/data/SecretAccessRepository.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/data/SecretAccessRepository.kt'),
]:
    text = path.read_text()
    text = replace_once(
        text,
        '''    fun unlock() {
        preferences.edit().putBoolean(KEY_UNLOCKED, true).apply()
    }

    fun hide()''',
        '''    fun unlock() {
        preferences.edit().putBoolean(KEY_UNLOCKED, true).apply()
    }

    fun showExamMaterialsInKnowledge(): Boolean =
        preferences.getBoolean(KEY_SHOW_IN_KNOWLEDGE, false)

    fun setShowExamMaterialsInKnowledge(show: Boolean) {
        preferences.edit().putBoolean(KEY_SHOW_IN_KNOWLEDGE, show).apply()
    }

    fun hide()''',
        f'{path}: visibility accessors',
    )
    text = replace_once(
        text,
        '''    companion object {
        private const val KEY_UNLOCKED = "exam_questions_unlocked"
    }
''',
        '''    companion object {
        private const val KEY_UNLOCKED = "exam_questions_unlocked"
        private const val KEY_SHOW_IN_KNOWLEDGE = "exam_materials_in_knowledge"
    }
''',
        f'{path}: visibility key',
    )
    path.write_text(text)

# Hidden 329-question section: add the explicit switch.
for path in [
    Path('app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt'),
]:
    text = path.read_text()
    text = replace_once(
        text,
        'import androidx.compose.material3.TextButton\n',
        'import androidx.compose.material3.TextButton\nimport androidx.compose.material3.Switch\n',
        f'{path}: Switch import',
    )
    text = replace_once(
        text,
        'import ru.railbrake.calculator.core.Vl80sObservationCatalog\n',
        'import ru.railbrake.calculator.core.Vl80sObservationCatalog\nimport ru.railbrake.calculator.data.SecretAccessRepository\n',
        f'{path}: SecretAccessRepository import',
    )
    text = replace_once(
        text,
        '''    val context = LocalContext.current
    val repository = remember { ExamQuestionRepository(context) }
    var query''',
        '''    val context = LocalContext.current
    val repository = remember { ExamQuestionRepository(context) }
    val secretAccessRepository = remember { SecretAccessRepository(context) }
    var showInKnowledge by remember { mutableStateOf(secretAccessRepository.showExamMaterialsInKnowledge()) }
    var query''',
        f'{path}: preference state',
    )
    text = replace_once(
        text,
        '''        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Column(Modifier.weight(1f)) {
                RailSectionHeader("База вопросов", "329 проверочных вопросов • быстрый поиск по формулировке и ответу")
            }
            TextButton(onClick = onHide) { Text("Скрыть") }
        }
        OutlinedTextField(
''',
        '''        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Column(Modifier.weight(1f)) {
                RailSectionHeader("База вопросов", "329 проверочных вопросов • быстрый поиск по формулировке и ответу")
            }
            TextButton(onClick = onHide) { Text("Скрыть") }
        }
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
            shape = RoundedCornerShape(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(14.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Показывать материалы в справочнике", fontWeight = FontWeight.Bold)
                    Text(
                        if (showInKnowledge) "Материалы из базы 329 вопросов видны в обычном справочнике."
                        else "Материалы из базы 329 вопросов скрыты из обычного справочника.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = showInKnowledge,
                    onCheckedChange = { enabled ->
                        showInKnowledge = enabled
                        secretAccessRepository.setShowExamMaterialsInKnowledge(enabled)
                    }
                )
            }
        }
        OutlinedTextField(
''',
        f'{path}: visibility switch',
    )
    path.write_text(text)

# Knowledge base: hide the 329-derived material by default and add a clear-search cross.
for path in [
    Path('app/src/main/java/ru/railbrake/calculator/ui/KnowledgeBaseScreen.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/ui/KnowledgeBaseScreen.kt'),
]:
    text = path.read_text()
    text = replace_once(
        text,
        'import androidx.compose.material3.FilterChip\n',
        'import androidx.compose.material3.FilterChip\nimport androidx.compose.material3.IconButton\n',
        f'{path}: IconButton import',
    )
    text = replace_once(
        text,
        'import ru.railbrake.calculator.data.FavoriteArticleRepository\n',
        'import ru.railbrake.calculator.data.FavoriteArticleRepository\nimport ru.railbrake.calculator.data.SecretAccessRepository\n',
        f'{path}: SecretAccessRepository import',
    )
    text = replace_once(
        text,
        '''    val favoritesRepository = remember { FavoriteArticleRepository(context) }
    val examQuestionRepository = remember { ExamQuestionRepository(context) }
    var favoriteIds''',
        '''    val favoritesRepository = remember { FavoriteArticleRepository(context) }
    val secretAccessRepository = remember { SecretAccessRepository(context) }
    val showExamMaterialsInKnowledge = remember { secretAccessRepository.showExamMaterialsInKnowledge() }
    val examQuestionRepository = remember(showExamMaterialsInKnowledge) {
        if (showExamMaterialsInKnowledge) ExamQuestionRepository(context) else null
    }
    var favoriteIds''',
        f'{path}: conditional exam repository',
    )
    text = replace_once(
        text,
        '''            favoriteIds = favoriteIds,
            examQuestionRepository = examQuestionRepository,
            onOpenArticle''',
        '''            favoriteIds = favoriteIds,
            examQuestionRepository = examQuestionRepository,
            showExamMaterialsInKnowledge = showExamMaterialsInKnowledge,
            onOpenArticle''',
        f'{path}: KnowledgeHome argument',
    )
    text = replace_once(
        text,
        '''    favoriteIds: Set<String>,
    examQuestionRepository: ExamQuestionRepository,
    onOpenArticle''',
        '''    favoriteIds: Set<String>,
    examQuestionRepository: ExamQuestionRepository?,
    showExamMaterialsInKnowledge: Boolean,
    onOpenArticle''',
        f'{path}: KnowledgeHome signature',
    )
    text = replace_once(
        text,
        '''    val categories = remember {
        (KnowledgeRepository.categories + examQuestionRepository.categories).distinct()
    }
    val thematicFacts = remember(query, category, onlyFavorites) {
        if (onlyFavorites) emptyList() else examQuestionRepository.thematicFacts(
            query = query,
            category = category.takeUnless { it == "Все" }
        )
    }
''',
        '''    val categories = remember(showExamMaterialsInKnowledge, examQuestionRepository) {
        if (showExamMaterialsInKnowledge && examQuestionRepository != null) {
            (KnowledgeRepository.categories + examQuestionRepository.categories).distinct()
        } else {
            KnowledgeRepository.categories
        }
    }
    val thematicFacts = remember(query, category, onlyFavorites, showExamMaterialsInKnowledge, examQuestionRepository) {
        if (!showExamMaterialsInKnowledge || onlyFavorites || examQuestionRepository == null) {
            emptyList()
        } else {
            examQuestionRepository.thematicFacts(
                query = query,
                category = category.takeUnless { it == "Все" }
            )
        }
    }
''',
        f'{path}: hidden-by-default facts',
    )
    text = replace_once(
        text,
        '''            label = { Text("Поиск по справочнику") },
            singleLine = true,
            shape = RoundedCornerShape(16.dp)
''',
        '''            label = { Text("Поиск по справочнику") },
            singleLine = true,
            trailingIcon = {
                if (query.isNotEmpty()) {
                    IconButton(onClick = { query = "" }) {
                        Text("×", style = MaterialTheme.typography.titleLarge)
                    }
                }
            },
            shape = RoundedCornerShape(16.dp)
''',
        f'{path}: knowledge clear search',
    )
    path.write_text(text)

# Beta13 identity.
for path in [Path('app/build.gradle.kts'), Path('patch/app/build.gradle.kts')]:
    text = path.read_text()
    text = replace_once(text, 'versionCode = 157', 'versionCode = 158', f'{path}: versionCode')
    text = replace_once(text, 'versionName = "1.2.2-dev14-beta12"', 'versionName = "1.2.2-dev14-beta13"', f'{path}: versionName')
    path.write_text(text)

# Sanity checks.
assert 'KEY_SHOW_IN_KNOWLEDGE' in Path('app/src/main/java/ru/railbrake/calculator/data/SecretAccessRepository.kt').read_text()
assert 'Показывать материалы в справочнике' in Path('app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt').read_text()
knowledge = Path('app/src/main/java/ru/railbrake/calculator/ui/KnowledgeBaseScreen.kt').read_text()
assert 'if (showExamMaterialsInKnowledge) ExamQuestionRepository(context) else null' in knowledge
assert 'IconButton(onClick = { query = "" })' in knowledge
