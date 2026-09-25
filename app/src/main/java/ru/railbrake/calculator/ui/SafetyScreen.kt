package ru.railbrake.calculator.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.core.KnowledgeArticle
import ru.railbrake.calculator.core.KnowledgeRepository
import ru.railbrake.calculator.data.FavoriteArticleRepository

@Composable
fun SafetyScreen(onBack: () -> Unit) {
    var selectedArticleId by rememberSaveable { mutableStateOf<String?>(null) }
    val context = LocalContext.current
    val favoritesRepository = remember { FavoriteArticleRepository(context) }
    var favoriteIds by remember { mutableStateOf(favoritesRepository.load()) }
    val article = selectedArticleId?.let(KnowledgeRepository::articleById)

    BackHandler(enabled = article != null) { selectedArticleId = null }

    fun toggleFavorite(articleId: String) {
        favoriteIds = favoritesRepository.toggle(articleId)
    }

    if (article == null) {
        SafetyHome(
            favoriteIds = favoriteIds,
            onBack = onBack,
            onOpenArticle = { selectedArticleId = it.id },
            onToggleFavorite = ::toggleFavorite
        )
    } else {
        KnowledgeArticleScreen(
            article = article,
            favoriteIds = favoriteIds,
            onBack = { selectedArticleId = null },
            onOpenArticle = { selectedArticleId = it.id },
            onToggleFavorite = ::toggleFavorite,
            backLabel = "К охране труда"
        )
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun SafetyHome(
    favoriteIds: Set<String>,
    onBack: () -> Unit,
    onOpenArticle: (KnowledgeArticle) -> Unit,
    onToggleFavorite: (String) -> Unit
) {
    var query by rememberSaveable { mutableStateOf("") }
    var category by rememberSaveable { mutableStateOf("Все") }
    var onlyFavorites by rememberSaveable { mutableStateOf(false) }
    val results = remember(query, category, onlyFavorites, favoriteIds) {
        KnowledgeRepository.searchSafety(query, category)
            .filter { !onlyFavorites || it.id in favoriteIds }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp, vertical = 14.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        TextButton(onClick = onBack) { Text("← Главная", fontWeight = FontWeight.Bold) }
        RailSectionHeader(
            "Охрана труда",
            "Общие требования, риски, СИЗ и электробезопасность"
        )
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
        ) {
            Text(
                "Раздел не зависит от серии локомотива. Для конкретной работы применяются документы работодателя, установленный допуск и маркировка выданных средств защиты.",
                modifier = Modifier.padding(14.dp),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSecondaryContainer
            )
        }
        OutlinedTextField(
            value = query,
            onValueChange = { query = it },
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Поиск по охране труда") },
            singleLine = true,
            trailingIcon = {
                if (query.isNotEmpty()) {
                    IconButton(onClick = { query = "" }) {
                        Text("×", style = MaterialTheme.typography.titleLarge)
                    }
                }
            },
            shape = RoundedCornerShape(16.dp)
        )
        FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            FilterChip(
                selected = onlyFavorites,
                onClick = { onlyFavorites = !onlyFavorites },
                label = { Text("★ Избранное") }
            )
            KnowledgeRepository.safetyCategories.forEach { item ->
                FilterChip(
                    selected = category == item,
                    onClick = { category = item },
                    label = { Text(item) }
                )
            }
        }
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            items(results, key = { it.id }) { item ->
                Card(
                    onClick = { onOpenArticle(item) },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                ) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(item.category, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
                            Spacer(Modifier.width(8.dp))
                            Text("• ${item.status}", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Text(item.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Text(item.summary, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Spacer(Modifier.weight(1f))
                            TextButton(onClick = { onToggleFavorite(item.id) }) {
                                Text(if (item.id in favoriteIds) "★ В избранном" else "☆ В избранное")
                            }
                        }
                    }
                }
            }
            if (results.isEmpty()) {
                item {
                    Card(shape = RoundedCornerShape(18.dp), modifier = Modifier.fillMaxWidth()) {
                        Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Ничего не найдено", fontWeight = FontWeight.Bold)
                            Text("Измените запрос или выберите другую категорию.")
                            TextButton(onClick = { query = ""; category = "Все"; onlyFavorites = false }) {
                                Text("Сбросить фильтры")
                            }
                        }
                    }
                }
            }
        }
    }
}
