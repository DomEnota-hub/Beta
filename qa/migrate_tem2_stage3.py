#!/usr/bin/env python3
"""Preserve pinned Stage-3 source objects and verify their generated diagnostics."""
import hashlib
import json
from pathlib import Path

SOURCE = "docs/locomotives/diesel/tem2-family/common/stage3_model.json"
BLOB = "4234e401eb9d6ec03802669d0f74962cb23ea5c4"
ROOT = Path("content-packs/diesel/tem2-family")
LINEAGE = ROOT / "diagnostics/stage3-source-lineage.json"
SOURCES = ROOT / "sources/stage3-research.pack.json"
PROFILE = {"tem2-base": "tem2", "tem2u-improved": "tem2u"}


def read_doc(donor_root, path, expected):
    raw = (donor_root / path).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != expected and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == expected, path
    return json.loads(raw)


def build(donor_root, model_root):
    stage3 = read_doc(donor_root, SOURCE, BLOB)
    stage2 = json.loads((donor_root / "docs/locomotives/diesel/tem2-family/common/stage2_model.json").read_text())
    registry = json.loads((donor_root / "docs/locomotives/diesel/tem2-family/common/source_registry.json").read_text())
    audit = json.loads((model_root / ROOT / "migration/source-audit.json").read_text())
    lookup = {(m["variant"], m["sourceId"]): m["canonicalId"] for m in audit["mappings"]
              if m["sourceKind"] == "diagnostics"}
    canonical = {}
    for path in (model_root / ROOT / "diagnostics/recommended").glob("*.pack.json"):
        for entry in json.loads(path.read_text())["entries"]:
            canonical[entry["id"]] = entry["sourceObject"]["object"]
    source_by_id = {x["id"]: x for x in registry["sources"] + stage3["researchEvidence"]}
    source_title = {key: f"{x['title']} ({x.get('year', 'редакция не указана')}; {x.get('currentness', 'статус не указан')}; применимость: {', '.join(x.get('applicability', []))})"
                    for key, x in source_by_id.items()}
    aliases = {}
    for phrase, sid in stage3["assistantSemantics"]["routeCases"] + stage3["assistantSemantics"]["spokenQueries"]:
        aliases.setdefault(sid, []).append(phrase)
    aliases.setdefault("TEM2-DIAG-016", []).append("компрессор не выключается")
    aliases.setdefault("TEM2-DIAG-009", []).append("выбило защиту")
    aliases.setdefault("TEM2-DIAG-006", []).append("дизель сам заглох")
    applicable = {variant: {x[0] for x in stage2["equipment"] if profile in x[3]}
                  for profile, variant in PROFILE.items()}
    records = []
    for scenario in stage3["scenarios"]:
        targets = []
        for profile in scenario["profileIds"]:
            variant = PROFILE[profile]
            graph = scenario["runtimeGraph"]
            nodes = []
            for node in graph["nodes"]:
                body = node["text"]
                if node["type"] == "check":
                    body += "\nОжидается: " + node["expected"] + "\nПри отклонении: " + node["ifAbnormal"]
                nodes.append({"id": node["id"], "type": node["type"], "text": body,
                              "nextNodeId": node.get("nextNodeId"),
                              "actionLevel": node.get("actionLevel", "INFORMATION_ONLY"),
                              "choices": node.get("choices", []) + ([{
                                  "label": "Не знаю / исполнение не подтверждено",
                                  "nextNodeId": node["uncertainNextNodeId"],
                                  "responseKind": "UNKNOWN"}]
                                  if node.get("uncertainNextNodeId") else [])})
            expected = {"id": scenario["id"], "title": scenario["title"],
                        "symptom": "; ".join(scenario["symptoms"]),
                        "category": scenario["category"], "severity": scenario["riskClass"],
                        "equipmentRefs": [x for x in scenario["equipmentIds"] if x in applicable[variant]],
                        "searchTerms": scenario["queries"] + scenario["symptoms"] + aliases.get(scenario["id"], []),
                        "sourceAgeNote": "Исторические источники не дают действующего разрешения на действия.",
                        "informationConfidence": "SOURCE_BACKED_FUNCTIONAL",
                        "applicability": {"profiles": scenario["profileIds"], "variantSelectionRequired": True},
                        "graph": {"startNodeId": graph["startNodeId"], "nodes": nodes},
                        "sourceRefs": [{"sourceId": sid,
                                        "document": source_title.get(sid, "Источник не установлен"),
                                        "role": "FACTORY_BASELINE_OR_CURRENT_REFERENCE"}
                                       for sid in scenario["evidenceRefs"]]}
            target = lookup[(variant, scenario["id"])]
            assert canonical[target] == expected, (scenario["id"], variant)
            targets.append({"variantId": variant, "canonicalId": target,
                            "projectionVerified": True})
        records.append({"sourceObject": scenario, "targets": targets})
    assert len(records) == 24 and sum(len(x["targets"]) for x in records) == 46
    lineage = {"schemaVersion": 1, "sourcePath": SOURCE, "sourceBlobSha": BLOB,
               "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
               "generatorPath": "tools/build_tem2_android_assets.py",
               "generatorGitBlob": "f8a8fcbacc9d4acabd921dd86e9f5cb1d1950fe8",
               "scenarios": records,
               "rootMetadata": {k: v for k, v in stage3.items()
                                if k not in ("scenarios", "researchEvidence")}}
    source_entries = [{"id": "tem2.source." + record["id"].lower(), "type": "SOURCE",
                       "owner": {"kind": "MODEL", "modelId": "tem2-family"},
                       "applicability": {"modelIds": ["tem2-family"], "variantIds": ["tem2"]},
                       "layer": "STANDARD", "publicationStatus": "CANDIDATE",
                       "provenance": "UNKNOWN", "sourceStatus": "UNKNOWN",
                       "actionDisposition": "INFORMATION_ONLY", "title": record["title"],
                       "summary": ", ".join(record["use"]), "sourceRefs": [], "links": [],
                       "sourceObject": {"sourcePath": SOURCE, "sourceBlobSha": BLOB,
                                        "object": record}}
                      for record in stage3["researchEvidence"]]
    manifest = {"schemaVersion": 1, "packId": "tem2-family.sources.stage3-research",
                "packVersion": "0.1.0", "family": "DIESEL", "modelIds": ["tem2-family"],
                "variantIds": ["tem2"], "locale": "ru-RU",
                "entries": [x["id"] for x in source_entries], "requiresRuntime": "1.1.0",
                "sourceCatalogVersion": "test-3176d6ee-tem2-stage3",
                "checksums": {"stage3_model.json.gitBlob": BLOB}}
    return {LINEAGE: json.dumps(lineage, ensure_ascii=False, separators=(",", ":")) + "\n",
            SOURCES: json.dumps({"manifest": manifest, "entries": source_entries},
                                ensure_ascii=False, separators=(",", ":")) + "\n"}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--model-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    for path, content in build(a.donor_root, a.model_root).items():
        target = a.output_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    print("TEM2_STAGE3_LINEAGE", 24, 46, 3)
