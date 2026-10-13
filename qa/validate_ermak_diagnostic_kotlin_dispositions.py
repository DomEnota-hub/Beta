#!/usr/bin/env python3
"""Check pinned diagnostic Kotlin wrappers are classified as code, not content."""
import argparse
import json
from pathlib import Path

DEST = Path("docs/data-migration/diagnostic-kotlin-wrapper-dispositions.json")
LEDGER = Path("docs/data-migration/source-discovery-ledger.json")
PINS = {
    "app/src/main/java/ru/railbrake/calculator/core/Chme3DiagnosticRepository.kt": "5775a53cc7b3a2d66bd40f15568199e3ee80ea6e",
    "app/src/main/java/ru/railbrake/calculator/core/ErmakDiagnosticRepository.kt": "01fcf7c267d879fdd5f6da7ab751a48db7cf3051",
    "app/src/main/java/ru/railbrake/calculator/core/Tem2DiagnosticRepository.kt": "d61d6f13fedc6ca7a5f37327ff92f28c593e7908",
}


def validate(root: Path, ledger_path: Path) -> int:
    data = json.loads((root / DEST).read_text(encoding="utf-8"))
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert data["donorCommit"] == ledger["sourceCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert data["runtimeImport"] is False
    assert data["publicationStatus"] == "NOT_PROMOTED"
    rows = data["rows"]
    assert len(rows) == len(PINS) and {r["sourcePath"] for r in rows} == set(PINS)
    for row in rows:
        path = row["sourcePath"]
        source = [r for r in ledger["rows"] if r["sourcePath"] == path]
        assert len(source) == 1, path
        assert source[0]["sourceArtifactGitBlob"] == row["sourceBlobSha"] == PINS[path]
        assert source[0]["disposition"] == "PENDING_EXTRACTION"
        assert row["disposition"] == "DEFERRED_SCOPE"
        assert row["embeddedScenarioObjectCount"] == 0
        assert row["canonicalScenarioIds"] == []
        assert row["actionAuthority"] == "NONE_FROM_CODE_COMMENT_OR_PARSER"
        assert row["runtimeBehaviorDeferred"] is True
    return len(rows)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--ledger", type=Path, default=LEDGER)
    a = p.parse_args()
    print("DIAGNOSTIC_KOTLIN_WRAPPERS_PASS", validate(a.root, a.ledger))
