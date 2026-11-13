#!/usr/bin/env python3
"""Compare pinned generator literals with the preserved Ermak source objects."""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/electric/ermak/migration/source-assets/enrich_ermak_pantograph.py"
SOURCE_BLOB = "a913c985c346289cb3202a00d1a331fce354bf9a"


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def constants(raw):
    tree = ast.parse(raw.decode("utf-8"))
    values = {}

    def resolve(node):
        if isinstance(node, ast.Name):
            return values[node.id]
        if isinstance(node, ast.Dict):
            return {resolve(k): resolve(v) for k, v in zip(node.keys, node.values)}
        if isinstance(node, (ast.List, ast.Tuple)):
            return [resolve(item) for item in node.elts]
        return ast.literal_eval(node)

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                values[node.targets[0].id] = resolve(node.value)
            except (ValueError, TypeError, KeyError):
                pass
    return values


def main():
    raw = SOURCE.read_bytes()
    assert blob(raw) == SOURCE_BLOB
    values = constants(raw)
    params = values["PARAMETERS"]
    assert len(params) == 15
    eq = json.loads((ROOT / "content-packs/electric/ermak/atlas/equipment/equipment-01.pack.json").read_text())
    kb = json.loads((ROOT / "content-packs/electric/ermak/technical-data/knowledge/knowledge-01.pack.json").read_text())
    audit = json.loads((ROOT / "content-packs/electric/ermak/migration/source-audit.json").read_text())
    equipment = next(e for e in eq["entries"] if e["id"] == values["EQUIPMENT_ID"])["sourceObject"]["object"]
    article = next(e for e in kb["entries"] if e["id"] == values["ARTICLE_ID"])["sourceObject"]["object"]
    assert equipment["parameters"] == params
    expected_kb = [{"name": p["name"], "value": p["value"], "unit": p["unit"],
                    "applicability": p.get("condition", "ТАсС-10-01; базовое исполнение 2ЭС5К/3ЭС5К"),
                    "status": "BASE_CONFIRMED", "sourceRefs": [p["sourceId"]]} for p in params]
    assert article["keyParameters"] == expected_kb
    assert article["atlasData"]["parameterCoverage"] == {"status": "documented", "count": 15}
    assert equipment["parameterCoverage"] == {"status": "documented", "count": 15}
    assert audit["sourceRootMetadata"]["equipment"]["sourceRegistry"]["TASS10_TECH_DATA"] == values["DATA_REF"]
    print("ERMAK_PANTOGRAPH_GENERATOR_PARAMETERS_PASS 15 15")


if __name__ == "__main__":
    main()
