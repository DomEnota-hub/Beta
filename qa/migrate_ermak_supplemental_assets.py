#!/usr/bin/env python3
"""Index the two byte-for-byte pinned Ermak supplements as archival sources."""
import gzip
import hashlib
import json
from pathlib import Path

DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
PREFIX = "content-packs/electric/ermak/migration/source-assets/"
DEST = Path("content-packs/electric/ermak/migration/supplemental-asset-index.json")
PINS = (
    ("ermak_links.json.gz", "432eb86db028b8c6c1413ad054bc110fa83ce633",
     "cfe49bb00baa0baffcbc0012ac1cec7cd68495b5d12117b06a84599bc4d3b4e0"),
    ("ermak_system_map.json.gz", "bd17468332261f7fb965de6e1ba3d7f0b28a05b2",
     "78b617dad7af46bf9abe1e20380fbbf559f602da7dcde9bad835e2df007e3765"),
)


def audit_links(document: dict) -> dict:
    indexes = document["indexes"]
    groups = {name: set(indexes[name]) for name in
              ("byEquipment", "bySystem", "byDiagnostic", "byScheme")}
    fields = {
        "byEquipment": {"systemIds": "bySystem", "diagnosticIds": "byDiagnostic", "schemeIds": "byScheme"},
        "bySystem": {"equipmentIds": "byEquipment", "diagnosticIds": "byDiagnostic", "schemeIds": "byScheme"},
        "byDiagnostic": {"systemIds": "bySystem", "equipmentIds": "byEquipment",
                         "relatedScenarioIds": "byDiagnostic"},
        "byScheme": {"systemIds": "bySystem", "equipmentIds": "byEquipment"},
    }
    missing = []
    edge_count = 0
    for group, mappings in fields.items():
        for source_id, obj in indexes[group].items():
            for field, target_group in mappings.items():
                for target in obj.get(field, []):
                    edge_count += 1
                    if target not in groups[target_group]:
                        missing.append({"sourceGroup": group, "sourceId": source_id,
                                        "field": field, "targetId": target})
    diagnostic_pairs = set()
    scheme_pairs = set()
    for diag_id, obj in indexes["byDiagnostic"].items():
        for link in obj.get("schemeLinks", []):
            scheme_id = link["schemeId"]
            edge_count += 1
            if scheme_id not in groups["byScheme"]:
                missing.append({"sourceGroup": "byDiagnostic", "sourceId": diag_id,
                                "field": "schemeLinks", "targetId": scheme_id})
            diagnostic_pairs.add((diag_id, scheme_id))
    for scheme_id, obj in indexes["byScheme"].items():
        for link in obj.get("diagnosticLinks", []):
            diag_id = link["diagnosticId"]
            edge_count += 1
            if diag_id not in groups["byDiagnostic"]:
                missing.append({"sourceGroup": "byScheme", "sourceId": scheme_id,
                                "field": "diagnosticLinks", "targetId": diag_id})
            scheme_pairs.add((diag_id, scheme_id))
    assert diagnostic_pairs == scheme_pairs, "diagnostic/scheme links are not reciprocal"
    assert len(diagnostic_pairs) == document["statistics"]["canonicalDiagnosticSchemePairs"]
    return {
        "indexedCounts": {name: len(ids) for name, ids in groups.items()},
        "internalReferenceOccurrences": edge_count,
        "reciprocalDiagnosticSchemePairs": len(diagnostic_pairs),
        "unresolvedInternalReferences": missing,
        "knowledgeReferencesExternallyUnverified": True,
        "profileCompatibilityExternallyUnverified": True,
    }


def build(root: Path) -> dict:
    assets = []
    parsed = {}
    for name, blob_sha, sha256 in PINS:
        destination = PREFIX + name
        data = (root / destination).read_bytes()
        git_sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert git_sha == blob_sha, (name, "donor Git blob mismatch")
        assert hashlib.sha256(data).hexdigest() == sha256, (name, "compressed SHA-256 mismatch")
        decoded = gzip.decompress(data)
        doc = json.loads(decoded)
        parsed[name] = doc
        assets.append({
            "sourceRepo": "DomEnota-hub/Test-",
            "sourceCommit": DONOR,
            "sourcePath": "app/src/main/assets/technical/" + name,
            "sourceBlobSha": blob_sha,
            "compressedSha256": sha256,
            "decodedSha256": hashlib.sha256(decoded).hexdigest(),
            "destinationPath": destination,
            "sourceTopLevelKeys": list(doc),
            "preservation": "EXACT_COMPRESSED_BYTES",
            "canonicalDisposition": "PENDING_MAPPING",
        })
    links = parsed["ermak_links.json.gz"]
    systems = parsed["ermak_system_map.json.gz"]
    assert len(systems["systems"]) == 15
    assert len(systems["criticalLinks"]) == 16
    assert len(systems["openQuestions"]) == 7
    assert len(systems["sourceIds"]) == 13
    assert len(links["indexes"]["byEquipment"]) == 111
    assert len(links["indexes"]["bySystem"]) == 15
    assert len(links["indexes"]["byDiagnostic"]) == 135
    assert len(links["indexes"]["byScheme"]) == 22
    assert len(set(links["indexes"]["byDiagnostic"])) == 135
    return {
        "schemaVersion": 1,
        "donorCommit": DONOR,
        "publicationStatus": "CANDIDATE",
        "actionDisposition": "INFORMATION_ONLY",
        "runtimeImport": False,
        "canonicalMappingStatus": "PENDING_OBJECT_RECONCILIATION",
        "assets": assets,
        "observedCounts": {
            "systemMapSystems": 15,
            "systemMapCriticalLinks": 16,
            "systemMapOpenQuestions": 7,
            "systemMapSourceIds": 13,
            "linkIndexEquipment": 111,
            "linkIndexSystems": 15,
            "linkIndexDiagnostics": 135,
            "linkIndexSchemes": 22,
            "canonicalCandidateDiagnostics": 136,
        },
        "missingDiagnosticLinkIds": ["ER-DIAG-136"],
        "sourceGraphAudit": audit_links(links),
        "boundary": "Donor PASS labels and links are historical source data, not current safety, variant, publication or action authority.",
    }


if __name__ == "__main__":
    root = Path(".")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(build(root), ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
