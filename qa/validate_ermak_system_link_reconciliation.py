#!/usr/bin/env python3
"""Reconcile pinned Ermak source indexes with candidate packs, without promoting links."""

import argparse
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path


BASE = Path("content-packs/electric/ermak")
REPORT = Path("docs/data-migration/ermak-system-link-reconciliation.json")
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"


def entries(root, relative, pattern):
    paths = sorted((root / BASE / relative).glob(pattern))
    assert paths, relative
    return [entry for path in paths
            for entry in json.loads(path.read_text(encoding="utf-8"))["entries"]]


def reconcile(root):
    migration = root / BASE / "migration"
    index = json.loads((migration / "supplemental-asset-index.json").read_text(encoding="utf-8"))
    assert index["donorCommit"] == PIN
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["canonicalMappingStatus"] == "PENDING_OBJECT_RECONCILIATION"
    assets = {Path(a["destinationPath"]).name: a for a in index["assets"]}
    assert set(assets) == {"ermak_system_map.json.gz", "ermak_links.json.gz"}

    def read_source(name):
        asset = assets[name]
        assert asset["sourceCommit"] == PIN
        assert asset["canonicalDisposition"] == "PENDING_MAPPING"
        compressed = (root / asset["destinationPath"]).read_bytes()
        git_blob = hashlib.sha1(b"blob " + str(len(compressed)).encode() + b"\0" + compressed).hexdigest()
        assert git_blob == asset["sourceBlobSha"]
        assert hashlib.sha256(compressed).hexdigest() == asset["compressedSha256"]
        decoded = gzip.decompress(compressed)
        assert hashlib.sha256(decoded).hexdigest() == asset["decodedSha256"]
        return json.loads(decoded)

    system_map = read_source("ermak_system_map.json.gz")
    links = read_source("ermak_links.json.gz")
    system_entries = [entry for entry in entries(root, "technical-data/knowledge", "knowledge-*.pack.json")
                      if entry["sourceObject"]["object"].get("articleType") == "system"]
    source_entries = entries(root, "technical-data/sources", "sources-*.pack.json")
    diagnostic_entries = entries(root, "diagnostics/recommended", "diagnostics-*.pack.json")
    systems = system_map["systems"]
    system_ids = [s["id"] for s in systems]
    assert len(systems) == len(system_entries) == len(set(system_ids)) == 15
    by_system = defaultdict(list)
    for entry in system_entries:
        assert entry["publicationStatus"] == "CANDIDATE"
        assert entry["actionDisposition"] == "INFORMATION_ONLY"
        for system_id in entry["sourceObject"]["object"]["systemIds"]:
            by_system[system_id].append(entry)
    assert set(by_system) == set(system_ids) == set(links["indexes"]["bySystem"])
    assert all(len(by_system[system_id]) == 1 for system_id in system_ids)

    title_differences = [
        {"systemId": system["id"], "sourceName": system["name"], "cardTitle": by_system[system["id"]][0]["title"]}
        for system in systems if system["name"] != by_system[system["id"]][0]["title"]
    ]
    critical = system_map["criticalLinks"]
    assert len(critical) == 16
    missing_critical = [
        {"from": src, "to": dst, "relation": relation}
        for src, dst, relation in critical
        if dst not in by_system[src][0]["sourceObject"]["object"].get("relatedSystems", [])
    ]
    # relatedSystems expresses adjacency only. Even the 15 matching endpoints
    # do not independently establish the direction or relation label.
    source_id_map = defaultdict(list)
    for entry in source_entries:
        source = entry["sourceObject"]["object"]["source"]
        source_id_map[source["sourceId"]].append({
            "entryId": entry["id"], "document": source.get("document"),
            "title": source.get("title"), "url": source.get("url"),
        })
    missing_source_ids = sorted(set(system_map["sourceIds"]) - set(source_id_map))
    collisions = {source_id: sorted(records, key=lambda item: item["entryId"])
                  for source_id, records in sorted(source_id_map.items()) if len(records) > 1}

    canonical_diagnostics = {entry["id"] for entry in diagnostic_entries}
    link_diagnostics = set(links["indexes"]["byDiagnostic"])
    assert len(canonical_diagnostics) == 136 and len(link_diagnostics) == 135
    missing_diagnostic_ids = sorted(canonical_diagnostics - link_diagnostics)
    assert not (link_diagnostics - canonical_diagnostics)
    assert missing_diagnostic_ids == index["missingDiagnosticLinkIds"]

    report = {
        "schemaVersion": 1,
        "donorCommit": PIN,
        "disposition": "CANDIDATE_SOURCE_RECONCILIATION_ONLY",
        "runtimeImport": False,
        "counts": {"systems": len(systems), "systemCards": len(system_entries),
                   "criticalLinks": len(critical), "criticalPairsPresentInCardAdjacency": len(critical) - len(missing_critical),
                   "sourceEntries": len(source_entries), "canonicalDiagnostics": len(canonical_diagnostics),
                   "linkIndexedDiagnostics": len(link_diagnostics)},
        "titleDifferences": title_differences,
        "criticalLinksMissingFromCardAdjacency": missing_critical,
        "systemMapSourceIdsWithoutSourceEntry": missing_source_ids,
        "reusedRawSourceIds": collisions,
        "diagnosticsMissingFromLinkIndex": missing_diagnostic_ids,
        "interpretation": "Adjacency does not confirm direction or relation type. Source IDs and conflicting registry records are not resolved. No runtime links, action authority, requiredness or variant applicability are promoted.",
    }
    assert [x["systemId"] for x in title_differences] == ["SYS-20", "SYS-70", "SYS-90"]
    assert missing_critical == [{"from": "SYS-80", "to": "SYS-20", "relation": "cuts_traction"}]
    assert missing_source_ids == ["ER-SRC-001", "ER-SRC-017", "ER-SRC-018", "ER-SRC-020", "ER-SRC-021"]
    assert set(collisions) == {"ER-SRC-039", "ER-SRC-041"}
    assert len({r["url"] for r in collisions["ER-SRC-039"]}) == 2
    assert len({r["url"] for r in collisions["ER-SRC-041"]}) == 1
    assert missing_diagnostic_ids == ["ER-DIAG-136"]
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = reconcile(args.root)
    path = args.root / REPORT
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.write_report:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    else:
        assert path.read_text(encoding="utf-8") == encoded, "reconciliation report is stale"
    print("ERMAK_SYSTEM_LINK_RECONCILIATION_PASS", report["counts"])
