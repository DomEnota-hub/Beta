#!/usr/bin/env python3
"""Document 20 × 3 technical applicability without inventing TO-1 requiredness."""
import argparse
import json
from pathlib import Path

ACCEPTANCE = Path("content-packs/diesel/chme3-family/migration/acceptance-source-index.json")
ATLAS = Path("content-packs/diesel/chme3-family/migration/atlas-source-index.json")
PROFILES = Path("content-packs/diesel/chme3-family/migration/profile-source-index.json")
REGISTRIES = Path("content-packs/diesel/chme3-family/migration/source-registry-index.json")
OUTPUT = Path("docs/data-migration/chme3-acceptance-applicability-20x3.json")
VARIANTS = (("chme3", "ЧМЭ3"), ("chme3t", "ЧМЭ3Т"), ("chme3e", "ЧМЭ3Э"))
RATIONALES = (
    "Документы и прежние замечания относятся к конкретной единице; состав записей зависит от её истории.",
    "Комплектность, СИЗ и противопожарное имущество сверяются с фактической комплектацией и условиями работ.",
    "Рама и автосцепка отмечены для всех трёх исполнений; осмотр ограничен доступными наружными узлами.",
    "Колёсные пары, буксы, рессоры и тележки отмечены для всех трёх исполнений; состояние устанавливается на конкретной единице.",
    "Тяговый редуктор и подвеска ТЭД отмечены для всех трёх исполнений; компоновка и доступность требуют сверки.",
    "Рычажная передача и цилиндры отмечены для всех трёх исполнений; объём и способ проверки зависят от действующих тормозных правил.",
    "Компрессор, резервуары и регулятор давления отмечены для всех трёх исполнений; параметры и допустимые утечки здесь не назначаются.",
    "Влагоотделитель, резервуары и промежуточный холодильник отмечены для всех трёх исполнений; слив требует безопасного порядка.",
    "Тормозные краны, воздухораспределитель и ЭПК отмечены для всех трёх исполнений; тип и проверка зависят от установленного оборудования.",
    "Проверка действия тормозов относится к локомотиву в условиях выдачи и работы; вид опробования определяется ситуацией и действующими правилами.",
    "Бак, дизель и водомасляный теплообменник отмечены для всех трёх исполнений; нормы запасов требуют документа конкретного исполнения.",
    "Дизель и перечисленные механические узлы отмечены для всех трёх исполнений; доступный осмотр не разрешает вмешательство.",
    "Насосы, фильтры и теплообменник отмечены для всех трёх исполнений; схема и разрешённые операции уточняются по единице.",
    "Турбонагнетатель, охладитель, радиатор и вентиляторы отмечены для всех трёх исполнений; привод и компоновка могут различаться.",
    "АКБ, выключатель, вспомогательный генератор и регулятор отмечены для всех трёх исполнений; расположение АКБ и схема уточняются.",
    "Электрические машины и категория аппаратов отмечены для всех трёх исполнений; электрическая логика исполнения различается.",
    "Контроллер и сигнализация отмечены для всех трёх исполнений; органы и электронное управление сверяются по исполнению.",
    "Освещение, звуковой сигнал и стеклоочистители названы общим пунктом; конкретные приборы не привязаны к Atlas ID в источнике.",
    "Песочная система отмечена для всех трёх исполнений; фактическое устройство и доступный способ проверки уточняются.",
    "Пуск дизеля и перечисленные агрегаты отмечены для всех трёх исполнений; последовательность управления отличается по исполнению.",
)
assert len(RATIONALES) == 20


def documents(index):
    return {d["sourcePath"]: d["sourceObject"] for d in index["documents"]}


def build(root):
    acceptance = json.loads((root / ACCEPTANCE).read_text())
    atlas = json.loads((root / ATLAS).read_text())
    profiles = json.loads((root / PROFILES).read_text())
    registries = json.loads((root / REGISTRIES).read_text())
    for index in (acceptance, atlas, profiles, registries):
        assert index["runtimeImport"] is False and index["publicationStatus"] == "CANDIDATE"
        assert index["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    adocs, pdocs = documents(acceptance), documents(profiles)
    item_path = "docs/locomotives/chme3/acceptance_required_pass4.json"
    items = adocs[item_path]["items"]
    assert len(items) == 21 and [x["id"] for x in items[:20]] == [f"CHME3-REQ-{i:02d}" for i in range(1, 21)]
    assert items[20]["id"] == "CHME3T-REQ-21" and items[20]["profiles"] == ["ЧМЭ3Т"]
    epath = "docs/locomotives/diesel/chme3-family/chme3e/acceptance_stage4.json"
    e = adocs[epath]
    assert e["inheritance"]["inheritCommonRequiredItems"] == 20
    assert e["inheritance"]["excludeRequiredItemIds"] == ["CHME3T-REQ-21"]
    assert "local approved work list" in e["requirednessPolicy"]["commonRequired"]
    base = pdocs["docs/locomotives/chme3/profiles.json"]
    assert {p["series"] for p in base["profiles"]} == {v for _, v in VARIANTS}
    atlas_equipment = {}
    for d in atlas["documents"]:
        for field in ("equipment", "records"):
            for i, record in enumerate(d["sourceObject"].get(field, [])):
                atlas_equipment.setdefault(record["id"], []).append({
                    "sourcePath": d["sourcePath"], "sourcePointer": f"/{field}/{i}",
                    "name": record.get("name"), "applicability": record.get("applicability"),
                    "role": "CARD" if "atlas_cards_" in d["sourcePath"] else "INDEX"})
    registry = {}
    for d in registries["documents"]:
        for i, record in enumerate(d["sourceObject"]["sources"]):
            registry.setdefault(record["id"], []).append({"sourcePath": d["sourcePath"],
                                                              "sourcePointer": f"/sources/{i}"})
    matrix = []
    for i, item in enumerate(items[:20]):
        equipment = []
        for eid in item.get("equipmentIds", []):
            occurrences = atlas_equipment[eid]
            assert len(occurrences) == 2 and {o["role"] for o in occurrences} == {"INDEX", "CARD"}, eid
            assert all(o["applicability"] == [v for _, v in VARIANTS] for o in occurrences), eid
            equipment.append({"id": eid, "sourceOccurrences": occurrences})
        refs = item["sourceRefs"]
        assert all(ref in registry and len(registry[ref]) == 1 for ref in refs)
        cells = {}
        for variant, label in VARIANTS:
            if variant == "chme3":
                variant_reason = "Базовый ЧМЭ3; наличие, состояние и допустимый объём сверяются по фактической машине."
                profile_evidence = "docs/locomotives/chme3/profiles.json#/profiles/0"
            elif variant == "chme3t":
                variant_reason = ("ЧМЭ3Т: общий узел проверяется по фактической компоновке; "
                                  "оборудование реостатного тормоза относится к отдельному пункту CHME3T-REQ-21.")
                profile_evidence = "docs/locomotives/chme3/profiles.json#/profiles/1"
            else:
                variant_reason = ("ЧМЭ3Э: наследование общего пункта допускается только для установленного "
                                  "оборудования; электронные отличия и отсутствие реостатного тормоза учитываются отдельно.")
                profile_evidence = epath + "#/inheritance"
            if i in (15, 16, 19) and variant != "chme3":
                status = "VARIANT_METHOD_REQUIRES_PRIMARY_CHECK"
            elif not equipment:
                status = "TOPIC_SUPPORTED_ACTUAL_SCOPE_UNVERIFIED"
            else:
                status = "ATLAS_SUPPORTED_ACTUAL_EQUIPMENT_UNVERIFIED"
            cells[variant] = {"series": label, "technicalApplicability": status,
                              "reason": RATIONALES[i] + " " + variant_reason,
                              "profileEvidence": profile_evidence,
                              "sourceRefs": refs, "equipmentIds": item.get("equipmentIds", []),
                              "requiredness": "UNDETERMINED_APPROVED_LOCAL_TO1_LIST_MISSING",
                              "safetyBoundary": item.get("actionBoundary", "Наблюдение и запись состояния; способ действий — только по действующей документации и безопасному технологическому процессу."),
                              "actualUnitVerificationRequired": True}
        matrix.append({"itemId": item["id"], "title": item["title"],
                       "sourcePath": item_path, "sourcePointer": f"/items/{i}",
                       "legacySourcePhase": item["phase"], "sourceCheck": item["check"],
                       "sourceRefs": refs,
                       "sourceRegistryEvidence": [dict(sourceId=ref, **registry[ref][0]) for ref in refs],
                       "equipmentEvidence": equipment, "cells": cells})
    assert len(matrix) == 20 and sum(len(row["cells"]) for row in matrix) == 60
    return {"schemaVersion": 1, "donorCommit": acceptance["donorCommit"],
            "scope": "SOURCE_REVIEW_ONLY_NO_RUNTIME_IMPORT", "runtimeImport": False,
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
            "technicalDecisionPolicy": "ATLAS_AND_PROFILE_SOURCE_SUPPORT_ONLY_ACTUAL_UNIT_CHECK_REQUIRED",
            "requirednessPolicy": "NO_NETWORK_OR_LOCAL_TO1_MANDATORY_ASSIGNMENT_WITHOUT_APPROVED_WORK_LIST",
            "missingPrimaryDocuments": [
                "Актуальный утверждённый перечень работ ТО-1 локомотивной бригады соответствующих дороги и депо: обязательность каждого пункта, ситуация выдачи/приёмки, объём и ответственный.",
                "Действующая редакция ЧМЭ3 ИО с извещениями и документы конкретного исполнения/модернизации: оборудование и безопасный способ проверки для данной единицы.",
                "Действующие правила обслуживания тормозов и местный технологический процесс: вид опробования и безопасный порядок пневматических операций в фактической ситуации."],
            "rows": matrix}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--output", type=Path, default=OUTPUT)
    p.add_argument("--verify-output", action="store_true")
    a = p.parse_args()
    rendered = json.dumps(build(a.root), ensure_ascii=False, indent=2) + "\n"
    if a.verify_output:
        assert a.output.read_text() == rendered
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(rendered)
    print("CHME3_ACCEPTANCE_APPLICABILITY_PASS", 20, 60)
