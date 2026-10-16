#!/usr/bin/env python3
"""Rebuild pinned CHME3/TEM2 Android assets from preserved source objects."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content-packs/locomotive-migration/migration/source-assets"
INPUT = BASE / "family-replay"
MANIFEST = ROOT / "docs/data-migration/family-generator-replay.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
SCRIPTS = {"build_chme3_android_assets.py": "4392f7285a1f3c4e910710508919f97c6e96cd30",
           "build_tem2_android_assets.py": "f8a8fcbacc9d4acabd921dd86e9f5cb1d1950fe8"}
EXTRA_INPUTS = {
    "tem2_stage2_model.json": ("docs/locomotives/diesel/tem2-family/common/stage2_model.json", "7f5c20331f8e8f905d6a8d944d4decac672d620e"),
    "tem2_stage3_model.json": ("docs/locomotives/diesel/tem2-family/common/stage3_model.json", "4234e401eb9d6ec03802669d0f74962cb23ea5c4"),
    "tem2_stage4_acceptance.json": ("docs/locomotives/diesel/tem2-family/common/stage4_acceptance.json", "2e3454b9e75141ff211918acab527ff228e56363"),
    "tem2_source_registry.json": ("docs/locomotives/diesel/tem2-family/common/source_registry.json", "160a2531a67bdb1c6fff1fb532fc3df6044d67a6"),
    "source_presentations.json": ("app/src/main/assets/technical/source_presentations.json", "6dde42099f5c6e9f1226212ae5e42c6a04fde00c"),
}


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def check():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["donorCommit"] == DONOR and manifest["runtimeImport"] is False
    golden = {row["path"]: row["donorBlobSha"] for row in manifest["outputs"]}
    assert len(golden) == len(manifest["outputs"]) == 26
    assert len(set(golden.values())) == 13
    for path, sha in list(golden.items()):
        if path.startswith("app/"):
            assert golden[path.replace("app/", "patch/app/", 1)] == sha
    indexes = sorted((ROOT / "content-packs/diesel").glob("*/migration/*-source-index.json"))
    documents = {}
    for path in indexes:
        data = json.loads(path.read_text())
        assert data["donorCommit"] == DONOR
        for doc in data.get("documents", []):
            source = doc["sourcePath"]
            assert source.startswith("docs/locomotives/") and source not in documents
            documents[source] = doc["sourceObject"]
    assert len(documents) == 59
    with tempfile.TemporaryDirectory(prefix="family-generator-replay-") as folder:
        work = Path(folder)
        for source, obj in documents.items():
            dest = work / source
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(obj, ensure_ascii=False))
        for filename, (source, sha) in EXTRA_INPUTS.items():
            data = (INPUT / filename).read_bytes()
            assert blob_sha(data) == sha
            target = work / source
            assert not target.exists(), source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        source_presentation = work / EXTRA_INPUTS["source_presentations.json"][0]
        mirror = work / "patch/app/src/main/assets/technical/source_presentations.json"
        mirror.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_presentation, mirror)
        for filename, sha in SCRIPTS.items():
            data = (BASE / filename).read_bytes()
            assert blob_sha(data) == sha
            target = work / "tools" / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            subprocess.run([sys.executable, str(target)], cwd=work, check=True,
                           capture_output=True, text=True)
        output = {}
        for tree in ("app", "patch/app"):
            base = work / tree / "src/main/assets/technical"
            for path in base.glob("*"):
                output[path.relative_to(work).as_posix()] = blob_sha(path.read_bytes())
        assert output == golden, (set(output) ^ set(golden),
                                  [(p, output[p], golden[p]) for p in output.keys() & golden.keys()
                                   if output[p] != golden[p]])
    print("FAMILY_GENERATOR_REPLAY_PASS 59 5 26 13")


if __name__ == "__main__":
    check()
