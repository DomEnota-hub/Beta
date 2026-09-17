#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import gzip
import json
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
assets = root / "app/src/main/assets/technical"
sources = root / "app/src/main/java"

if not assets.exists() or not sources.exists():
    raise SystemExit("usage: canonical_field_audit.py <patched Android project root>")

kt_files = list(sources.rglob("*.kt"))
kt_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in kt_files)

# Recognize direct JSON access and deliberate named-bucket iteration. This is not a
# proof that a field is rendered; it is a guard against fields never being addressed.
def key_is_read(key: str) -> bool:
    escaped = re.escape(key)
    patterns = [
        rf'opt(?:String|Int|Long|Double|Boolean|JSONArray|JSONObject)\(\s*"{escaped}"',
        rf'\.array\(\s*"{escaped}"',
        rf'\.obj\(\s*"{escaped}"',
        rf'get(?:String|Int|Long|Double|Boolean|JSONArray|JSONObject)\(\s*"{escaped}"',
        rf'"{escaped}"',  # named bucket lists / maps intentionally addressed dynamically
    ]
    return any(re.search(p, kt_text) for p in patterns)


def load_asset(path: Path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_name(path: Path) -> str:
    return path.name[:-3] if path.name.endswith(".gz") else path.name


def leaves(value, path=()):
    if isinstance(value, dict):
        if not value:
            yield path, value
        for key, child in value.items():
            yield from leaves(child, path + (key,))
    elif isinstance(value, list):
        if not value:
            yield path + ("[]",), value
        for child in value:
            yield from leaves(child, path + ("[]",))
    else:
        yield path, value


def keys_recursive(value) -> set[str]:
    result = set()
    if isinstance(value, dict):
        for k, v in value.items():
            result.add(k)
            result.update(keys_recursive(v))
    elif isinstance(value, list):
        for v in value:
            result.update(keys_recursive(v))
    return result


metadata_keys = {
    "schemaVersion", "catalogVersion", "project", "stage", "status", "generatedAt",
    "generatedFrom", "sourcePackage", "release", "statistics", "pendingMerge"
}

# Prefer uncompressed JSON if both forms exist; otherwise transparently inspect .json.gz.
asset_by_name = {}
for path in sorted(list(assets.glob("*.json")) + list(assets.glob("*.json.gz"))):
    name = canonical_name(path)
    current = asset_by_name.get(name)
    if current is None or (current.suffix == ".gz" and path.suffix != ".gz"):
        asset_by_name[name] = path

report_lines = []
critical_failures = []
summary = []
asset_keys = {}

for name, asset in sorted(asset_by_name.items()):
    data = load_asset(asset)
    asset_keys[name] = keys_recursive(data)
    paths = Counter()
    examples = defaultdict(list)
    for path, value in leaves(data):
        if not path:
            continue
        normalized = "/".join(path)
        paths[normalized] += 1
        if len(examples[normalized]) < 2 and value not in (None, "", [], {}):
            examples[normalized].append(str(value)[:120].replace("\n", " "))

    uncovered = []
    for path, count in paths.items():
        named = [x for x in path.split("/") if x != "[]"]
        if not named:
            continue
        key = named[-1]
        if key in metadata_keys:
            continue
        if not key_is_read(key):
            uncovered.append((count, path, examples[path]))

    uncovered.sort(reverse=True)
    total = sum(paths.values())
    uncovered_occ = sum(c for c, _, _ in uncovered)
    summary.append((name, len(paths), len(uncovered), total, uncovered_occ))
    report_lines.append(f"\n## {name}\nunique leaf paths={len(paths)}; unread leaf paths={len(uncovered)}; leaf occurrences={total}; unread occurrences={uncovered_occ}")
    for count, path, ex in uncovered[:80]:
        report_lines.append(f"UNREAD x{count:4d}  {path}  examples={ex}")

critical_keys = {
    "vl80s_acceptance.json": [
        "routes", "mode", "itemIds", "notes", "preconditions", "states", "rules", "gates"
    ],
    "vl80s_diagnostics.json": [
        "edges", "from", "to", "relatedEquipmentIds"
    ],
    "vl80s_electrical.json": [
        "baseSchemes", "modeOverlays", "variantOverlays", "semanticEdges", "paths"
    ],
    "vl80s_pneumatic.json": [
        "views", "states", "referenceBenchmarks", "paths", "sequence"
    ],
    "ermak_diagnostics.json": [
        "graph", "startNodeId", "nodes", "type", "choices", "nextNodeId", "nextScenarioId",
        "userFacingPolicy", "riskClass", "sourceBound", "terminalStatus"
    ],
    "ermak_links.json": [
        "byEquipment", "bySystem", "byDiagnostic", "byScheme"
    ],
    "ermak_schemes.json": [
        "variantSelector", "dimensions", "requiredWhen", "hardRules", "schemes", "variantRules",
        "hotspotLayer", "semanticGraph", "flowLayer", "path"
    ],
    "ermak_system_map.json": [
        "systems", "criticalLinks", "profiles"
    ],
}

for file_name, keys in critical_keys.items():
    present = asset_keys.get(file_name, set())
    missing = [k for k in keys if k in present and not key_is_read(k)]
    if missing:
        critical_failures.append(f"{file_name}: present but never addressed: {', '.join(missing)}")

print("CANONICAL FIELD COVERAGE SUMMARY")
for name, path_count, unread_paths, total, unread_occ in summary:
    print(f"{name:34s} paths={path_count:4d} unread={unread_paths:4d} occurrences={total:6d} unread_occ={unread_occ:6d}")

print("\nCRITICAL CONTRACT CHECK")
if critical_failures:
    for item in critical_failures:
        print("FAIL", item)
else:
    print("PASS all explicitly critical canonical fields present in assets are addressed by Kotlin loaders/runtime")

report_path = root / "canonical-field-audit.txt"
report_path.write_text(
    "CANONICAL FIELD COVERAGE AUDIT\n" +
    "\n".join(f"{n}: unique_paths={p}, unread_paths={u}, leaf_occurrences={t}, unread_occurrences={o}" for n,p,u,t,o in summary) +
    "\n\nCRITICAL CONTRACT CHECK\n" + ("\n".join(critical_failures) if critical_failures else "PASS") +
    "\n" + "\n".join(report_lines) + "\n",
    encoding="utf-8"
)

if critical_failures:
    raise SystemExit(2)
