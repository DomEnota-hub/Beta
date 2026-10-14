from pathlib import Path

FILES = [
    Path('app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt'),
]

OLD_VL = 'TechnicalSection.KNOWLEDGE -> loadVl80sKnowledge() + loadWheelFlatReference(TechnicalFamily.VL80S)'
NEW_VL = 'TechnicalSection.KNOWLEDGE -> loadVl80sKnowledge() + loadWheelFlatReference(TechnicalFamily.VL80S) + loadBrakeJamReference(TechnicalFamily.VL80S)'
OLD_ER = 'TechnicalSection.KNOWLEDGE -> loadErmakKnowledge() + loadWheelFlatReference(TechnicalFamily.ERMAK)'
NEW_ER = 'TechnicalSection.KNOWLEDGE -> loadErmakKnowledge() + loadWheelFlatReference(TechnicalFamily.ERMAK) + loadBrakeJamReference(TechnicalFamily.ERMAK)'

ANCHOR = '''\n\n    private fun loadWheelFlatReference(family: TechnicalFamily): List<TechnicalEntry> {'''

FUNCTION = r'''

    private fun loadBrakeJamReference(family: TechnicalFamily): List<TechnicalEntry> {
        val id = if (family == TechnicalFamily.VL80S) "vl80-brake-jam" else "ER-KB-BRAKE-JAM"
        return listOf(
            TechnicalEntry(
                id = id,
                family = family,
                section = TechnicalSection.KNOWLEDGE,
                title = "Заклинивание тормоза вагона: порядок действий",
                subtitle = "Ручной отпуск, выключение неисправного тормоза и контроль фактического отпуска",
                status = "ATTENTION",
                blocks = listOf(
                    TechnicalBlock("Если отдельный вагон не отпустил", listOf(
                        "По указанию машиниста проверить фактический отпуск: выход штока тормозного цилиндра и отход тормозных колодок (накладок) от колес (дисков).",
                        "Если тормоз отдельного вагона не отпустил, выполнить ручной отпуск — выпустить воздух из запасного резервуара через выпускной клапан.",
                        "После восстановления зарядного давления выполнить установленную проверку торможения и отпуска и повторно убедиться в отпуске тормоза."
                    )),
                    TechnicalBlock("Если неисправность сохраняется и тормоз выключается", listOf(
                        "Перекрыть разобщительный кран на отводе тормозной магистрали к воздухораспределителю — неисправный тормоз вагона отключается от управления по тормозной магистрали.",
                        "Полностью выпустить воздух из запасного резервуара и камер воздухораспределителя через выпускной клапан.",
                        "Убедиться, что шток тормозного цилиндра вернулся и тормозные колодки (накладки) отошли от колес (дисков).",
                        "Если после полного выпуска воздуха колодки (накладки) не отошли, не считать тормоз отпущенным: требуется осмотр механической части тормоза и дальнейшее решение по установленному порядку."
                    )),
                    TechnicalBlock("После выключения тормоза", listOf(
                        "Доложить машинисту номер или место вагона, выполненные действия и результат проверки отпуска.",
                        "Учесть выключенный тормоз при определении фактического тормозного нажатия поезда и внести необходимые изменения в справку ВУ-45 в установленном порядке.",
                        "После возобновления движения проверить действие тормозов поезда в установленном порядке."
                    )),
                    TechnicalBlock("Безопасность при вмешательстве в тормозное оборудование", listOf(
                        "Если требуется техническое обслуживание или ремонт тормозного оборудования грузового вагона в составе поезда, работы выполняются только после перекрытия разобщительного крана и выпуска сжатого воздуха из запасного (рабочего) резервуара и тормозного цилиндра.",
                        "Не разбирать соединения и не ослаблять элементы пневматической системы, находящиеся под давлением."
                    )),
                    TechnicalBlock("Нормативная основа", listOf(
                        "Распоряжение ОАО «РЖД» от 12.12.2017 № 2580р (ред. от 18.02.2025): при отсутствии отпуска у отдельных вагонов предусмотрен выпуск воздуха из запасных резервуаров через выпускной клапан с последующей проверкой отпуска.",
                        "Правила технического обслуживания тормозного оборудования и управления тормозами железнодорожного подвижного состава, протокол Совета по железнодорожному транспорту от 6–7 мая 2014 г. № 60.",
                        "ПОТ РЖД-4100612-ЦДИ-128-2018, п. 2.2.4: требования безопасности при обслуживании и ремонте тормозного оборудования грузового вагона в составе поезда."
                    ))
                ),
                searchText = "заклинивание тормоза не отпустил вагон ручной отпуск воздухораспределитель выпускной клапан запасный резервуар разобщительный кран колодки тормозной цилиндр ву-45 тормозное нажатие".lowercase()
            )
        )
    }
'''

for path in FILES:
    text = path.read_text(encoding='utf-8')
    if NEW_VL not in text:
        if OLD_VL not in text:
            raise SystemExit(f'VL knowledge anchor not found in {path}')
        text = text.replace(OLD_VL, NEW_VL, 1)
    if NEW_ER not in text:
        if OLD_ER not in text:
            raise SystemExit(f'Ermak knowledge anchor not found in {path}')
        text = text.replace(OLD_ER, NEW_ER, 1)
    if 'private fun loadBrakeJamReference' not in text:
        if ANCHOR not in text:
            raise SystemExit(f'function anchor not found in {path}')
        text = text.replace(ANCHOR, FUNCTION + ANCHOR, 1)
    path.write_text(text, encoding='utf-8')

print('Brake-jam reference patch applied')
