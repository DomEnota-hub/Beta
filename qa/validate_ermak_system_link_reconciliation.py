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
RESOLUTION = BASE / "migration/source-identity-resolution.json"


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


def load_resolution(root):
    return json.loads((root / RESOLUTION).read_text(encoding="utf-8"))


def validate_resolution(root, data=None):
    """Check the identity overlay against unmodified source objects and fail closed."""
    data = load_resolution(root) if data is None else data
    assert data["schemaVersion"] == 1 and data["donorCommit"] == PIN
    assert data["publicationStatus"] == "CANDIDATE"
    assert data["actionDisposition"] == "INFORMATION_ONLY"
    assert data["runtimeImport"] is False
    all_sources = entries(root, "technical-data/sources", "sources-*.pack.json")
    sources = {entry["id"]: entry for entry in all_sources}
    assert len(sources) == len(all_sources) == 99
    records = data["sourceRecords"]
    assert len(records) == 4
    assert len({row["sourceEntryId"] for row in records}) == 4
    expected_ids = {"ermak.source.es5k_vov_to2", "ermak.source.tass10_tech_data",
                    "ermak.source.dp011_rgups", "ermak.source.dp011_rgups_data"}
    assert {row["sourceEntryId"] for row in records} == expected_ids
    for row in records:
        entry = sources[row["sourceEntryId"]]
        original = entry["sourceObject"]
        source = original["object"]["source"]
        assert {key: row[key] for key in (
            "registryKey", "legacySourceId", "originalDocument", "originalTitle",
            "originalUrl", "originalLocator", "sourcePath", "sourceBlobSha"
        )} == {
            "registryKey": original["object"]["registryKey"],
            "legacySourceId": source["sourceId"], "originalDocument": source["document"],
            "originalTitle": source["title"], "originalUrl": source["url"],
            "originalLocator": source["locator"], "sourcePath": original["sourcePath"],
            "sourceBlobSha": original["sourceBlobSha"],
        }
        assert row["rawIdLinkDisposition"] == "AMBIGUOUS_NO_AUTOMATIC_LINK"
        assert entry["publicationStatus"] == "CANDIDATE"
        assert entry["actionDisposition"] == "INFORMATION_ONLY"
    grouped = defaultdict(list)
    for row in records:
        grouped[row["legacySourceId"]].append(row)
    assert set(grouped) == {"ER-SRC-039", "ER-SRC-041"}
    assert all(len(value) == 2 for value in grouped.values())
    r39, r41 = grouped["ER-SRC-039"], grouped["ER-SRC-041"]
    assert len({row["publicationId"] for row in r39}) == 2
    assert len({row["bibliographicWorkId"] for row in r39}) == 2
    assert len({row["originalUrl"] for row in r39}) == 2
    assert len({row["publicationId"] for row in r41}) == 1
    assert len({row["bibliographicWorkId"] for row in r41}) == 1
    assert len({row["originalUrl"] for row in r41}) == 1
    publications = data["publications"]
    works = data["bibliographicWorks"]
    pub_by_id = {item["id"]: item for item in publications}
    work_by_id = {item["id"]: item for item in works}
    assert len(pub_by_id) == len(publications) == 3
    assert len(work_by_id) == len(works) == 3
    assert set(pub_by_id) == {row["publicationId"] for row in records}
    assert set(work_by_id) == {row["bibliographicWorkId"] for row in records}
    for pub in publications:
        corresponding = [row for row in records if row["publicationId"] == pub["id"]]
        assert pub["bibliographicWorkId"] in work_by_id
        assert sorted(pub["sourceEntryIds"]) == sorted(row["sourceEntryId"] for row in corresponding)
        assert {row["originalUrl"] for row in corresponding} == {pub["url"]}
        assert all(row["bibliographicWorkId"] == pub["bibliographicWorkId"] for row in corresponding)
    verigin = work_by_id["ermak.work.verigin_2024"]
    assert verigin["author"] == "Веригин Олег Сергеевич" and verigin["year"] == 2024
    assert verigin["title"] == ("Влияние электромеханических процессов в тяговом "
                                 "электроприводе магистрального электровоза переменного тока "
                                 "на надежность и долговечность колесных пар")
    assert "Приложение Б, таблица Б.1" in verigin["locator"]
    assert verigin["primaryUrl"] == r41[0]["originalUrl"]
    assert {row["bibliographicWorkId"] for row in r41} == {verigin["id"]}

    system_map = json.loads(gzip.decompress((root / BASE / "migration/source-assets/ermak_system_map.json.gz").read_bytes()))
    unresolved = data["unresolvedSourceIds"]
    source_ids = {entry["sourceObject"]["object"]["source"]["sourceId"] for entry in all_sources}
    assert [item["sourceId"] for item in unresolved] == sorted(set(system_map["sourceIds"]) - source_ids)
    assert all(item["disposition"] == "SOURCE_GAP" and item["automaticMatch"] == "FORBIDDEN"
               and item["requiredEvidence"] == "ORIGINAL_NUMBERED_SOURCE_REGISTRY" for item in unresolved)
    evidence = data["technicalEvidence"]
    assert evidence["sourceDocument"] == "ИДМБ.661142.009РЭ1 (3ТС.001.012РЭ1)"
    assert evidence["sourceSection"].startswith("6.6.1")
    assert evidence["observedChain"] == ["ЭПК У25", "KV12", "КТ1/KV15", "КМ41/КМ42", "шкаф А55"]
    assert evidence["scope"] == "ONLY_DOCUMENTED_EARLY_CIRCUIT"
    assert evidence["requiresExactExecutionConfirmation"] is True
    assert evidence["universalRelationActive"] is False and evidence["runtimeImport"] is False
    assert evidence["rawSystemLink"] == {"from": "SYS-80", "to": "SYS-20",
                                         "relation": "cuts_traction",
                                         "disposition": "HISTORICAL_UNCONFIRMED_AS_UNIVERSAL"}
    assert ["SYS-80", "SYS-20", "cuts_traction"] in system_map["criticalLinks"]
    diagnostic = data["diagnosticGap"]
    ids = {entry["id"] for entry in entries(root, "diagnostics/recommended", "diagnostics-*.pack.json")}
    links = json.loads(gzip.decompress((root / BASE / "migration/source-assets/ermak_links.json.gz").read_bytes()))
    assert diagnostic["scenarioId"] == diagnostic["candidateCardId"] == "ER-DIAG-136"
    assert diagnostic["scenarioId"] in ids and diagnostic["scenarioId"] not in links["indexes"]["byDiagnostic"]
    assert diagnostic["causeStatus"] == "NOT_DOCUMENTALLY_ESTABLISHED"
    assert diagnostic["disposition"] == "SEPARATE_CANDIDATE_WITHOUT_STAGE7_LINK"
    assert diagnostic["autoAddToStage7"] is False and diagnostic["runtimeImport"] is False
    assert diagnostic["generationEvidence"] == [
        {"path": "tools/integrate_beta51_ermak_diagnostics.jq", "gitBlob": "b0c9692487675826622b864e4139b9526724f29d"},
        {"path": "tools/deepen_ermak_p0_batch2.py", "gitBlob": "806d39755c0e8cc6131a21e140a0521b601f2e90"}]
    assert diagnostic["stage7WiringScript"] == {
        "path": ".github/scripts/wire_ermak_stage7_links.py", "gitBlob": "adb1f345e38552e59abab54fe22781eb5323f19a"}
    systems = {item["id"]: item for item in system_map["systems"]}
    cards = {e["sourceObject"]["object"]["systemIds"][0]: e for e in
             entries(root, "technical-data/knowledge", "knowledge-*.pack.json")
             if e["sourceObject"]["object"].get("articleType") == "system"}
    assert data["systemTitles"] == [
        {"systemId": sid, "sourceName": systems[sid]["name"], "cardTitle": cards[sid]["title"]}
        for sid in ("SYS-20", "SYS-70", "SYS-90")]
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = reconcile(args.root)
    validate_resolution(args.root)
    path = args.root / REPORT
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.write_report:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    else:
        assert path.read_text(encoding="utf-8") == encoded, "reconciliation report is stale"
    print("ERMAK_SYSTEM_LINK_RECONCILIATION_PASS", report["counts"])
