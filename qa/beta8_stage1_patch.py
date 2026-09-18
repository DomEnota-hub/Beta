from pathlib import Path
import re

ROOTS = [Path("app"), Path("patch/app")]


def patch_screen(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    text, count = re.subn(
        r'\n    var trainingScenarioId by rememberSaveable \{ mutableStateOf\("gv-no-close"\) \}.*?\n    val results =',
        '\n    val results =',
        text,
        count=1,
        flags=re.S,
    )
    assert count == 1, f"training state block not found in {path}"

    trainer_chip = '                item { FilterChip(catalogMode == "training", { catalogMode = "training" }, label = { Text("Тренажёр") }) }\n'
    assert trainer_chip in text, f"trainer chip not found in {path}"
    text = text.replace(trainer_chip, "", 1)

    aux_line = '    QuickRouteItem("Вспомогательные машины", "Не запускаются фазорасщепитель, вентиляторы или компрессор.", "aux-machines"),\n'
    oil_line = '    QuickRouteItem("Масляный насос трансформатора", "Не запускается, отключается или не подтверждается работа маслонасоса трансформатора.", "oil-pump-failure"),\n'
    assert aux_line in text, f"quick route anchor not found in {path}"
    if oil_line not in text:
        text = text.replace(aux_line, aux_line + oil_line, 1)

    old_search = '''        if (catalogMode == "scenarios" || catalogMode == "observations") item {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = { Text(if (catalogMode == "scenarios") "Симптом или аппарат" else "Лампа, прибор, звук или аппарат") },
                placeholder = { Text(if (catalogMode == "scenarios") "Например: ЭКГ, №395, БУРТ, АЛСН" else "Например: выбило ГВ, ТМ падает, стук, боксование") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
        }
'''
    new_search = '''        if (catalogMode == "scenarios" || catalogMode == "observations" || catalogMode == "quick") item {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = {
                    Text(
                        when (catalogMode) {
                            "scenarios" -> "Симптом или аппарат"
                            "observations" -> "Лампа, прибор, звук или аппарат"
                            else -> "Поиск во вкладке «В пути»"
                        }
                    )
                },
                placeholder = {
                    Text(
                        when (catalogMode) {
                            "scenarios" -> "Например: ЭКГ, №395, БУРТ, АЛСН"
                            "observations" -> "Например: выбило ГВ, ТМ падает, стук, боксование"
                            else -> "Например: маслонасос, тормоза, дым"
                        }
                    )
                },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
        }
'''
    assert old_search in text, f"search block not found in {path}"
    text = text.replace(old_search, new_search, 1)

    text, count = re.subn(
        r'\n        \} else if \(catalogMode == "training"\) \{.*?\n        \} else if \(catalogMode == "quick"\) \{',
        '\n        } else if (catalogMode == "quick") {',
        text,
        count=1,
        flags=re.S,
    )
    assert count == 1, f"trainer UI branch not found in {path}"

    observation_tail = '''        } to equipment
    }

    LazyColumn(
'''
    quick_filter = '''        } to equipment
    }
    val quickResults = quickRouteItems.filter { item ->
        val scenario = DiagnosticRepository.scenario(item.scenarioId)
        val matchesVariant = scenario?.let { candidate ->
            LocomotiveProfiles.appliesToVariant(selectedVariantId, candidate.applicableVariantIds)
        } == true
        val matchesQuery = query.isBlank() || listOf(
            item.title,
            item.subtitle,
            scenario?.title.orEmpty(),
            scenario?.summary.orEmpty()
        ).any { value -> value.contains(query, ignoreCase = true) }
        matchesVariant && matchesQuery
    }

    LazyColumn(
'''
    assert observation_tail in text, f"observation block anchor not found in {path}"
    text = text.replace(observation_tail, quick_filter, 1)

    old_quick_items = '''            items(
                quickRouteItems.filter { item ->
                    DiagnosticRepository.scenario(item.scenarioId)?.let { scenario ->
                        LocomotiveProfiles.appliesToVariant(selectedVariantId, scenario.applicableVariantIds)
                    } == true
                },
                key = { it.scenarioId }
            ) { item ->
'''
    new_quick_items = '''            if (quickResults.isEmpty()) {
                item {
                    InfoCard(
                        "Ничего не найдено",
                        listOf("Измените запрос или очистите строку поиска."),
                        MaterialTheme.colorScheme.surfaceVariant
                    )
                }
            }
            items(quickResults, key = { it.scenarioId }) { item ->
'''
    assert old_quick_items in text, f"quick list block not found in {path}"
    text = text.replace(old_quick_items, new_quick_items, 1)

    path.write_text(text, encoding="utf-8")


def patch_catalog(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if 'id = "oil-pump-failure"' in text:
        return

    anchor = '''            causes = listOf("Засорена или пережата импульсная линия.", "Есть утечка в линии прибора.", "Заедает механизм манометра.", "Прибор имеет недопустимую погрешность.", "Реальное изменение давления ошибочно принята за отказ прибора."),
            related = listOf("pressure-gauge-mismatch", "equalizing-reservoir-mismatch", "brake-cylinder-imbalance", "compressor-long-run")
        )
    )
'''
    # Correct source wording is "принято"; keep a fallback to avoid a fragile patch.
    if anchor not in text:
        anchor = anchor.replace("принята", "принято")

    replacement = anchor.replace(
        '''        )
    )
''',
        '''        ),
        scenario(
            id = "oil-pump-failure",
            category = "Вспомогательные машины",
            title = "Отказ масляного насоса трансформатора",
            summary = "Маслонасос трансформатора не запускается, отключается после пуска либо работа системы циркуляции масла не подтверждается.",
            equipment = listOf("маслонасос трансформатора", "тяговый трансформатор", "контактор маслонасоса", "цепи собственных нужд", "контроль циркуляции масла"),
            questions = listOf(
                q("oil-start", "Маслонасос совсем не запускается при штатной команде?", "Проверять наличие команды, питание отходящей цепи, контактор и действие защиты.", "Уточнить, отключается ли насос после пуска или проблема только в подтверждении циркуляции.", "oil-run"),
                q("oil-run", "После запуска насос отключается, гудит, вибрирует или работает с необычным шумом?", "Вероятны перегрузка, механическое сопротивление, дефект двигателя или повторное действие защиты.", "Проверять достоверность признака циркуляции масла и связанную индикацию.", "oil-danger"),
                q("oil-danger", "Есть отсутствие подтверждённой циркуляции масла, рост температуры, запах, дым или действие защиты трансформатора?", "Снять связанную нагрузку, не продолжать эксплуатацию без подтверждённого охлаждения и доложить установленным порядком.", "Зафиксировать расхождение команды, индикации и фактической работы для проверки по схеме конкретной секции.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Нет команды или питания цепи маслонасоса.", "Не включается либо отпадает контактор маслонасоса.", "Срабатывает защита электродвигателя.", "Есть механическое сопротивление или неисправность насоса/двигателя.", "Неисправен контроль циркуляции масла или связанная индикация."),
            related = listOf("aux-machines", "aux-common-loss", "aux-machine-single-trip", "smoke-fire-flashover")
        )
    )
''',
        1,
    )
    assert anchor in text, f"catalog insertion anchor not found in {path}"
    path.write_text(text.replace(anchor, replacement, 1), encoding="utf-8")


for root in ROOTS:
    patch_screen(root / "src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt")
    patch_catalog(root / "src/main/java/ru/railbrake/calculator/core/DiagnosticCompletionCatalog.kt")

for rel in (
    "src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt",
    "src/main/java/ru/railbrake/calculator/core/DiagnosticCompletionCatalog.kt",
):
    assert (Path("app") / rel).read_bytes() == (Path("patch/app") / rel).read_bytes(), f"mirror mismatch: {rel}"

print("Beta8 diagnostics stage patched and mirrors verified")
