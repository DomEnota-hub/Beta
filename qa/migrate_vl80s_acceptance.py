#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR = ROOT / "build/vl80s-donor"
MODEL_ROOT = ROOT / "content-packs/electric/vl80s"
SOURCE = DONOR / "vl80s_acceptance.json"
EQUIPMENT_ROOT = MODEL_ROOT / "atlas/equipment"
ACCEPTANCE_ROOT = MODEL_ROOT / "acceptance"
OLD_PACK = ACCEPTANCE_ROOT / "pantograph.vertical.pack.json"

SOURCE_COMMIT = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
SOURCE_BLOB = "5174e8fa343bb4d5b61d4f541d4dffec2708127d"

REQUIRED = [
    ("Документы и передача замечаний", "Проверить записи в журнале технического состояния, получить сведения о замечаниях и выполненных работах."),
    ("Механическая часть", "Осмотреть доступные узлы механической части в объёме ТО-1; выявленные неисправности зафиксировать установленным порядком."),
    ("Крышевое оборудование и токоприёмник", "Осмотреть с земли крышевое оборудование и проверить токоприёмник в установленном безопасном порядке."),
    ("Тяговые двигатели и вспомогательные машины", "Осмотреть доступное внешнее состояние тяговых двигателей и вспомогательных машин."),
    ("Вентиляция и форкамеры", "Проверить доступное состояние вентиляции, воздухозаборов и форкамер."),
    ("Электрическое и пневматическое управление", "Проверить аппаратуру управления и работу вспомогательных машин в предусмотренном руководством порядке."),
    ("Освещение и сигнализация", "Проверить освещение, звуковые и световые сигналы."),
    ("Песок и пескоподача", "Проверить наличие песка и работу устройств пескоподачи."),
    ("Масло тягового трансформатора", "Проверить уровень масла тягового трансформатора."),
    ("Конденсат и утечки воздуха", "Удалить конденсат из предусмотренных сборников и проверить отсутствие недопустимых утечек воздуха."),
    ("Приборы и показания", "Проверить предусмотренные контрольно-измерительные приборы и сигнализацию."),
    ("Запас воды", "Проверить предусмотренный запас воды."),
    ("Инструмент, СИЗ и схемы", "Проверить комплектность инструмента, защитных средств, противопожарного имущества и необходимых схем."),
    ("Стеклоочистители", "Проверить работу стеклоочистителей."),
    ("Тормозное оборудование", "Проверить тормозное оборудование по действующей инструкции по техническому обслуживанию тормозов."),
]
REQUIRED_SOURCE = (
    "ВЛ80С. Руководство по эксплуатации: раздел IV «Техническое обслуживание ТО-1 "
    "электровоза локомотивными бригадами» и раздел «Приёмка электровоза в депо»"
)

def unique(values):
    result = []
    seen = set()
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            value = value.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result

def source_ids(values):
    result = []
    for value in values or []:
        if isinstance(value, str):
            result.append(value)
        elif isinstance(value, dict):
            value_id = value.get("sourceId") or value.get("id")
            if value_id:
                result.append(value_id)
    return unique(result)

def block(title, lines):
    cleaned = unique(line for line in lines if isinstance(line, str))
    return {"title": title, "lines": cleaned} if cleaned else None

def pack(pack_id, entries):
    return {
        "manifest": {
            "schemaVersion": 1,
            "packId": pack_id,
            "packVersion": "0.1.0",
            "family": "ELECTRIC",
            "modelIds": ["vl80s"],
            "variantIds": [],
            "locale": "ru-RU",
            "entries": [entry["id"] for entry in entries],
            "requiresRuntime": "1.1.0",
            "sourceCatalogVersion": "test-3176d6ee-vl80s-acceptance",
            "checksums": {},
        },
        "entries": entries,
    }

def route_title(raw):
    route_id = raw.get("id", "")
    if route_id == "route_canonical":
        return "Полный осмотр"
    if route_id == "route_from_outside":
        return "Полный осмотр — начать снаружи"
    if route_id == "route_from_cab":
        return "Полный осмотр — начать из кабины"
    return raw.get("title") or route_id

def route_mode_label(value):
    return {
        "step_by_step": "пошагово",
        "checklist": "контрольный список",
        "route": "маршрут",
        "area": "по зоне",
    }.get(value, "маршрут")

source = json.loads(SOURCE.read_text(encoding="utf-8"))
items = source.get("items", [])
routes = source.get("routes", [])
if len(items) != 66:
    raise SystemExit(f"Expected 66 donor acceptance items, got {len(items)}")
if len(routes) != 7:
    raise SystemExit(f"Expected 7 donor acceptance routes, got {len(routes)}")

equipment_documents = {}
equipment_by_id = {}
for path in sorted(EQUIPMENT_ROOT.glob("*.pack.json")):
    document = json.loads(path.read_text(encoding="utf-8"))
    equipment_documents[path] = document
    for entry in document.get("entries", []):
        if entry.get("type") != "EQUIPMENT":
            continue
        entry_id = entry["id"]
        if entry_id in equipment_by_id:
            raise SystemExit(f"Duplicate equipment ID {entry_id}")
        equipment_by_id[entry_id] = entry

if len(equipment_by_id) != 89:
    raise SystemExit(f"Expected 89 migrated equipment entries, got {len(equipment_by_id)}")

# A later diagnostic-link stage enriches these canonical items. Preserve its
# verified same-model relations when the pinned donor acceptance data is rebuilt.
existing_items_path = ACCEPTANCE_ROOT / "items.pack.json"
existing_diagnostic_links = {}
if existing_items_path.exists():
    existing_document = json.loads(existing_items_path.read_text(encoding="utf-8"))
    for existing in existing_document.get("entries", []):
        existing_diagnostic_links[existing["id"]] = [
            link for link in existing.get("links", [])
            if link.get("type") == "RELATED_SCENARIO"
            and link.get("targetId", "").startswith("vl80s.diag.")
        ]

donor_entries = []
reverse_acceptance = defaultdict(set)
pending_diagnostic_hint_count = 0

for raw in items:
    entry_id = raw.get("id")
    if not isinstance(entry_id, str) or not entry_id.startswith("VL80-ACC-"):
        raise SystemExit(f"Unexpected acceptance item ID: {entry_id!r}")

    equipment_ids = unique(
        [raw.get("equipmentId")]
        + list(raw.get("relatedEquipmentIds") or [])
    )
    unknown_equipment = sorted(set(equipment_ids) - set(equipment_by_id))
    if unknown_equipment:
        raise SystemExit(
            f"{entry_id}: unknown equipment references {unknown_equipment}"
        )

    links = []
    for equipment_id in equipment_ids:
        links.append(
            {
                "type": "EQUIPMENT",
                "targetId": equipment_id,
                "role": "acceptance-equipment",
            }
        )
        reverse_acceptance[equipment_id].add(entry_id)

    links.extend(existing_diagnostic_links.get(entry_id, []))

    blocks = []
    for title, lines in (
        ("Нормальные признаки", raw.get("normalSigns") or []),
        ("Возможные неисправности", raw.get("possibleFaults") or []),
        ("Опасные признаки", raw.get("dangerFlags") or []),
        ("Граница действий", [raw.get("actionBoundary")]),
        ("Условия", raw.get("preconditions") or []),
    ):
        value = block(title, lines)
        if value:
            blocks.append(value)

    diagnostic_hints = raw.get("diagnosticHints") or []
    pending_diagnostic_hint_count += len(diagnostic_hints)

    search_terms = unique(
        [
            raw.get("title"),
            raw.get("check"),
            raw.get("phase"),
        ]
        + list(raw.get("normalSigns") or [])
        + list(raw.get("possibleFaults") or [])
    )

    donor_entries.append(
        {
            "id": entry_id,
            "type": "ACCEPTANCE_ITEM",
            "owner": {"kind": "MODEL", "modelId": "vl80s"},
            "applicability": {"modelIds": ["vl80s"]},
            "publicationStatus": "ACTIVE",
            "provenance": "UNKNOWN",
            "sourceStatus": "UNKNOWN",
            "actionDisposition": "INFORMATION_ONLY",
            "title": raw.get("title") or entry_id,
            "summary": raw.get("check"),
            "blocks": blocks,
            "searchTerms": search_terms,
            "sourceRefs": source_ids(raw.get("sourceRefs")),
            "links": links,
            "acceptanceMeta": {
                "phase": raw.get("phase"),
                "variantRule": raw.get("variantRule"),
                "pendingDiagnosticHints": diagnostic_hints,
            },
        }
    )

required_entries = []
required_ids = []
for index, (title, check) in enumerate(REQUIRED, start=1):
    entry_id = f"VL80-REQ-{index:02d}"
    required_ids.append(entry_id)
    links = []
    # This relation was already proven by the first vertical slice.
    if entry_id == "VL80-REQ-03":
        links.append(
            {
                "type": "EQUIPMENT",
                "targetId": "VL-EQ-HV-002",
                "role": "acceptance-equipment",
            }
        )
        reverse_acceptance["VL-EQ-HV-002"].add(entry_id)

    required_entries.append(
        {
            "id": entry_id,
            "type": "ACCEPTANCE_ITEM",
            "owner": {"kind": "MODEL", "modelId": "vl80s"},
            "applicability": {"modelIds": ["vl80s"]},
            "publicationStatus": "ACTIVE",
            "provenance": "MANUFACTURER",
            "sourceStatus": "UNKNOWN",
            "actionDisposition": "INFORMATION_ONLY",
            "title": title,
            "summary": check,
            "blocks": [
                {"title": "Обязательная проверка", "lines": [check]},
                {"title": "Источник", "lines": [REQUIRED_SOURCE]},
            ],
            "searchTerms": [title, check, "обязательная приёмка", "ТО-1"],
            "sourceRefs": [],
            "links": links,
            "acceptanceMeta": {
                "phase": "REQUIRED",
                "requiredBaseItem": True,
            },
        }
    )

all_item_ids = {entry["id"] for entry in donor_entries + required_entries}
donor_item_ids = {entry["id"] for entry in donor_entries}

route_records = [
    {
        "id": "VL80-ROUTE-required",
        "title": "Обязательная приёмка",
        "mode": "checklist",
        "modeLabel": "контрольный список",
        "status": "ROUTE",
        "sequence": required_ids,
        "sourceRouteId": None,
        "description": (
            "Базовый объём по руководству. Фактический обязательный объём "
            "уточняется утверждённым перечнем депо и действующими местными инструкциями."
        ),
    }
]

for raw in routes:
    source_route_id = raw.get("id")
    source_ids_for_route = raw.get("itemIds") or []
    unknown = sorted(set(source_ids_for_route) - donor_item_ids)
    if unknown:
        raise SystemExit(
            f"Route {source_route_id}: unknown donor acceptance items {unknown}"
        )
    sequence = unique(required_ids + source_ids_for_route)
    route_records.append(
        {
            "id": f"VL80-ROUTE-{source_route_id}",
            "title": route_title(raw),
            "mode": raw.get("mode") or "route",
            "modeLabel": route_mode_label(raw.get("mode")),
            "status": (
                "ROUTE"
                if source_route_id == "route_canonical"
                else "ROUTE_VARIANT"
            ),
            "sequence": sequence,
            "sourceRouteId": source_route_id,
            "description": (
                "Маршрут объединяет обязательный базовый объём и расширенные "
                "карточки осмотра без объявления всех расширенных пунктов обязательными."
            ),
        }
    )

canonical = next(
    (route for route in route_records if route["sourceRouteId"] == "route_canonical"),
    None,
)
if canonical is None:
    raise SystemExit("Canonical acceptance route is missing")
if set(canonical["sequence"]) != all_item_ids:
    missing = sorted(all_item_ids - set(canonical["sequence"]))
    extra = sorted(set(canonical["sequence"]) - all_item_ids)
    raise SystemExit(
        f"Canonical route is not complete: missing={missing}, extra={extra}"
    )

ACCEPTANCE_ROOT.mkdir(parents=True, exist_ok=True)
items_path = ACCEPTANCE_ROOT / "items.pack.json"
required_path = ACCEPTANCE_ROOT / "required.pack.json"
index_path = ACCEPTANCE_ROOT / "index.json"

items_path.write_text(
    json.dumps(
        pack("vl80s.acceptance.items", donor_entries),
        ensure_ascii=False,
        indent=2,
    ) + "\n",
    encoding="utf-8",
)
required_path.write_text(
    json.dumps(
        pack("vl80s.acceptance.required", required_entries),
        ensure_ascii=False,
        indent=2,
    ) + "\n",
    encoding="utf-8",
)
index_path.write_text(
    json.dumps(
        {
            "schemaVersion": 1,
            "modelId": "vl80s",
            "sourceSnapshot": {
                "repository": "DomEnota-maker/Test-",
                "commit": SOURCE_COMMIT,
                "asset": "app/src/main/assets/technical/vl80s_acceptance.json.gz",
                "blobSha": SOURCE_BLOB,
            },
            "itemPacks": [
                "electric/vl80s/acceptance/required.pack.json",
                "electric/vl80s/acceptance/items.pack.json",
            ],
            "routes": route_records,
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n",
    encoding="utf-8",
)

if OLD_PACK.exists():
    OLD_PACK.unlink()

# Add reverse equipment -> acceptance links without touching any other model.
for path, document in equipment_documents.items():
    changed = False
    for entry in document.get("entries", []):
        for acceptance_id in sorted(reverse_acceptance.get(entry["id"], [])):
            link = {
                "type": "ACCEPTANCE_ITEM",
                "targetId": acceptance_id,
                "role": "acceptance-check",
            }
            if link not in entry.get("links", []):
                entry.setdefault("links", []).append(link)
                changed = True
    if changed:
        path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

runtime_index_path = MODEL_ROOT / "runtime-index.json"
runtime_index = json.loads(runtime_index_path.read_text(encoding="utf-8"))
runtime_index["packs"] = [
    value
    for value in runtime_index["packs"]
    if value != "electric/vl80s/acceptance/pantograph.vertical.pack.json"
]
for value in (
    "electric/vl80s/acceptance/required.pack.json",
    "electric/vl80s/acceptance/items.pack.json",
):
    if value not in runtime_index["packs"]:
        runtime_index["packs"].append(value)
runtime_index.setdefault("featureIndexes", {})["acceptance"] = (
    "electric/vl80s/acceptance/index.json"
)
runtime_index_path.write_text(
    json.dumps(runtime_index, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

report = {
    "sourceCommit": SOURCE_COMMIT,
    "donorItemCount": len(donor_entries),
    "requiredItemCount": len(required_entries),
    "totalItemCount": len(all_item_ids),
    "donorRouteCount": len(routes),
    "runtimeRouteCount": len(route_records),
    "equipmentWithAcceptanceLinks": len(reverse_acceptance),
    "pendingDiagnosticHintCount": pending_diagnostic_hint_count,
    "replacedTemporaryPacks": [
        "content-packs/electric/vl80s/acceptance/pantograph.vertical.pack.json"
    ],
}
migration_dir = MODEL_ROOT / "migration"
migration_dir.mkdir(parents=True, exist_ok=True)
(migration_dir / "acceptance-report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print(
    "VL80S_ACCEPTANCE_MIGRATION_GENERATED",
    len(donor_entries),
    len(required_entries),
    len(route_records),
    len(reverse_acceptance),
)
