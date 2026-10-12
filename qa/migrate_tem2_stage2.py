#!/usr/bin/env python3
"""Preserve TEM2 Stage-2 foundation objects with explicit variant projections."""
import hashlib
import json
from pathlib import Path

SOURCE = "docs/locomotives/diesel/tem2-family/common/stage2_model.json"
BLOB = "7f5c20331f8e8f905d6a8d944d4decac672d620e"
DEST = Path("content-packs/diesel/tem2-family/atlas/stage2-source-lineage.json")
ROOT = Path("content-packs/diesel/tem2-family")
PROFILE = {"tem2-base": ("tem2", "TEM2"), "tem2u-improved": ("tem2u", "TEM2U")}
FLOW_KIND = {"ELECTRICAL_TRACTION_CURRENT": "TRACTION_CURRENT",
             "ELECTRICAL_EXCITATION": "EXCITATION", "ELECTRICAL_CONTROL_POWER": "CONTROL_POWER",
             "ELECTRICAL_AUX_POWER": "AUXILIARY_POWER", "PNEUMATIC_SUPPLY": "AIR_SUPPLY",
             "PNEUMATIC_BRAKE_CONTROL": "CONTROL_PRESSURE",
             "PNEUMATIC_BRAKE_ACTUATION": "BRAKE_CYLINDER_CONTROL"}


def build(donor_root, model_root):
    raw = (donor_root / SOURCE).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != BLOB and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == BLOB
    doc = json.loads(raw)
    audit = json.loads((model_root / ROOT / "migration/source-audit.json").read_text())
    catalog = {(m["variant"], m["sourceId"]): m["canonicalId"] for m in audit["mappings"]
               if m["sourceKind"] == "catalog"}
    sequence = {(m["variant"], m["sourceId"]): m["canonicalId"] for m in audit["mappings"]
                if m["sourceKind"] == "sequences"}
    entries = {}
    for path in (model_root / ROOT).rglob("*.pack.json"):
        for e in json.loads(path.read_text())["entries"]:
            entries[e["id"]] = e["sourceObject"]["object"]
    output = {}
    for kind in ("systems", "equipment", "schemes", "flows"):
        rows = []
        for original in doc[kind]:
            sid = original["id"] if isinstance(original, dict) else original[0]
            targets = []
            for profile, (variant, family) in PROFILE.items():
                applicable = {x[0] for x in doc["equipment"] if profile in x[3]}
                if kind == "systems":
                    projected = f"{family}-{sid}"
                    target = catalog[(variant, projected)]
                    assert entries[target]["title"] == original[1]
                elif kind == "equipment":
                    if profile not in original[3]:
                        continue
                    projected = sid
                    target = catalog[(variant, projected)]
                    assert entries[target]["title"] == original[1]
                elif kind == "schemes":
                    if profile not in original["app"]:
                        continue
                    projected = f"{family}-INT-{sid}"
                    target = catalog[(variant, projected)]
                    assert entries[target]["title"] == original["title"]
                else:
                    if profile not in original[2]:
                        continue
                    projected = f"{family}-{original[3]}-FLOW"
                    target = sequence[(variant, projected)]
                    seq = entries[target]
                    ids = [x for x in original[4] if x in applicable]
                    edges = [{"fromEquipmentId": a, "toEquipmentId": b,
                              "flowKind": FLOW_KIND.get(original[1], "COMMAND"),
                              "label": original[1].replace("_", " ").lower()}
                             for a, b in zip(ids, ids[1:])]
                    assert any(step["edges"] == edges for step in seq["steps"]), (sid, variant)
                targets.append({"variantId": variant, "canonicalId": target,
                                "sourceTargetId": projected})
            assert targets, (kind, sid)
            rows.append({"sourceObject": original, "sourceId": sid, "targets": targets})
        output[kind] = rows
    assert [len(output[k]) for k in output] == [9, 36, 9, 11]
    return {"schemaVersion": 1, "sourcePath": SOURCE, "sourceBlobSha": BLOB,
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
            "generatorPath": "tools/build_tem2_android_assets.py",
            "generatorGitBlob": "f8a8fcbacc9d4acabd921dd86e9f5cb1d1950fe8",
            "sourceObjects": output,
            "rootMetadata": {k: v for k, v in doc.items() if k not in output}}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--model-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    content = json.dumps(build(a.donor_root, a.model_root), ensure_ascii=False,
                         separators=(",", ":")) + "\n"
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    print("TEM2_STAGE2_LINEAGE", 9, 36, 9, 11)
