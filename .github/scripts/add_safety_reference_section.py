from pathlib import Path

FILES = [
    Path('app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt'),
]

SAFETY_FUNCTION = r'''
    private fun loadSafety(family: TechnicalFamily): List<TechnicalEntry> {
        val familyKey = if (family == TechnicalFamily.VL80S) "VL80S" else "ERMAK"
        val prefix = "SAFETY-$familyKey"

        fun item(
            suffix: String,
            title: String,
            subtitle: String,
            status: String = "INFORMATION",
            blocks: List<TechnicalBlock>
        ): TechnicalEntry {
            val search = buildList {
                add(title)
                add(subtitle)
                blocks.forEach { block ->
                    add(block.title)
                    addAll(block.lines)
                }
            }.joinToString(" ").lowercase()
            return TechnicalEntry(
                id = "$prefix-$suffix",
                family = family,
                section = TechnicalSection.SAFETY,
                title = title,
                subtitle = subtitle,
                status = status,
                blocks = blocks,
                searchText = search
            )
        }

        return listOf(
            item(
                suffix = "FACTORS",
                title = "Опасные и вредные производственные факторы",
                subtitle = "Как классифицировать факторы и не путать справочник с оценкой конкретного рабочего места",
                blocks = listOf(
                    TechnicalBlock("Основные группы", listOf(
                        "Физические факторы",
                        "Химические факторы",
                        "Биологические факторы",
                        "Психофизиологические факторы"
                    )),
                    TechnicalBlock("Для железнодорожной среды", listOf(
                        "Движущийся подвижной состав, части машин и механизмов, зоны возможного перемещения оборудования",
                        "Электрическое напряжение и электрическая дуга",
                        "Шум, вибрация, неблагоприятный микроклимат и недостаточная освещённость",
                        "Пыль, аэрозоли, масла, топлива и другие химические вещества — при их фактическом наличии",
                        "Физические нагрузки, напряжённость внимания и нервно-эмоциональная нагрузка"
                    )),
                    TechnicalBlock("Важно", listOf(
                        "Фактический перечень опасностей определяется по конкретному рабочему месту, выполняемой операции и оценке профессиональных рисков работодателя."
                    )),
                    TechnicalBlock("Нормативная основа", listOf(
                        "ГОСТ 12.0.003-2015 — классификация опасных и вредных производственных факторов",
                        "Трудовой кодекс РФ, статья 214 — выявление опасностей и оценка профессиональных рисков"
                    ))
                )
            ),
            item(
                suffix = "RISK",
                title = "Выявление опасностей и оценка риска",
                subtitle = "Что проверить до начала действия",
                blocks = listOf(
                    TechnicalBlock("Перед началом работы", listOf(
                        "Уточнить выполняемую операцию, место и границы безопасного выполнения",
                        "Проверить, какие опасности относятся именно к этой операции и рабочему месту",
                        "Сверить требования технологической документации, местных инструкций и установленного порядка допуска",
                        "Не считать отсутствие видимой опасности подтверждением безопасности"
                    )),
                    TechnicalBlock("Если условия изменились", listOf(
                        "Повторно оценить ситуацию и действовать по установленному у работодателя порядку управления профессиональными рисками."
                    )),
                    TechnicalBlock("Нормативная основа", listOf(
                        "Трудовой кодекс РФ, статья 214 — систематическое выявление опасностей, анализ и оценка профессиональных рисков"
                    ))
                )
            ),
            item(
                suffix = "PROTECTION",
                title = "Меры защиты: технические, организационные и СИЗ",
                subtitle = "Защита должна соответствовать реальной опасности",
                blocks = listOf(
                    TechnicalBlock("Технические и коллективные меры", listOf(
                        "Использовать предусмотренные ограждения, блокировки, сигнализацию и средства коллективной защиты",
                        "Не обходить защитные устройства ради ускорения работы"
                    )),
                    TechnicalBlock("Организационные меры", listOf(
                        "Соблюдать установленную технологию, порядок допуска, ограждения и взаимодействия работников",
                        "Выполнять только те действия, на которые есть обучение, допуск и полномочия"
                    )),
                    TechnicalBlock("Средства индивидуальной защиты", listOf(
                        "Применять выданные СИЗ по назначению и в исправном состоянии",
                        "СИЗ дополняют, но не отменяют технические и организационные меры безопасности"
                    )),
                    TechnicalBlock("Нормативная основа", listOf(
                        "Трудовой кодекс РФ, статьи 214 и 215 — средства коллективной и индивидуальной защиты, обучение и соблюдение требований охраны труда"
                    ))
                )
            ),
            item(
                suffix = "ELECTRICAL",
                title = "Электробезопасность и границы допуска",
                subtitle = "Справочная информация не является разрешением на работу в электроустановке",
                status = "ATTENTION",
                blocks = listOf(
                    TechnicalBlock("Главное", listOf(
                        "Работы и обслуживание электроустановок выполняются только работниками, соответствующими установленным требованиям к обучению, группе и допуску",
                        "Организационные и технические меры безопасности определяются видом работы и действующими правилами",
                        "Наличие схемы или описания в приложении не даёт права открывать оборудование, выполнять переключения или работы под напряжением"
                    )),
                    TechnicalBlock("Для электровоза", listOf(
                        "Приоритет имеют действующая технологическая документация, инструкции по эксплуатации, местный порядок и указания ответственных работников."
                    )),
                    TechnicalBlock("Нормативная основа", listOf(
                        "Приказ Минтруда России №903н — Правила по охране труда при эксплуатации электроустановок"
                    ))
                )
            ),
            item(
                suffix = "ROLLING-STOCK",
                title = "Безопасность рядом с подвижным составом и на путях",
                subtitle = "Риски движения, маневров и технического обслуживания",
                status = "ATTENTION",
                blocks = listOf(
                    TechnicalBlock("Основной принцип", listOf(
                        "Перемещение по производственной территории, осмотр и обслуживание подвижного состава выполняются по установленным безопасным маршрутам и технологическому порядку",
                        "Маневровая работа, ограждение и закрепление подвижного состава выполняются по установленным правилам с учётом местных условий"
                    )),
                    TechnicalBlock("При эксплуатации локомотива", listOf(
                        "В пути следования требования безопасности определяются технологической документацией и руководствами (инструкциями) по эксплуатации."
                    )),
                    TechnicalBlock("Нормативная основа", listOf(
                        "Приказ Минтруда России №860н — Правила по охране труда при эксплуатации подвижного состава железнодорожного транспорта"
                    ))
                )
            ),
            item(
                suffix = "STOP",
                title = "Когда работу нужно прекратить и сообщить",
                subtitle = "Неисправность, нарушение технологии или угроза жизни и здоровью",
                status = "STOP_AND_REPORT",
                blocks = listOf(
                    TechnicalBlock("Неисправность или нарушение технологии", listOf(
                        "Сообщить непосредственному руководителю о выявленной неисправности оборудования или инструмента, нарушении применяемой технологии и приостановить работу до устранения."
                    )),
                    TechnicalBlock("Угроза жизни и здоровью", listOf(
                        "Немедленно известить непосредственного или вышестоящего руководителя о известной ситуации, угрожающей жизни и здоровью людей."
                    )),
                    TechnicalBlock("Также сообщается", listOf(
                        "О нарушениях требований охраны труда, известных несчастных случаях и ухудшении состояния здоровья, включая признаки профессионального заболевания или острого отравления."
                    )),
                    TechnicalBlock("Нормативная основа", listOf(
                        "Трудовой кодекс РФ, статья 215 — обязанности работника в области охраны труда"
                    ))
                )
            ),
            item(
                suffix = "TRAINING",
                title = "Обучение, инструктаж и первая помощь",
                subtitle = "Допуск к работе начинается не с приложения, а с установленного обучения",
                blocks = listOf(
                    TechnicalBlock("Работник", listOf(
                        "Проходит установленное обучение по охране труда и безопасным методам работы",
                        "Проходит обучение по оказанию первой помощи и применению СИЗ в предусмотренных случаях",
                        "Проходит инструктаж, стажировку и проверку знаний, если это требуется для выполняемой работы"
                    )),
                    TechnicalBlock("Работодатель", listOf(
                        "Не допускает к исполнению обязанностей работников, не прошедших обязательное обучение, инструктаж, проверку знаний и предусмотренные медицинские осмотры."
                    )),
                    TechnicalBlock("Нормативная основа", listOf(
                        "Трудовой кодекс РФ, статьи 214 и 215"
                    ))
                )
            )
        )
    }
'''

for path in FILES:
    text = path.read_text(encoding='utf-8')

    text = text.replace(
        '    ACCEPTANCE("Приёмка"),\n    SYSTEMS("Системы")',
        '    ACCEPTANCE("Приёмка"),\n    SYSTEMS("Системы"),\n    SAFETY("Охрана труда")'
    )

    text = text.replace(
        '            TechnicalSection.KNOWLEDGE,\n            TechnicalSection.ELECTRICAL,',
        '            TechnicalSection.KNOWLEDGE,\n            TechnicalSection.SAFETY,\n            TechnicalSection.ELECTRICAL,',
        1
    )
    second_anchor = '            TechnicalSection.KNOWLEDGE,\n            TechnicalSection.ELECTRICAL,'
    if second_anchor in text:
        text = text.replace(
            second_anchor,
            '            TechnicalSection.KNOWLEDGE,\n            TechnicalSection.SAFETY,\n            TechnicalSection.ELECTRICAL,',
            1
        )

    text = text.replace(
        '            TechnicalSection.SYSTEMS -> loadVl80sSystems()\n',
        '            TechnicalSection.SYSTEMS -> loadVl80sSystems()\n            TechnicalSection.SAFETY -> loadSafety(TechnicalFamily.VL80S)\n'
    )
    text = text.replace(
        '            TechnicalSection.ACCEPTANCE -> emptyList()\n',
        '            TechnicalSection.ACCEPTANCE -> emptyList()\n            TechnicalSection.SAFETY -> loadSafety(TechnicalFamily.ERMAK)\n'
    )

    text = text.replace(
        '        id.startsWith("ER-SCH-") -> listOf(TechnicalFamily.ERMAK to TechnicalSection.ELECTRICAL, TechnicalFamily.ERMAK to TechnicalSection.PNEUMATIC)\n',
        '        id.startsWith("ER-SCH-") -> listOf(TechnicalFamily.ERMAK to TechnicalSection.ELECTRICAL, TechnicalFamily.ERMAK to TechnicalSection.PNEUMATIC)\n        id.startsWith("SAFETY-VL80S-") -> listOf(TechnicalFamily.VL80S to TechnicalSection.SAFETY)\n        id.startsWith("SAFETY-ERMAK-") -> listOf(TechnicalFamily.ERMAK to TechnicalSection.SAFETY)\n'
    )

    text = text.replace(
        '        return id.startsWith("VL-") || id.startsWith("VL80-") || id.startsWith("ER-") || id.startsWith("SYS-") || id.startsWith("route_") || id.matches(Regex("^[a-z][a-z0-9]+(?:-[a-z0-9]+)+$"))\n',
        '        return id.startsWith("VL-") || id.startsWith("VL80-") || id.startsWith("ER-") || id.startsWith("SYS-") || id.startsWith("SAFETY-") || id.startsWith("route_") || id.matches(Regex("^[a-z][a-z0-9]+(?:-[a-z0-9]+)+$"))\n'
    )

    marker = '    private fun schemeEntry(\n'
    if SAFETY_FUNCTION.strip() not in text:
        if marker not in text:
            raise SystemExit(f'marker missing in {path}')
        text = text.replace(marker, SAFETY_FUNCTION + '\n' + marker, 1)

    path.write_text(text, encoding='utf-8')

# sanity
for path in FILES:
    text = path.read_text(encoding='utf-8')
    required = [
        'SAFETY("Охрана труда")',
        'TechnicalSection.SAFETY -> loadSafety(TechnicalFamily.VL80S)',
        'TechnicalSection.SAFETY -> loadSafety(TechnicalFamily.ERMAK)',
        'title = "Опасные и вредные производственные факторы"',
        'title = "Когда работу нужно прекратить и сообщить"',
        'Приказ Минтруда России №903н',
        'Приказ Минтруда России №860н',
    ]
    for needle in required:
        if needle not in text:
            raise SystemExit(f'missing {needle!r} in {path}')
