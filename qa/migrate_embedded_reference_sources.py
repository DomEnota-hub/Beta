#!/usr/bin/env python3
"""Preserve three Kotlin-embedded reference groups with exact injector provenance."""

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content-packs/common/knowledge/migration"
OUTPUT = BASE / "embedded-reference-sources.candidate.json"
FILES = {
    "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt": "TechnicalDataRepository.kt",
    ".github/scripts/add_brake_jam_reference.py": "add_brake_jam_reference.py",
    ".github/scripts/add_wheel_flat_reference.py": "add_wheel_flat_reference.py",
    ".github/scripts/add_safety_reference_section.py": "add_safety_reference_section.py",
}
GROUPS = (("loadBrakeJamReference", "add_brake_jam_reference.py", 1),
          ("loadWheelFlatReference", "add_wheel_flat_reference.py", 1),
          ("loadSafety", "add_safety_reference_section.py", 7))


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def project():
    discovery = json.loads((ROOT / "docs/data-migration/source-discovery-ledger.json").read_text())
    rows = {r["sourcePath"]: r for r in discovery["rows"]}
    assets = {}
    for source, name in FILES.items():
        raw = (BASE / "source-assets" / name).read_bytes()
        assert git_blob(raw) == rows[source]["sourceArtifactGitBlob"]
        assert len(raw) == rows[source]["sourceBytes"]
        assets[name] = raw.decode("utf-8")
    kotlin = assets["TechnicalDataRepository.kt"]
    groups = []
    for function, script, count in GROUPS:
        start = kotlin.index("    private fun " + function + "(")
        end = kotlin.index("\n    private fun ", start + 5)
        fragment = kotlin[start:end].strip()
        node = ast.parse(assets[script])
        script_literals = [assign.value.value for assign in node.body
                           if isinstance(assign, ast.Assign) and isinstance(assign.value, ast.Constant)
                           and isinstance(assign.value.value, str)]
        assert any(fragment in literal for literal in script_literals), function
        if function == "loadSafety":
            cards = [{"suffix": suffix, "title": title} for suffix, title in
                     re.findall(r'suffix = "([^"]+)"\s*,\s*title = "([^"]+)"', fragment)]
        else:
            cards = [{"idExpression": re.search(r'val id = (.*)', fragment).group(1),
                      "title": re.search(r'title = "([^"]+)"', fragment).group(1)}]
        assert len(cards) == count
        groups.append({"function": function, "injectorSourcePath": next(p for p, n in FILES.items() if n == script),
                       "entryTemplates": cards, "sourceFragmentSha256": hashlib.sha256(fragment.encode()).hexdigest(),
                       "sourceFragment": fragment})
    return {"schemaVersion": 1, "donorCommit": discovery["sourceCommit"],
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "actionDisposition": "INFORMATION_ONLY",
            "sourceWarning": "Historical procedural and safety text only. Current rules, applicability and action permission have not been established; source labels remain original donor claims.",
            "sourceFiles": [{"sourcePath": p, "sourceBlobSha": rows[p]["sourceArtifactGitBlob"],
                             "archivePath": "content-packs/common/knowledge/migration/source-assets/" + n}
                            for p, n in FILES.items()],
            "groups": groups}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text() == encoded
    else:
        OUTPUT.write_text(encoded)
    print("EMBEDDED_REFERENCE_SOURCE_PASS 3 9")


if __name__ == "__main__":
    main()
