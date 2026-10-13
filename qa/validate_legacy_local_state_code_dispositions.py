#!/usr/bin/env python3
"""Check source-file pins and keep legacy local-state stores out of history runtime."""
import argparse
import json
from pathlib import Path

DEST = Path("docs/data-migration/legacy-local-state-code-dispositions.json")
LEDGER = Path("docs/data-migration/source-discovery-ledger.json")
HISTORY = Path("feature-history/src/main/kotlin/ru/railbrake/calculator/history/HistoryContracts.kt")
PINS = {
    "app/src/main/java/ru/railbrake/calculator/data/AcceptanceStateRepository.kt": ("60cfce418d591e02701ea3138d3afabff9c36904", "technical_acceptance_states", "ACCEPTANCE_LOCAL_STATE_AND_REPORT_FORMAT"),
    "app/src/main/java/ru/railbrake/calculator/data/DiagnosticSessionRepository.kt": ("cc63f7a7abf17b4498ba3644b095be1127ef4df2", "diagnostic_sessions", "DIAGNOSTIC_SESSION_LOCAL_JOURNAL"),
    "app/src/main/java/ru/railbrake/calculator/data/KnowledgeDisplayRepository.kt": ("3ce3550ae696a05041514d2e099057b2ebb32604", "knowledge_display_v2", "KNOWLEDGE_PRESENTATION_PREFERENCES"),
    "app/src/main/java/ru/railbrake/calculator/data/TechnicalRecentRepository.kt": ("7c896f5ce0d0c0c50c0dd0ed7eba070fea9f4fff", "technical_recent_materials", "RECENT_TECHNICAL_ENTRY_IDS"),
}


def validate(root: Path, ledger_path: Path) -> int:
    data = json.loads((root / DEST).read_text(encoding="utf-8"))
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert data["schemaVersion"] == 1
    assert data["donorCommit"] == ledger["sourceCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert data["publicationStatus"] == "NOT_PROMOTED" and data["runtimeImport"] is False
    rows = data["rows"]
    by_path = {r["sourcePath"]: r for r in rows}
    assert len(rows) == len(by_path) == len(PINS) and set(by_path) == set(PINS)
    for path, (sha, prefs, role) in PINS.items():
        source = [r for r in ledger["rows"] if r["sourcePath"] == path and r["sourceObjectId"] == "source-file"]
        assert len(source) == 1 and source[0]["sourceArtifactGitBlob"] == sha
        row = by_path[path]
        assert row["sourceBlobSha"] == sha and row["disposition"] == "DEFERRED_SCOPE"
        assert row["preferencesFile"] == prefs and row["codeRole"] == role
        assert row["storedFields"] and row["storageMigrationImplemented"] is False
    assert "BLOCKING decodes as NOTE" in by_path[next(p for p in PINS if p.endswith("AcceptanceStateRepository.kt"))]["observedLegacyBehavior"]
    diag = by_path[next(p for p in PINS if p.endswith("DiagnosticSessionRepository.kt"))]
    assert "timestamp collisions" in diag["migrationBoundary"]
    assert "separate from calculation HistoryRecord" in diag["migrationBoundary"]
    assert "do not authorize" in by_path[next(p for p in PINS if p.endswith("KnowledgeDisplayRepository.kt"))]["migrationBoundary"]
    assert "not a calculation record" in by_path[next(p for p in PINS if p.endswith("TechnicalRecentRepository.kt"))]["observedLegacyBehavior"]
    h = data["calculationHistoryStorage"]
    assert h["destinationContract"] == str(HISTORY)
    assert h["migrationGate"] == "legacyFormatVerified=false"
    assert h["status"] == "FORMAT_OBSERVED_MIGRATION_PENDING"
    assert h["zipOnlySourcePath"] == "RailBrakeCalculator.zip!RailBrakeCalculator/app/src/main/java/ru/railbrake/calculator/data/HistoryRepository.kt"
    assert h["memberBlobSha"] == "d95a2ce465e2f09bb96d74b8318f36b16d21afd0"
    assert h["memberManifest"] == "docs/data-migration/legacy-zip-member-manifest.json"
    assert h["storageMigrationImplemented"] is False
    contract = (root / HISTORY).read_text(encoding="utf-8")
    assert "const val legacyFormatVerified: Boolean = false" in contract
    assert data["remainingScope"] == "OTHER_KOTLIN_AND_ZIP_OBJECTS_PENDING_REVIEW"
    return len(rows)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--ledger", type=Path, default=LEDGER)
    a = p.parse_args()
    print("LEGACY_LOCAL_STATE_CODE_PASS", validate(a.root, a.ledger))
