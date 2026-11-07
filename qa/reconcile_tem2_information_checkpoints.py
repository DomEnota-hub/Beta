#!/usr/bin/env python3
"""Relate the historical TEM2 Stage-2/4 information claims to pinned objects."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
INPUT = ROOT / "content-packs/locomotive-migration/migration/source-assets/family-replay"
STAGE2 = "docs/integration/TEM2_STAGE2_ATLAS_CHECKPOINT.md"
STAGE4 = "docs/integration/TEM2_STAGE4_FINAL_CHECKPOINT.md"
OUT = ROOT / "docs/data-migration/tem2-information-checkpoint-relations.json"
BLOBS = {"tem2_stage2_model.json": "7f5c20331f8e8f905d6a8d944d4decac672d620e",
         "tem2_stage4_acceptance.json": "2e3454b9e75141ff211918acab527ff228e56363"}


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def project():
    history = json.loads(ARCHIVE.read_text())
    documents = {d["sourcePath"]: d for d in history["documents"]}
    snapshots = {}
    for name, sha in BLOBS.items():
        raw = (INPUT / name).read_bytes()
        assert blob_sha(raw) == sha
        snapshots[name] = json.loads(raw)
    s2, s4 = snapshots.values()
    a2 = json.loads((ROOT / "content-packs/diesel/tem2-family/atlas/stage2-source-lineage.json").read_text())
    a4 = json.loads((ROOT / "content-packs/diesel/tem2-family/acceptance/routes-stage4.json").read_text())
    items = json.loads((ROOT / "content-packs/diesel/tem2-family/acceptance/items-stage4.pack.json").read_text())["entries"]

    assert a2["sourceBlobSha"] == BLOBS["tem2_stage2_model.json"]
    for kind in ("systems", "equipment", "schemes", "flows"):
        assert [r["sourceObject"] for r in a2["sourceObjects"][kind]] == s2[kind]
    assert a4["donorGitBlob"] == BLOBS["tem2_stage4_acceptance.json"]
    assert [r["sourceObject"] for r in a4["routes"]] == s4["routes"]
    assert a4["rootMetadata"] == {k: v for k, v in s4.items() if k not in ("routes", "coreChecks", "profileChecks")}
    originals = s4["coreChecks"] + s4["profileChecks"]
    assert [r["sourceObject"]["object"] for r in items] == originals
    assert all(r["sourceObject"]["sourceBlobSha"] == BLOBS["tem2_stage4_acceptance.json"]
               and r["publicationStatus"] == "CANDIDATE"
               and r["actionDisposition"] == "INFORMATION_ONLY" for r in items)

    applicable = {p: sum(p in e[3] for e in s2["equipment"]) for p in s2["profiles"]}
    assert (len(s2["systems"]), len(s2["equipment"]), len(s2["schemes"]),
            len(s2["flows"]), sum(len(f[4]) for f in s2["flows"])) == (9, 36, 9, 11, 42)
    assert applicable == {"tem2-base": 33, "tem2u-improved": 35}
    assert s2["interactiveProjection"]["coordinatePolicy"] == "DISPLAY_ONLY_NOT_PHYSICAL_LOCATION"
    assert s2["classification"] == "SOURCE_BACKED_FUNCTIONAL"
    assert s4["expandedAcceptance"]["expectedEquipmentCountByProfile"] == applicable
    assert len(s4["coreChecks"]) == 14 and len(s4["profileChecks"]) == 2
    assert s4["sessionContract"]["routeSwitchKeepsSession"] is True
    assert len(s4["routes"]) == 2
    assert [r["phases"] for r in s4["routes"]] == [
        ["OUTSIDE", "ENGINE_ROOM", "CAB", "BRAKE_PNEUMATIC"],
        ["CAB", "BRAKE_PNEUMATIC", "ENGINE_ROOM", "OUTSIDE"]]

    expected = {
        STAGE2: ("**36**", "**9**", "**11**", "**42**", "**17**", "**91**", "33/33", "35/35", "DISPLAY_ONLY_NOT_PHYSICAL_LOCATION"),
        STAGE4: ("**14 общих проверок**", "**2 профильные проверки ТЭМ2У**", "33/33", "35/35", "FAIL_CLOSED", "не являются сами по себе текущим разрешением", "Это **не** означает"),
    }
    rows = []
    for path, phrases in expected.items():
        source = documents[path]
        text = source["exactSourceText"]
        assert all(phrase in text for phrase in phrases), path
        assert blob_sha(text.encode()) == source["sourceBlobSha"]
        rows.append({"sourcePath": path, "sourceBlobSha": source["sourceBlobSha"],
                     "sourceTextSha256": hashlib.sha256(text.encode()).hexdigest(),
                     "relation": "HISTORICAL_CLAIMS_TO_EXACT_SOURCE_OBJECTS",
                     "currentAuthorityVerified": False})
    assert s4["expandedAcceptance"]["policy"].find("without claiming") >= 0
    return {"schemaVersion": 1, "donorCommit": history["donorCommit"],
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "actionAuthorityGranted": False,
            "note": "Stage-2/4 counts, routes and source objects match preserved candidates. The 17 views and 91 hotspots are historical claims also covered by the separate exact generator-output replay; they are not rederived here. Neither historical checkpoint verifies current obligations, execution-specific applicability, runtime integration or action permission. Diagnostic Stage-3 claims await the diagnostic phase.",
            "checkpoints": rows, "stage2SourceBlob": BLOBS["tem2_stage2_model.json"],
            "stage4SourceBlob": BLOBS["tem2_stage4_acceptance.json"],
            "sourceObjectCounts": {"systems": 9, "equipment": 36, "schemes": 9,
                                   "flows": 11, "flowNodes": 42, "coreChecks": 14,
                                   "profileChecks": 2, "routes": 2},
            "applicableEquipmentByProfile": applicable,
            "stage2Destination": "content-packs/diesel/tem2-family/atlas/stage2-source-lineage.json",
            "stage4Destinations": ["content-packs/diesel/tem2-family/acceptance/routes-stage4.json",
                                   "content-packs/diesel/tem2-family/acceptance/items-stage4.pack.json"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.write_text(encoded)
    print("TEM2_INFORMATION_CHECKPOINTS_PASS 2 9 36 9 11 42 14 2")
