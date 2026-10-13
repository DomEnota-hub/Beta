#!/usr/bin/env python3
"""Verify pinned Ermak generator code dispositions and candidate-only outputs."""
import argparse
import gzip
import json
from pathlib import Path

DEST = Path("docs/data-migration/ermak-generator-dispositions.json")
LEDGER = Path("docs/data-migration/source-discovery-ledger.json")
PACK = Path("content-packs/electric/ermak/diagnostics/recommended")
LINKS = Path("content-packs/electric/ermak/migration/source-assets/ermak_links.json.gz")
PINS = {
    "tools/integrate_beta51_ermak_diagnostics.jq": "b0c9692487675826622b864e4139b9526724f29d",
    "tools/deepen_ermak_p0_batch2.py": "806d39755c0e8cc6131a21e140a0521b601f2e90",
    ".github/scripts/wire_ermak_stage7_links.py": "adb1f345e38552e59abab54fe22781eb5323f19a",
}
ROUTES = ["ER-DIAG-040", "ER-DIAG-051", "ER-DIAG-052", "ER-DIAG-053",
          "ER-DIAG-054", "ER-DIAG-055", "ER-DIAG-056", "ER-DIAG-136"]
RELATED = ["ER-DIAG-015", "ER-DIAG-016", "ER-DIAG-017", "ER-DIAG-041",
           "ER-DIAG-045", "ER-DIAG-046", "ER-DIAG-047", "ER-DIAG-050",
           "ER-DIAG-052", "ER-DIAG-055"]


def validate(root: Path, ledger_path: Path, data=None) -> int:
    data = data if data is not None else json.loads((root / DEST).read_text(encoding="utf-8"))
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert data["schemaVersion"] == 1
    assert data["donorCommit"] == ledger["sourceCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert data["publicationStatus"] == "NOT_PROMOTED" and data["runtimeImport"] is False
    rows = data["rows"]
    by_path = {r["sourcePath"]: r for r in rows}
    assert len(rows) == len(by_path) == len(PINS) and set(by_path) == set(PINS)
    for path, sha in PINS.items():
        source = [r for r in ledger["rows"] if r["sourcePath"] == path and r["sourceObjectId"] == "source-file"]
        assert len(source) == 1 and source[0]["sourceArtifactGitBlob"] == sha
        row = by_path[path]
        assert row["sourceBlobSha"] == sha and row["disposition"] == "DEFERRED_SCOPE"
        assert row["authority"] == "SOURCE_CODE_IS_NOT_PRIMARY_TECHNICAL_APPROVAL"
        assert row["runtimeBehaviorDeferred"] is True
    clone = by_path["tools/integrate_beta51_ermak_diagnostics.jq"]
    deepen = by_path["tools/deepen_ermak_p0_batch2.py"]
    wire = by_path[".github/scripts/wire_ermak_stage7_links.py"]
    assert clone["codeRole"] == "CREATE_DIAGNOSTIC_CANDIDATE"
    assert clone["inputScenarioId"] == "ER-DIAG-050"
    assert clone["derivedScenarioIds"] == ["ER-DIAG-136"]
    assert clone["relatedScenarioIdsInGenerator"] == RELATED
    assert deepen["codeRole"] == "DEEPEN_EXISTING_DIAGNOSTIC_CANDIDATES"
    assert deepen["routeScenarioIds"] == ROUTES
    assert wire["codeRole"] == "PATCH_LEGACY_UI_CONSUMER"
    assert wire["inputAsset"] == "app/src/main/assets/technical/ermak_links.json.gz"
    assert wire["targetSourcePath"] == "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt"
    files = sorted((root / PACK).glob("diagnostics-*.pack.json"))
    assert files
    entries = [e for p in files for e in json.loads(p.read_text(encoding="utf-8"))["entries"]]
    by_id = {e["id"]: e for e in entries}
    assert len(entries) == len(by_id) == 136
    assert set(ROUTES + RELATED + [clone["inputScenarioId"]]) <= set(by_id)
    assert all(by_id[sid]["publicationStatus"] == "CANDIDATE" and
               by_id[sid]["actionDisposition"] == "INFORMATION_ONLY" for sid in set(ROUTES + RELATED))
    links = json.loads(gzip.decompress((root / LINKS).read_bytes()))
    assert data["unresolvedStage7ScenarioId"] == "ER-DIAG-136"
    assert data["stage7AutoLink"] is False
    assert "ER-DIAG-136" not in links["indexes"]["byDiagnostic"]
    assert data["remainingGeneratorScope"] == "OTHER_DONOR_GENERATORS_PENDING_OBJECT_REVIEW"
    return len(rows)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--ledger", type=Path, default=LEDGER)
    a = p.parse_args()
    print("ERMAK_GENERATOR_DISPOSITIONS_PASS", validate(a.root, a.ledger))
