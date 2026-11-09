#!/usr/bin/env python3
"""Fail-closed integrity audit of the pinned donor-asset crosswalk.

This validates raw-copy preservation and published runtime index boundaries,
NOT semantic donor-to-Beta object parity. It never promotes candidates.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "docs/migration/donor-asset-crosswalk.json"
DONOR_SHA = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
SHA_RE = re.compile(r"^[a-f0-9]{40}$")


def blob_sha(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def safe_relative(path: str) -> Path:
    p = Path(path)
    if p.is_absolute() or not p.parts or ".." in p.parts or "\\" in path:
        raise AssertionError(f"unsafe path: {path}")
    return p


def validate_raw_copy(root: Path, path: str, expected_sha: str, expected_size: int) -> None:
    rel = safe_relative(path)
    assert rel.parts[0] == "content-packs", path
    file = root / rel
    assert file.is_file(), f"missing exact raw copy: {path}"
    payload = file.read_bytes()
    assert len(payload) == expected_size, f"size mismatch: {path}"
    assert blob_sha(payload) == expected_sha, f"SHA mismatch: {path}"


def validate_runtime_index(root: Path, model_root: str, model_id: str) -> int:
    base = safe_relative(model_root)
    index_path = root / base / "runtime-index.json"
    if not index_path.is_file():
        return 0  # Absence of runtime-index is NOT proof that model data is absent.
    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert index["modelId"] == model_id, (index_path, index.get("modelId"))
    packs = index["packs"]
    assert isinstance(packs, list) and packs, index_path
    assert len(packs) == len(set(packs)), f"duplicate runtime paths: {index_path}"
    relative_root = base.relative_to("content-packs")
    for name in packs:
        rel = safe_relative(name)
        assert rel.parts[:len(relative_root.parts)] == relative_root.parts, (model_id, name)
        assert name.endswith(".pack.json"), name
        assert not any(part in {"research", "candidate", "migration", "source-assets"} for part in rel.parts), name
        assert (root / "content-packs" / rel).is_file(), f"runtime pack missing: {name}"
    return len(packs)


def validate(root: Path, manifest: dict) -> tuple[int, int, int]:
    assert manifest["schemaVersion"] == 1
    assert manifest["donor"] == {"repository": "DomEnota-hub/Test-", "commit": DONOR_SHA}
    assets = manifest["assets"]
    assert len(assets) == 36, f"expected 36 donor assets, got {len(assets)}"
    seen = set()
    raw_copies = 0
    for row in assets:
        path = row["sourcePath"]
        rel = safe_relative(path)
        assert rel.parts[:4] == ("app", "src", "main", "assets"), path
        assert path not in seen, f"duplicate donor asset: {path}"
        seen.add(path)
        sha = row["gitBlobSha"]
        assert SHA_RE.fullmatch(sha), path
        size = row["compressedBytes"]
        assert isinstance(size, int) and size > 0, path
        assert row["format"] == ("json.gz" if path.endswith(".json.gz") else "json"), path
        assert row["recordParity"] in {"UNVERIFIED", "SOURCE_ARRAY_EQUIVALENT_CANDIDATE"}, path
        if row["recordParity"] == "SOURCE_ARRAY_EQUIVALENT_CANDIDATE":
            assert row["family"] in {"tem2", "chme3", "ermak"}, path
            assert row.get("evidenceWorkflow", "").startswith(
                "https://github.com/DomEnota-hub/Beta/actions/runs/"
            ), f"missing source-object parity CI evidence: {path}"
        assert row["runtimePublication"] == "NOT_PROVEN", "do not infer runtime publication"
        for copy in row["exactRawCopies"]:
            validate_raw_copy(root, copy, sha, size)
            raw_copies += 1
    assert raw_copies == 5, f"expected five exact raw copies, got {raw_copies}"
    catalog = json.loads((root / "content-packs/catalog.json").read_text(encoding="utf-8"))
    assert len(catalog["models"]) == 4
    runtime_packs = 0
    for model in catalog["models"]:
        model_root = model["root"]
        assert (root / safe_relative(model_root)).is_dir(), model_root
        runtime_packs += validate_runtime_index(root, model_root, model["modelId"])
    assert runtime_packs > 0, "no published runtime pack index verified"
    return len(assets), raw_copies, runtime_packs


if __name__ == "__main__":
    result = validate(ROOT, json.loads(CROSSWALK.read_text(encoding="utf-8")))
    print("DONOR_ASSET_CROSSWALK_PASS assets=%d exact_copies=%d indexed_runtime_packs=%d" % result)
