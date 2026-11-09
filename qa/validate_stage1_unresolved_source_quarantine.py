#!/usr/bin/env python3
"""Guard unresolved CHME3/Ermak source links against accidental publication.

This checks explicit quarantine boundaries; it does not resolve sources or
certify any operational instruction.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR_SHA = "3176d6ee228f0ed4b78371f45209e10c1c724eff"


def read(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def validate(root: Path, chme3: dict, ermak: dict, identity: dict) -> dict:
    for data in (chme3, ermak, identity):
        assert data["donorCommit"] == DONOR_SHA, "unpinned source audit"
    unresolved = chme3["unresolvedReferences"]
    keys = [(r["source"], r["variant"], r["sourceTargetId"]) for r in unresolved]
    assert len(unresolved) == 610, "CHME3 unresolved count changed; reconcile evidence before release"
    assert len(keys) == len(set(keys)), "duplicate CHME3 unresolved source link"
    assert all(r["source"] and r["sourceTargetId"] for r in unresolved)
    assert all(r["variant"] in {"chme3", "chme3t", "chme3e"} for r in unresolved)
    counts = {}
    for ref in ermak["sourceReferences"]:
        status = ref["disposition"]
        assert status in {"LINKED", "SOURCE_GAP", "AMBIGUOUS_SOURCE_ID"}, status
        assert ref["occurrences"] > 0
        counts[status] = counts.get(status, 0) + ref["occurrences"]
        if status == "SOURCE_GAP":
            assert ref["registryKeys"] == [], ref["sourceId"]
        if status == "AMBIGUOUS_SOURCE_ID":
            assert len(ref["registryKeys"]) > 1, ref["sourceId"]
    assert counts["SOURCE_GAP"] == 542, counts
    assert counts["AMBIGUOUS_SOURCE_ID"] == 6, counts
    assert identity["publicationStatus"] == "CANDIDATE"
    assert identity["actionDisposition"] == "INFORMATION_ONLY"
    assert identity["runtimeImport"] is False
    for ref in identity["unresolvedSourceIds"]:
        assert ref["disposition"] == "SOURCE_GAP"
        assert ref["automaticMatch"] == "FORBIDDEN"
        assert ref["requiredEvidence"], ref
    gap = identity["diagnosticGap"]
    assert gap["scenarioId"] == "ER-DIAG-136"
    assert gap["autoAddToStage7"] is False
    assert gap["runtimeImport"] is False
    assert gap["disposition"] == "SEPARATE_CANDIDATE_WITHOUT_STAGE7_LINK"
    # A missing runtime-index alone is not sufficient for future APK sign-off,
    # but it is a necessary quarantine boundary in this migration stage.
    for base in ("content-packs/diesel/chme3-family", "content-packs/electric/ermak"):
        assert not (root / base / "runtime-index.json").exists(), f"unsafe runtime promotion: {base}"
    return {"chme3QuarantinedReferences": len(unresolved),
            "ermakSourceGapOccurrences": counts["SOURCE_GAP"],
            "ermakAmbiguousOccurrences": counts["AMBIGUOUS_SOURCE_ID"],
            "ermakMissingIndexId": gap["scenarioId"]}


def main() -> None:
    print(json.dumps(validate(
        ROOT,
        read(ROOT, "content-packs/diesel/chme3-family/migration/source-audit.json"),
        read(ROOT, "content-packs/electric/ermak/migration/source-audit.json"),
        read(ROOT, "content-packs/electric/ermak/migration/source-identity-resolution.json"),
    ), sort_keys=True))


if __name__ == "__main__":
    main()
