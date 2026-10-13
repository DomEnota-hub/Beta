#!/usr/bin/env python3
"""Pinned CHME3/T/E data importer with exact-content merge and variant isolation."""
import base64
import collections
import gzip
import hashlib
import json
from pathlib import Path

DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
VARIANTS = ("chme3", "chme3t", "chme3e")
PINS = {
    ("chme3", "catalog"): "fa63f0ca6bf46e91780d77e6e17131cd00a4df7e",
    ("chme3", "diagnostics"): "6a6068ad1ea54cb964b65a10ecf5c2425b2276e8",
    ("chme3t", "catalog"): "3682ce0b3a8607f972dec8527cb9af437484af95",
    ("chme3t", "diagnostics"): "41809c6464113f48ef032ed70d2cb4483f12c28e",
    ("chme3e", "catalog"): "095e3230dd40f8b1dbc93cd5181a69fcabd1975f",
    ("chme3e", "diagnostics"): "1ab9ae40bc90479eacb006d0eb62dd45e9f387fe",
}
TYPE_BY_SECTION = {
    "ACCEPTANCE": "ACCEPTANCE_ITEM", "EQUIPMENT": "EQUIPMENT",
    "KNOWLEDGE": "KNOWLEDGE", "DIAGNOSTICS": "KNOWLEDGE",
    "SYSTEMS": "KNOWLEDGE", "ELECTRICAL": "KNOWLEDGE", "PNEUMATIC": "KNOWLEDGE",
}
LINK_TYPES = {"ACCEPTANCE_ITEM":"ACCEPTANCE_ITEM", "EQUIPMENT":"EQUIPMENT",
              "KNOWLEDGE":"KNOWLEDGE", "DIAGNOSTIC_SCENARIO":"RELATED_SCENARIO"}
ROOT = Path("content-packs/diesel/chme3-family")
BRAKE_RESISTOR_SOURCE_ID = "CHME3T-EQ-BRAKE-RESISTORS"
BRAKE_RESISTOR_PREFERRED_NAME = "Блок тормозных резисторов"


def read_assets(donor_dir):
    result = {}
    for (variant, kind), sha in PINS.items():
        file = donor_dir / f"chme3_{variant}_{kind}.json.gz.b64"
        raw = base64.b64decode(file.read_text())
        assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == sha
        doc = json.loads(gzip.decompress(raw))
        records = doc["entries" if kind == "catalog" else "scenarios"]
        assert len(records) == len({r["id"] for r in records})
        result[(variant, kind)] = records
    return result


def compact(record):
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build(donor_dir):
    arrays = read_assets(donor_dir)
    groups = collections.defaultdict(list)
    for (variant, kind), records in arrays.items():
        for index, record in enumerate(records):
            groups[(kind, record["id"], compact(record))].append((variant, index, record))
    conflicts = collections.Counter((kind, source_id) for kind, source_id, _ in groups)
    variant_map = {}
    entries = {"catalog": [], "diagnostics": []}
    mappings = []
    for (kind, source_id, _), copies in sorted(groups.items()):
        variants = [v for v, _, _ in copies]
        suffix = "" if conflicts[(kind, source_id)] == 1 else "." + "-".join(variants)
        canonical_id = f"chme3.{kind}.{source_id.lower()}{suffix}"
        record = copies[0][2]
        display_title = record["title"]
        if kind == "catalog" and source_id == BRAKE_RESISTOR_SOURCE_ID:
            assert variants == ["chme3t"]
            assert record["title"] == "Тормозные резисторы"
            assert "тормозные резисторы" in record["searchAliases"]
            display_title = BRAKE_RESISTOR_PREFERRED_NAME
        path = f"app/src/main/assets/technical/chme3_{copies[0][0]}_{kind}.json.gz"
        content_type = ("DIAGNOSTIC_SCENARIO" if kind == "diagnostics" else
                        TYPE_BY_SECTION[record["section"]])
        entry = {
            "id": canonical_id, "type": content_type,
            "owner": {"kind":"MODEL", "modelId":"chme3-family"},
            "applicability": {"modelIds":["chme3-family"], "variantIds": variants},
            "layer":"STANDARD", "publicationStatus":"CANDIDATE",
            "provenance":"UNKNOWN", "sourceStatus":"UNKNOWN",
            "actionDisposition":"INFORMATION_ONLY",
            "title":display_title,
            "summary": record.get("subtitle") or record.get("symptom") or None,
            "searchTerms": record.get("searchAliases", []) if kind == "catalog" else record.get("searchTerms", []),
            "blocks": record.get("blocks", []) if kind == "catalog" else [],
            "links":[],
            "sourceObject":{"sourcePath":path,"sourceBlobSha":PINS[(copies[0][0],kind)],
                            "object":record},
        }
        entries[kind].append(entry)
        for j,(variant,index,_) in enumerate(copies):
            assert (variant, kind, source_id) not in variant_map
            variant_map[(variant, kind, source_id)] = entry
            mappings.append({"variant":variant,"sourceKind":kind,"sourceId":source_id,
                             "sourceIndex":index,"canonicalId":canonical_id,
                             "disposition":"MIGRATED" if j == 0 else "MERGED_WITH_CANONICAL",
                             "gitBlob":PINS[(variant,kind)]})
    # Every link is resolved in its own variant. Shared entries may have
    # variant-specific targets, so link applicability narrows that edge.
    unresolved = []
    for kind, grouped in entries.items():
        for entry in grouped:
            original = entry["sourceObject"]["object"]
            for variant in entry["applicability"]["variantIds"]:
                ids = (original.get("relatedIds", []) if kind == "catalog" else
                       original.get("equipmentRefs", []))
                for target_id in ids:
                    target = variant_map.get((variant, "catalog", target_id))
                    if target is None:
                        unresolved.append({"source":entry["id"], "variant":variant,
                                           "sourceTargetId":target_id})
                        continue
                    link = {"type":LINK_TYPES[target["type"]],"targetId":target["id"],
                            "role":"relatedIds" if kind == "catalog" else "equipmentRefs",
                            "applicability":{"variantIds":[variant]}}
                    entry["links"].append(link)
    outputs = {}
    for kind, grouped in entries.items():
        for offset in range(0,len(grouped),20):
            n=offset//20+1
            chunk=grouped[offset:offset+20]
            pack={
                "manifest":{"schemaVersion":1,"packId":f"chme3-family.{kind}.{n:02d}",
                    "packVersion":"0.1.0","family":"DIESEL","modelIds":["chme3-family"],
                    "variantIds":sorted({v for e in chunk for v in e["applicability"]["variantIds"]}),
                    "locale":"ru-RU","entries":[e["id"] for e in chunk],
                    "requiresRuntime":"1.1.0","sourceCatalogVersion":f"test-{DONOR[:8]}-chme3",
                    "checksums":{f"{v}.{kind}.gitBlob":PINS[(v,kind)] for v in VARIANTS}},
                "entries":chunk,
            }
            path=ROOT/("technical-data/catalog" if kind=="catalog" else
                       "diagnostics/recommended")/f"{kind}-{n:02d}.pack.json"
            outputs[path]=json.dumps(pack,ensure_ascii=False,separators=(",", ":"))+"\n"
    audit={"schemaVersion":1,"donorCommit":DONOR,
           "sourceCounts":{f"{v}.{k}":len(a) for (v,k),a in arrays.items()},
           "canonicalCounts":{k:len(e) for k,e in entries.items()},
           "mappings":sorted(mappings,key=lambda x:(x["variant"],x["sourceKind"],x["sourceIndex"])),
           "unresolvedReferences":unresolved,
           "linkCount":sum(len(e["links"]) for a in entries.values() for e in a)}
    outputs[ROOT/"migration/source-audit.json"]=(
        json.dumps(audit,ensure_ascii=False,separators=(",", ":"))+"\n")
    return outputs


if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--donor-dir",type=Path,required=True)
    p.add_argument("--output-root",type=Path,default=Path("."))
    a=p.parse_args()
    outputs=build(a.donor_dir)
    for path,content in outputs.items():
        target=a.output_root/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(content)
    print("CHME3_VARIANT_PACKS",len(outputs)-1)
