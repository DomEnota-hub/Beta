#!/usr/bin/env python3
"""Pinned Kotlin-source parity accounting, not executable feature parity.

Fail closed when the donor snapshot changes, an audited Kotlin source is
omitted, or a target touchpoint disappears. This never promotes a candidate.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/migration/donor-kotlin-crosswalk.json"
DONOR_SHA = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
SOURCE_PREFIX = "app/src/main/java/"
STATUSES = {"NOT_MIGRATED", "CONTRACT_ONLY", "PARTIAL"}
HEX40 = re.compile(r"^[a-f0-9]{40}$")


def safe_path(value: str) -> Path:
    p = Path(value)
    if not value or p.is_absolute() or ".." in p.parts or "\\" in value:
        raise AssertionError(f"unsafe repository path: {value!r}")
    return p


def validate(root: Path, manifest: dict, donor_tree: dict) -> dict:
    assert manifest["schemaVersion"] == 1
    assert manifest["donor"]["repository"] == "DomEnota-hub/Test-"
    assert manifest["donor"]["commit"] == DONOR_SHA
    assert manifest["donor"]["sourceRoot"] == SOURCE_PREFIX
    assert manifest["target"]["repository"] == "DomEnota-hub/Beta"
    assert manifest["scope"] == "PINNED_DONOR_MAIN_KOTLIN_ONLY_EXCLUDES_PATCH_AND_TESTS"
    assert donor_tree.get("truncated") is False, "Git tree incomplete"
    pinned = {
        e["path"]: e["sha"]
        for e in donor_tree["tree"]
        if e.get("type") == "blob"
        and e["path"].startswith(SOURCE_PREFIX)
        and e["path"].endswith(".kt")
    }
    assert len(pinned) == 74, f"pinned donor Kotlin count changed: {len(pinned)}"
    rows = manifest["sources"]
    assert len(rows) == 74, f"crosswalk Kotlin count changed: {len(rows)}"
    seen = set()
    counts = {s: 0 for s in sorted(STATUSES)}
    target_count = 0
    for row in rows:
        source = row["sourcePath"]
        safe_path(source)
        assert source.startswith(SOURCE_PREFIX) and source.endswith(".kt"), source
        assert source not in seen, f"duplicate donor Kotlin path: {source}"
        seen.add(source)
        sha = row["donorBlobSha"]
        assert HEX40.fullmatch(sha), source
        assert pinned.get(source) == sha, f"donor SHA or source missing: {source}"
        assert re.fullmatch(r"[a-z][a-z0-9-]+", row["featureArea"]), source
        status = row["status"]
        assert status in STATUSES, f"unproven promotion of {source}: {status}"
        assert row["userJourneyVerified"] is False, f"unproven full journey: {source}"
        targets = row["targetPaths"]
        assert isinstance(targets, list) and len(targets) == len(set(targets)), source
        assert bool(targets) == (status != "NOT_MIGRATED"), source
        for target in targets:
            path = safe_path(target)
            assert "/src/main/" in target and target.endswith(".kt"), target
            assert not target.startswith(("patch/", "content-packs/", "app/src/")), target
            assert (root / path).is_file(), f"target touchpoint missing: {target}"
            target_count += 1
        counts[status] += 1
    assert seen == set(pinned), f"missing donor paths: {sorted(set(pinned) - seen)}"
    assert counts["NOT_MIGRATED"] > 0 and counts["PARTIAL"] > 0
    return {"donorKotlinSources": len(seen), "targetTouchpoints": target_count, "statusCounts": counts}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor-tree", required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    donor_tree = json.loads(args.donor_tree.read_text(encoding="utf-8"))
    print(json.dumps(validate(ROOT, manifest, donor_tree), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
