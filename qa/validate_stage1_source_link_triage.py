#!/usr/bin/env python3
"""Evidence-gated source-link triage. Never promotes candidate data to runtime."""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR_SHA = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
LEDGER = "docs/migration/stage1-source-link-triage.json"
CHME = "content-packs/diesel/chme3-family/migration/source-audit.json"
ERMAK = "content-packs/electric/ermak/migration/source-audit.json"


def read(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def validate(ledger: dict, chme: dict, ermak: dict) -> dict:
    assert all(x["donorCommit"] == DONOR_SHA for x in (ledger, chme, ermak))
    assert ledger["schemaVersion"] == 1
    assert ledger["scope"] == "SOURCE_IDENTITY_TRIAGE_ONLY"
    assert ledger["runtimeImport"] is False
    assert ledger["actionDisposition"] == "INFORMATION_ONLY"
    assert ledger["chme3"]["sourceAudit"] == CHME
    assert ledger["ermak"]["sourceAudit"] == ERMAK

    refs = chme["unresolvedReferences"]
    assert len(refs) == ledger["chme3"]["unresolvedReferenceCount"] == 610
    assert len({(x["source"], x["variant"], x["sourceTargetId"]) for x in refs}) == len(refs)
    expected = defaultdict(lambda: {"referenceCount": 0, "variants": set()})
    for ref in refs:
        group = expected[ref["sourceTargetId"]]
        group["referenceCount"] += 1
        group["variants"].add(ref["variant"])
    mapped = defaultdict(set)
    for mapping in chme["mappings"]:
        mapped[mapping["sourceId"]].add(mapping["variant"])
    groups = ledger["chme3"]["targetGroups"]
    assert len(groups) == len(expected) == 19
    assert len({g["sourceTargetId"] for g in groups}) == len(groups)
    for group in groups:
        key = group["sourceTargetId"]
        assert key in expected, f"unrecognized CHME target {key}"
        assert group["referenceCount"] == expected[key]["referenceCount"], key
        assert group["variants"] == sorted(expected[key]["variants"]), key
        assert group["mappedSourceVariants"] == sorted(mapped[key]), key
        mismatch = bool(mapped[key]) and not expected[key]["variants"].issubset(mapped[key])
        assert group["variantMismatch"] is mismatch, key
        assert group["reviewStatus"] == "UNRESOLVED_QUARANTINED", key
        assert group["runtimeImport"] is False, key
        requirement = ("EXPLICIT_VARIANT_APPLICABILITY_AND_ORIGINAL_SOURCE" if mismatch
                       else "PINNED_VARIANT_SPECIFIC_SCHEME_OR_EQUIPMENT_SOURCE")
        assert group["requiredEvidence"] == requirement, key

    unresolved = {x["sourceId"]: x for x in ermak["sourceReferences"]
                  if x["disposition"] != "LINKED"}
    entries = ledger["ermak"]["sourceIds"]
    assert len(entries) == len(unresolved) == 57
    assert len({x["sourceId"] for x in entries}) == len(entries)
    total = sum(x["occurrences"] for x in unresolved.values())
    assert total == ledger["ermak"]["unresolvedOccurrenceCount"] == 548
    statuses = Counter()
    for entry in entries:
        key = entry["sourceId"]
        assert key in unresolved, f"unrecognized Ermak source {key}"
        source = unresolved[key]
        assert entry["occurrences"] == source["occurrences"], key
        assert entry["registryKeys"] == source["registryKeys"], key
        assert entry["sourceDisposition"] == source["disposition"], key
        assert entry["reviewStatus"] == "UNRESOLVED_QUARANTINED", key
        assert entry["runtimeImport"] is False, key
        requirement = ("ORIGINAL_SOURCE_REGISTRY_ENTRY_AND_DOCUMENT_IDENTITY"
                       if source["disposition"] == "AMBIGUOUS_SOURCE_ID"
                       else "ORIGINAL_SOURCE_REGISTRY_OR_VERIFIED_PUBLICATION")
        assert entry["requiredEvidence"] == requirement, key
        statuses[source["disposition"]] += source["occurrences"]
    assert statuses == {"SOURCE_GAP": 542, "AMBIGUOUS_SOURCE_ID": 6}
    return {"chme3UnresolvedReferences": len(refs), "chme3DistinctTargets": len(groups),
            "chme3CrossVariantTargets": [x["sourceTargetId"] for x in groups if x["variantMismatch"]],
            "ermakUnresolvedIds": len(entries), "ermakSourceGapOccurrences": statuses["SOURCE_GAP"],
            "ermakAmbiguousOccurrences": statuses["AMBIGUOUS_SOURCE_ID"],
            "runtimeImport": False}


def main() -> None:
    result = validate(read(ROOT, LEDGER), read(ROOT, CHME), read(ROOT, ERMAK))
    # Also check that neither family has an unsafe runtime index.
    for base in ("content-packs/diesel/chme3-family", "content-packs/electric/ermak"):
        assert not (ROOT / base / "runtime-index.json").exists(), base
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
