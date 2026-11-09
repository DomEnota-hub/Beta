#!/usr/bin/env python3
"""Pinned shared source parity, separated from publication and authority.

Checks the six known source-to-candidate projections by replaying their existing
deterministic generators in --check mode. Two presentation contracts and the
opaque exam payload are explicitly left unverified at the semantic level.
"""
import argparse
import gzip
import json
import subprocess
import sys
from pathlib import Path

from validate_vl80s_source_parity import git_blob

ROOT = Path(__file__).resolve().parents[1]
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
PROJECTED = {
    "diagnostic_framework_v2.json": "qa/migrate_diagnostic_reference_sources.py",
    "extended_emergency_policy.json": "qa/migrate_diagnostic_reference_sources.py",
    "extended_emergency_runtime.json": "qa/migrate_extended_emergency_source.py",
    "scheme_layout_metadata.json": "qa/migrate_shared_scheme_pairs.py",
    "stepwise_scheme_flows.json": "qa/migrate_shared_scheme_pairs.py",
    "source_presentations.json": "qa/migrate_source_presentations.py",
}
GENERATORS = tuple(sorted(set(PROJECTED.values())))


def validate(root, donor):
    crosswalk = json.loads((root / "docs/migration/donor-asset-crosswalk.json").read_text())
    assert crosswalk["donor"] == {"repository": "DomEnota-hub/Test-", "commit": PIN}
    shared = [a for a in crosswalk["assets"] if a["family"] == "shared"]
    ermak_exact = [a for a in crosswalk["assets"] if a["family"] == "ermak" and a["exactRawCopies"]]
    assert len(shared) == 9 and len(ermak_exact) == 2
    names = {Path(a["sourcePath"]).name for a in shared}
    assert set(PROJECTED) <= names
    assert names - set(PROJECTED) == {"exam_questions.json", "scheme_semantic_palette.json", "scheme_view_contract.json"}
    verified = 0
    for a in shared + ermak_exact:
        path = donor / a["sourcePath"]
        raw = path.read_bytes()
        assert len(raw) == a["compressedBytes"], a["sourcePath"]
        assert git_blob(raw) == a["gitBlobSha"], a["sourcePath"]
        if a["format"] == "json.gz":
            json.loads(gzip.decompress(raw).decode("utf-8-sig"))
        elif path.name != "exam_questions.json":
            json.loads(raw.decode("utf-8-sig"))
        for copy in a["exactRawCopies"]:
            assert (root / copy).read_bytes() == raw, copy
        verified += 1
    for script in GENERATORS:
        subprocess.run([sys.executable, script, str(donor), "--check"],
                       cwd=root, check=True)
    # No source-derived action permissions are created or modified.
    return {"pinnedBlobs": verified, "sharedAssets": 9,
            "sourceToCandidateProjections": len(PROJECTED),
            "generatorChecks": len(GENERATORS),
            "exactErmakRawAssets": len(ermak_exact),
            "semanticallyUnverifiedShared": 3}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--donor-dir", type=Path, required=True)
    a = p.parse_args()
    print("SHARED_PINNED_SOURCE_PARITY_PASS", validate(a.root, a.donor_dir))
