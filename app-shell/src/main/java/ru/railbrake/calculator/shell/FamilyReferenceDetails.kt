package ru.railbrake.calculator.shell

/** Non-procedural, independently worded descriptions of pinned donor objects.
 * Source IDs are donor evidence, not current-source approval. */
internal data class FamilyReferenceDetail(val description: String, val sourceIds: List<String>)

internal object FamilyReferenceDetails {
    fun forEntry(entry: FamilyReferencePreview): FamilyReferenceDetail? {
        if (entry.modelId !in setOf("2es5k", "3es5k") ||
            entry.scope != ReferenceScope.EXECUTION_UNVERIFIED ||
            entry.executionId != null ||
            entry.donorPath != "app/src/main/assets/technical/ermak_knowledge.json.gz" ||
            entry.donorBlobSha != "08d164fc11c33c241d04ad6ad60c13a3aec996c8") return null
        return when (entry.donorId) {
            "ER-KB-SYS-20" -> FamilyReferenceDetail(
                "Тяговый трансформатор питает преобразователи. Через аппараты силовой цепи и реакторы энергия поступает к тяговым двигателям. Групповое и поосное регулирование отличаются организацией управления двигателями; конкретная схема зависит от исполнения.",
                listOf("ER-SRC-001", "ER-SRC-002", "ER-SRC-004", "ER-SRC-018", "ER-SRC-019", "ER-SRC-026", "ER-SRC-029"),
            )
            "ER-KB-SYS-21" -> FamilyReferenceDetail(
                "При рекуперации тяговые двигатели работают как генераторы, а преобразователи обеспечивают передачу энергии обратно в сеть. Цепь возбуждения участвует в формировании тормозного момента. Электрическое торможение связано с пневматическим; конкретная логика замещения зависит от исполнения.",
                listOf("ER-SRC-001", "ER-SRC-002", "ER-SRC-007", "ER-SRC-018", "ER-SRC-019"),
            )
            "ER-KB-SYS-30" -> FamilyReferenceDetail(
                "Вспомогательные потребители получают питание от обмотки собственных нужд трансформатора. В зависимости от схемы питание машин организовано непосредственно или через преобразователь частоты. Состав потребителей зависит от типа секции и исполнения.",
                listOf("ER-SRC-001", "ER-SRC-002", "ER-SRC-003", "ER-SRC-004"),
            )
            else -> null
        }
    }
}
