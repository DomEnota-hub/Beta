#!/usr/bin/env python3
"""Give every provisional extraction file a bounded review outcome and next gate."""

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/data-migration"
OUTPUT = DIRECTORY / "pending-extraction-review.json"
HISTORICAL = "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
STAGES = "content-packs/locomotive-migration/migration/extended-stage-documents.candidate.json"
EMBEDDED = "content-packs/common/knowledge/migration/embedded-reference-sources.candidate.json"
MASSES = "content-packs/common/calculations/migration/locomotive-reference-source.candidate.json"
ERMAK = "content-packs/electric/ermak/migration/source-audit.json"
ERMAK_DIAG = "content-packs/electric/ermak/diagnostics/recommended/diagnostics-01.pack.json"
VL_DIAG = "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
STATE = "docs/data-migration/legacy-local-state-code-dispositions.json"
WRAPPERS = "docs/data-migration/diagnostic-kotlin-wrapper-dispositions.json"
ZIP = "docs/data-migration/legacy-zip-discovery-overlay.json"


def decide(path, existing):
    if path in existing:
        if path.endswith("/Vl80sNormalValues.kt"):
            return "EXACT_NORMAL_VALUES_AND_CONFIDENCE_SOURCE_PRESERVED", existing[path] + [
                "content-packs/electric/vl80s/technical-data/migration/kotlin-normal-values.candidate.json",
            ], "CURRENT_SOURCE_AUTHORITY_REVIEW"
        return "PREVIOUS_EVIDENCE_LINKED_SEMANTICS_OPEN", existing[path], "FINAL_OBJECT_OR_BEHAVIOR_REVIEW"
    if path.startswith("docs/"):
        evidence = [HISTORICAL]
        if path.startswith("docs/integration/extended_emergency_stage") and path.endswith((".json", ".tsv")):
            evidence.append(STAGES)
        return "EXACT_HISTORICAL_SOURCE_PRESERVED", evidence, "SOURCE_AUTHORITY_AND_OBJECT_JOIN"
    if path in (".github/scripts/add_brake_jam_reference.py",
                ".github/scripts/add_wheel_flat_reference.py",
                ".github/scripts/add_safety_reference_section.py",
                "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt"):
        if path.endswith("TechnicalDataRepository.kt"):
            return "EXACT_EMBEDDED_REFERENCE_AND_ACCEPTANCE_SOURCE_PRESERVED", [
                EMBEDDED,
                "content-packs/electric/ermak/acceptance/migration/kotlin-source.candidate.json",
                "content-packs/electric/vl80s/acceptance/migration/kotlin-required.candidate.json",
            ], "ACCEPTANCE_ROUTE_ORDER_AND_EXECUTION_APPLICABILITY"
        return "EXACT_EMBEDDED_REFERENCE_SOURCE_PRESERVED", [EMBEDDED], "CURRENT_SOURCE_APPLICABILITY_AND_DISPLAY_GATE"
    if path.endswith("/LocomotiveDatabase.kt"):
        return "EXACT_46_REFERENCE_ROWS_PRESERVED", [MASSES], "MASS_SOURCE_AND_VARIANT_REVIEW"
    if path.startswith(".github/scripts/enrich_ermak_"):
        return "TERMINAL_ERMAK_ASSETS_PRESERVED", [ERMAK], "SCRIPT_INTERMEDIATE_VALUES_AND_SOURCE_AUTHORITY"
    if path.startswith(".github/scripts/"):
        if "exam" in path or "hidden_access" in path:
            return "EXAM_ACCESS_BEHAVIOR_DEFERRED", [ZIP], "EXAM_ACCESS_HOSTING_POLICY"
        return "LEGACY_UI_OR_LINK_TRANSFORM_REVIEWED", [ERMAK], "UI_BEHAVIOR_AND_LINK_PARITY"
    if path.startswith("tools/"):
        if path.endswith("generate_exam_questions.py"):
            return "EXAM_GENERATOR_REVIEWED", [ZIP], "EXAM_ACCESS_HOSTING_POLICY"
        if "chme3_android_assets" in path:
            return "FAMILY_GENERATOR_REVIEWED", ["docs/data-migration/chme3-remaining-document-dispositions.json"], "PROJECTION_SEMANTICS"
        if "tem2_android_assets" in path:
            return "FAMILY_GENERATOR_REVIEWED", ["docs/data-migration/tem2-stage3-dispositions.json"], "PROJECTION_SEMANTICS"
        if "vl80s_diagnostics.jq" in path:
            return "TERMINAL_VL80S_DIAGNOSTIC_PRESERVED", [VL_DIAG], "DIAGNOSTIC_SOURCE_AUTHORITY"
        if path.endswith("audit_canonical_data.py"):
            return "VALIDATOR_CODE_REVIEWED", [], "VALIDATION_CONTRACT_PARITY"
        return "TERMINAL_ERMAK_DIAGNOSTICS_PRESERVED", [ERMAK_DIAG], "SCRIPT_ORDER_AND_DIAGNOSTIC_AUTHORITY"
    if path.startswith("app/src/main/java/"):
        if "/data/" in path:
            return "LOCAL_STATE_CODE_REVIEWED", [STATE], "SIGNED_UPGRADE_AND_STORAGE_MIGRATION"
        if "Diagnostic" in path or "HybridDiagnostic" in path or "ReferenceKnowledgePack" in path:
            return "DIAGNOSTIC_CODE_REVIEWED", [VL_DIAG], "INFORMATION_TRANSFER_THEN_BEHAVIOR_REVIEW"
        if path.endswith("BrakeCalculatorApp.kt"):
            return "CALCULATION_UI_CODE_REVIEWED", ["docs/CALCULATIONS_HISTORY_MIGRATION_CONTRACT.md"], "FORM_AND_HISTORY_PARITY"
        return "INFORMATION_DISPLAY_CODE_REVIEWED", [HISTORICAL], "DISPLAY_TEXT_AND_INTERACTION_PARITY"
    if path.startswith("qa/") or path.startswith("app/qa/"):
        if path.endswith((".trigger", ".txt")):
            return "BUILD_TRIGGER_REVIEWED", [], "NONE_FOR_INFORMATION"
        if "exam" in path:
            return "EXAM_ACCESS_QA_REVIEWED", [ZIP], "EXAM_ACCESS_HOSTING_POLICY"
        if "palette" in path or "visual" in path or "viewport" in path:
            return "UI_VISUAL_QA_REVIEWED", [], "SEPARATE_UI_STAGE"
        if "extended_emergency" in path:
            return "EXTENDED_SOURCE_QA_REVIEWED", [STAGES], "SOURCE_AUTHORITY_AND_WARNED_MODE"
        if "package_b" in path or "package_c" in path:
            return "SCHEME_GENERATOR_QA_REVIEWED", ["docs/data-migration/shared-scheme-flow-layout-dispositions.json"], "SCRIPT_LITERAL_AND_DISPLAY_PARITY"
        return "VALIDATOR_OR_GENERATOR_CODE_REVIEWED", [], "ASSERTION_OR_PROJECTION_PARITY"
    if path.startswith("patch/app/"):
        if path.endswith("BrakeCalculator.kt"):
            return "CALCULATION_CODE_CONTRACT_REVIEWED", ["docs/CALCULATIONS_HISTORY_MIGRATION_CONTRACT.md"], "NUMERICAL_AND_UPGRADE_PARITY"
        return "LEGACY_DIAGNOSTIC_CODE_REVIEWED", [VL_DIAG], "INFORMATION_TRANSFER_THEN_BEHAVIOR_REVIEW"
    if path == "RailBrakeCalculator.zip":
        return "ARCHIVE_COMPOSITION_REVIEWED", [ZIP], "ARCHIVE_ONLY_MEMBER_OBJECT_DECISIONS"
    if path.endswith(".apk"):
        return "HISTORICAL_BINARY_REVIEWED", [], "NO_RUNTIME_IMPORT"
    if path == "patch/design/launcher_icon.webp.b64":
        return "LEGACY_UI_MEDIA_REVIEWED", [], "SEPARATE_UI_STAGE"
    return "PROJECT_OR_BUILD_CONTEXT_REVIEWED", [], "NONE_FOR_INFORMATION"


def project():
    triage = json.loads((DIRECTORY / "pending-extraction-evidence.json").read_text())
    discovery = json.loads((DIRECTORY / "source-discovery-ledger.json").read_text())
    paths = {(r["sourcePath"], r["sourceObjectId"], r["sourceArtifactGitBlob"])
             for r in discovery["rows"] if r["disposition"] == "PENDING_EXTRACTION"}
    assert len(paths) == len(triage["rows"]) == 254
    existing = {r["sourcePath"]: r["evidencePaths"] for r in triage["rows"] if r["evidencePaths"]}
    assert len(existing) == 12  # five prior Kotlin sources, six dispositions, one pantograph script
    rows = []
    for row in triage["rows"]:
        key = (row["sourcePath"], row["sourceObjectId"], row["sourceArtifactGitBlob"])
        assert key in paths
        outcome, evidence, gate = decide(row["sourcePath"], existing)
        assert all((ROOT / path).is_file() for path in evidence), row["sourcePath"]
        rows.append({"sourcePath": row["sourcePath"], "sourceObjectId": row["sourceObjectId"],
                     "sourceArtifactGitBlob": row["sourceArtifactGitBlob"],
                     "sourceFileReview": outcome, "evidencePaths": evidence,
                     "remainingGate": gate, "finalObjectDisposition": None,
                     "publicationDecision": None})
    assert len({(r["sourcePath"], r["sourceObjectId"]) for r in rows}) == 254
    return {"schemaVersion": 1, "donorCommit": discovery["sourceCommit"],
            "scope": "254/254 provisional extraction file/container rows reviewed by source role",
            "note": "File-level review/preservation is distinct from object-level semantic parity, current authority, runtime activation and publication. The older discovery labels and unresolved gates remain explicit.",
            "reviewCounts": dict(sorted(Counter(r["sourceFileReview"] for r in rows).items())),
            "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text() == encoded
    else:
        OUTPUT.write_text(encoded)
    print("PENDING_EXTRACTION_REVIEW_PASS 254")


if __name__ == "__main__":
    main()
