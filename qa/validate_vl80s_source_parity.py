#!/usr/bin/env python3
"""Pinned VL80S donor-to-candidate parity gate, without runtime promotion.

The original nine JSON/GZIP catalogs are compared to preserved source objects.
Projected pack identity is checked separately; no safety/source approval follows.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

DONOR_SHA = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
ASSET_DIR = "app/src/main/assets/technical/"
ASSETS = (
    "vl80s_acceptance.json.gz",
    "vl80s_diagnostics.json.gz",
    "vl80s_electrical.json.gz",
    "vl80s_electrical_variants.json.gz",
    "vl80s_equipment.json.gz",
    "vl80s_pantograph_reference_pack.json",
    "vl80s_pneumatic.json.gz",
    "vl80s_pneumatic_variants.json.gz",
    "vl80s_variants.json.gz",
)
ROOT = Path(__file__).resolve().parents[1]
MODEL = "content-packs/electric/vl80s/"


def git_blob(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + bytes([0]) + payload).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def assert_candidate(obj):
    assert obj["donorCommit"] == DONOR_SHA
    assert obj["modelOwner"] == "vl80s"
    assert obj["publicationStatus"] == "CANDIDATE"
    assert obj["runtimeImport"] is False


def read_pinned(row, donor):
    source = row["sourcePath"]
    assert source == ASSET_DIR + Path(source).name
    raw = (donor / source).read_bytes()
    assert len(raw) == row["compressedBytes"], source
    assert git_blob(raw) == row["gitBlobSha"], source
    assert row["format"] in {"json.gz", "json"}
    decoded = gzip.decompress(raw) if row["format"] == "json.gz" else raw
    return json.loads(decoded.decode("utf-8-sig"))


def pack_entries(root, relative_glob):
    entries = []
    for path in sorted((root / MODEL).glob(relative_glob)):
        pack = json.loads(path.read_text(encoding="utf-8"))
        assert pack["manifest"]["modelIds"] == ["vl80s"], path
        assert pack["manifest"]["entries"] == [e["id"] for e in pack["entries"]], path
        entries.extend(pack["entries"])
    assert len(entries) == len({e["id"] for e in entries}), relative_glob
    return entries


def validate(root, donor):
    crosswalk = json.loads((root / "docs/migration/donor-asset-crosswalk.json").read_text())
    assert crosswalk["donor"] == {"repository": "DomEnota-hub/Test-", "commit": DONOR_SHA}
    rows = {Path(r["sourcePath"]).name: r for r in crosswalk["assets"] if r["family"] == "vl80s"}
    assert set(rows) == set(ASSETS), (set(ASSETS) - set(rows), set(rows) - set(ASSETS))
    sources = {name: read_pinned(rows[name], donor) for name in ASSETS}

    acceptance = json.loads((root / MODEL / "migration/acceptance-source.candidate.json").read_text())
    assert_candidate(acceptance)
    assert acceptance["sourcePath"] == rows["vl80s_acceptance.json.gz"]["sourcePath"]
    assert acceptance["sourceBlobSha"] == rows["vl80s_acceptance.json.gz"]["gitBlobSha"]
    assert acceptance["sourceObject"] == sources["vl80s_acceptance.json.gz"]
    assert acceptance["sourceObjectSha256"] == digest(acceptance["sourceObject"])

    diagnostic = json.loads((root / MODEL / "diagnostics/migration/diagnostics-source.candidate.json").read_text())
    assert_candidate(diagnostic)
    assert diagnostic["actionAuthorityGranted"] is False
    assert diagnostic["sourcePath"] == rows["vl80s_diagnostics.json.gz"]["sourcePath"]
    assert diagnostic["sourceBlobSha"] == rows["vl80s_diagnostics.json.gz"]["gitBlobSha"]
    assert diagnostic["sourceObject"] == sources["vl80s_diagnostics.json.gz"]
    assert diagnostic["sourceObjectSha256"] == digest(diagnostic["sourceObject"])

    scheme = json.loads((root / MODEL / "migration/scheme-source-catalogs.candidate.json").read_text())
    assert_candidate(scheme)
    assert len(scheme["sources"]) == 5
    seen = set()
    for item in scheme["sources"]:
        name = Path(item["sourcePath"]).name
        assert name in ASSETS and name not in {"vl80s_acceptance.json.gz", "vl80s_diagnostics.json.gz", "vl80s_equipment.json.gz", "vl80s_pantograph_reference_pack.json"}
        assert name not in seen
        seen.add(name)
        assert item["sourcePath"] == rows[name]["sourcePath"]
        assert item["sourceBlobSha"] == rows[name]["gitBlobSha"]
        assert item["sourceObject"] == sources[name], name
        assert item["sourceObjectSha256"] == digest(item["sourceObject"]), name
    assert seen == set(ASSETS) - {"vl80s_acceptance.json.gz", "vl80s_diagnostics.json.gz", "vl80s_equipment.json.gz", "vl80s_pantograph_reference_pack.json"}

    pantograph = json.loads((root / MODEL / "diagnostics/migration/pantograph-reference-source.candidate.json").read_text())
    assert pantograph["donorCommit"] == DONOR_SHA
    assert pantograph["publicationStatus"] == "CANDIDATE"
    assert pantograph["runtimeImport"] is False and pantograph["actionAuthorityGranted"] is False
    assert pantograph["sourcePath"] == rows["vl80s_pantograph_reference_pack.json"]["sourcePath"]
    assert pantograph["sourceBlobSha"] == rows["vl80s_pantograph_reference_pack.json"]["gitBlobSha"]
    assert pantograph["sourceObject"] == sources["vl80s_pantograph_reference_pack.json"]
    assert pantograph["sourceObjectSha256"] == digest(pantograph["sourceObject"])

    equipment = json.loads((root / MODEL / "migration/equipment-context.candidate.json").read_text())
    assert_candidate(equipment)
    assert equipment["sourcePath"] == rows["vl80s_equipment.json.gz"]["sourcePath"]
    assert equipment["sourceBlobSha"] == rows["vl80s_equipment.json.gz"]["gitBlobSha"]
    source_equipment = sources["vl80s_equipment.json.gz"]
    assert equipment["sourceRootWithoutRecords"] == {k: v for k, v in source_equipment.items() if k != "records"}
    assert equipment["sourceRootSha256"] == digest(equipment["sourceRootWithoutRecords"])
    donor_equipment_ids = [e["id"] for e in source_equipment["records"]]
    projected_equipment = pack_entries(root, "atlas/equipment/*.pack.json")
    assert len(donor_equipment_ids) == len(set(donor_equipment_ids)) == 89
    assert {e["id"] for e in projected_equipment} == set(donor_equipment_ids)
    assert equipment["recordCountPreservedInEquipmentPacks"] == 89

    donor_acceptance_ids = {e["id"] for e in sources["vl80s_acceptance.json.gz"]["items"]}
    projected_acceptance = pack_entries(root, "acceptance/items.pack.json")
    assert len(donor_acceptance_ids) == len(projected_acceptance) == 66
    assert {e["id"] for e in projected_acceptance} == donor_acceptance_ids

    donor_diag_ids = {e["id"] for e in sources["vl80s_diagnostics.json.gz"]["scenarios"]}
    projected_diagnostics = (pack_entries(root, "diagnostics/recommended/*.pack.json") +
                             pack_entries(root, "diagnostics/extended/supplemental-operational/*.pack.json"))
    assert len(donor_diag_ids) == len(projected_diagnostics) == 103
    assert {e["id"] for e in projected_diagnostics} == {"vl80s.diag." + i for i in donor_diag_ids}
    assert all(e["publicationStatus"] == "CANDIDATE" for e in projected_diagnostics)

    profile = json.loads((root / MODEL / "profile-catalog.json").read_text())
    donor_buckets = [e["id"] for e in sources["vl80s_variants.json.gz"]["physicalBuckets"]]
    assert len(donor_buckets) == 9
    assert [e["id"] for e in profile["physicalBuckets"]] == donor_buckets
    assert profile["defaultVariantId"] == "vl80s_unknown"

    runtime = json.loads((root / MODEL / "runtime-index.json").read_text())
    assert runtime["modelId"] == "vl80s"
    assert not any("migration/" in p or "candidate" in p or "research" in p
                   for p in runtime["packs"])
    result = {"sourceAssets": len(sources), "fullPreservedSources": 8,
              "equipmentContextAndIds": 89, "acceptanceIds": 66,
              "diagnosticIds": 103, "variantBuckets": 9,
              "diagnosticEdges": len(sources["vl80s_diagnostics.json.gz"]["edges"])}
    assert result["diagnosticEdges"] == 1181
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--donor-dir", type=Path, required=True)
    a = p.parse_args()
    print("VL80S_PINNED_SOURCE_PARITY_PASS", validate(a.root, a.donor_dir))
