#!/usr/bin/env python3
"""Compare archived Package B counts and scope with preserved sequence objects."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
CHECKPOINT = "docs/integration/PACKAGE_B_STEPWISE_FLOWS_CHECKPOINT.md"
PACKS = (
    ROOT / "content-packs/diesel/chme3-family/atlas/shared-scheme-pairs.candidate.pack.json",
    ROOT / "content-packs/electric/ermak/atlas/shared-scheme-pairs.candidate.pack.json",
)
OUT = ROOT / "docs/data-migration/package-b-checkpoint-relations.json"


def project():
    archive = json.loads(HISTORY.read_text())
    source, = (d for d in archive["documents"] if d["sourcePath"] == CHECKPOINT)
    text = source["exactSourceText"]
    for phrase in ("Всего последовательностей: **55**", "Всего шагов: **145**",
                   "CHME3: 7, CHME3E: 14, CHME3T: 8, ERMAK: 26",
                   "ELECTRICAL: 32, PNEUMATIC: 23", "SOURCE_BACKED_FUNCTIONAL",
                   "не выдаются за монтажную трассировку", "без процедуры подключения внешней сети"):
        assert phrase in text
    entries = []
    for path in PACKS:
        pack = json.loads(path.read_text())
        entries.extend((path, e) for e in pack["entries"])
    sequences = [(path, e) for path, e in entries if "steps" in e["sourceObject"]["object"]]
    layouts = [(path, e) for path, e in entries if "sequenceId" in e["sourceObject"]["object"]]
    assert len(entries) == 110 and len(sequences) == len(layouts) == 55
    assert len({e["sourceObject"]["object"]["id"] for _, e in sequences}) == 55
    assert sum(len(e["sourceObject"]["object"]["steps"]) for _, e in sequences) == 145
    by_family = Counter(e["sourceObject"]["object"]["family"] for _, e in sequences)
    by_domain = Counter(e["sourceObject"]["object"]["domain"] for _, e in sequences)
    by_representation = Counter(e["sourceObject"]["object"]["representation"] for _, e in sequences)
    assert dict(by_family) == {"CHME3": 7, "CHME3T": 8, "CHME3E": 14, "ERMAK": 26}
    assert dict(by_domain) == {"ELECTRICAL": 32, "PNEUMATIC": 23}
    assert dict(by_representation) == {"SOURCE_BACKED_FUNCTIONAL": 55}
    assert all(e["publicationStatus"] == "CANDIDATE" and e["actionDisposition"] == "INFORMATION_ONLY"
               for _, e in entries)
    return {"schemaVersion": 1, "donorCommit": archive["donorCommit"],
            "checkpointPath": CHECKPOINT, "checkpointBlobSha": source["sourceBlobSha"],
            "checkpointTextSha256": hashlib.sha256(text.encode()).hexdigest(),
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "actionAuthorityGranted": False,
            "note": "Historical count/representation claims match preserved source objects. Functional pathways do not establish wires, terminals, pipes, execution-specific applicability or permission to connect external power.",
            "sourcePacks": [str(p.relative_to(ROOT)) for p in PACKS],
            "sequenceCount": len(sequences), "stepCount": 145, "layoutCount": len(layouts),
            "familyCounts": dict(sorted(by_family.items())),
            "domainCounts": dict(sorted(by_domain.items())),
            "representationCounts": dict(sorted(by_representation.items()))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = project()
    encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.write_text(encoded)
    print("PACKAGE_B_CHECKPOINT_PASS 55 145")


if __name__ == "__main__":
    main()
