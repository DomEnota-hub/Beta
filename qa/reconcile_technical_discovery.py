#!/usr/bin/env python3
"""Join technical discovery groups to current evidence without changing their dispositions."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/data-migration/source-discovery-ledger.json"
DESTINATION = ROOT / "docs/data-migration/technical-discovery-evidence.json"

CHME3 = "content-packs/diesel/chme3-family/migration/source-audit.json"
TEM2 = "content-packs/diesel/tem2-family/migration/source-audit.json"
ERMAK = "content-packs/electric/ermak/migration/source-audit.json"
VL80S = "content-packs/electric/vl80s"
SHARED = "content-packs/locomotive-migration"

# A path points to source-preservation evidence, never by itself to publication.
EVIDENCE = {
    **{name: ("INFORMATION", "SOURCE_AUDIT_AND_MODEL_PACKS", [CHME3]) for name in (
        "chme3_chme3_catalog.json.gz", "chme3_chme3_diagnostics.json.gz",
        "chme3_chme3t_catalog.json.gz", "chme3_chme3t_diagnostics.json.gz",
        "chme3_chme3e_catalog.json.gz", "chme3_chme3e_diagnostics.json.gz")},
    **{name: ("INFORMATION", "SOURCE_AUDIT_AND_MODEL_PACKS", [TEM2]) for name in (
        "tem2_tem2_catalog.json", "tem2_tem2_diagnostics.json",
        "tem2_tem2u_catalog.json", "tem2_tem2u_diagnostics.json",
        "tem2_stepwise_scheme_flows.json", "tem2_scheme_layout_metadata.json")},
    **{name: ("INFORMATION", "SOURCE_AUDIT_AND_MODEL_PACKS", [ERMAK]) for name in (
        "ermak_diagnostics.json.gz", "ermak_equipment.json.gz",
        "ermak_knowledge.json.gz", "ermak_schemes.json.gz")},
    "ermak_system_map.json.gz": ("INFORMATION", "EXACT_SOURCE_INDEX", [
        "content-packs/electric/ermak/migration/source-indexes/ermak_system_map.json.gz"]),
    "ermak_links.json.gz": ("INFORMATION", "EXACT_SOURCE_INDEX", [
        "content-packs/electric/ermak/migration/source-indexes/ermak_links.json.gz"]),
    "vl80s_equipment.json.gz": ("INFORMATION", "PROJECTED_RECORDS_AND_ROOT_SNAPSHOT", [
        f"{VL80S}/migration/equipment-context.candidate.json",
        f"{VL80S}/migration/equipment-report.json"]),
    "vl80s_acceptance.json.gz": ("INFORMATION", "COMPLETE_SOURCE_SNAPSHOT", [
        f"{VL80S}/migration/acceptance-source.candidate.json"]),
    **{name: ("INFORMATION", "COMPLETE_SOURCE_SNAPSHOT", [
        f"{VL80S}/migration/scheme-source-catalogs.candidate.json"]) for name in (
            "vl80s_electrical.json.gz", "vl80s_pneumatic.json.gz",
            "vl80s_electrical_variants.json.gz", "vl80s_pneumatic_variants.json.gz",
            "vl80s_variants.json.gz")},
    "source_presentations.json": ("INFORMATION", "EXACT_OBJECT_DISPOSITION_AND_CANDIDATES", [
        "docs/data-migration/source-presentation-dispositions.json"]),
    **{name: ("INFORMATION", "PAIRED_SOURCE_OBJECTS_AND_ROOT_METADATA", [
        "docs/data-migration/shared-scheme-flow-layout-dispositions.json",
        f"{SHARED}/shared-scheme-source-metadata.candidate.json"]) for name in (
            "stepwise_scheme_flows.json", "scheme_layout_metadata.json")},
    "diagnostic_framework_v2.json": ("DIAGNOSTIC_SOURCE", "COMPLETE_SOURCE_SNAPSHOT", [
        f"{VL80S}/diagnostics/migration/framework-source.candidate.json"]),
    "vl80s_diagnostics.json.gz": ("DIAGNOSTIC_SOURCE", "COMPLETE_SOURCE_SNAPSHOT", [
        f"{VL80S}/diagnostics/migration/diagnostics-source.candidate.json"]),
    "vl80s_pantograph_reference_pack.json": ("DIAGNOSTIC_SOURCE", "COMPLETE_SOURCE_SNAPSHOT", [
        f"{VL80S}/diagnostics/migration/pantograph-reference-source.candidate.json"]),
    "extended_emergency_runtime.json": ("DIAGNOSTIC_SOURCE", "COMPLETE_OBJECTS_IN_MODEL_CANDIDATES", [
        "content-packs/diesel/chme3-family/diagnostics/extended/source-candidates.candidate.json",
        "content-packs/diesel/tem2-family/diagnostics/extended/source-candidates.candidate.json",
        f"{SHARED}/extended-emergency-source-metadata.candidate.json"]),
    "extended_emergency_policy.json": ("DIAGNOSTIC_SOURCE", "COMPLETE_SOURCE_SNAPSHOT", [
        f"{SHARED}/extended-emergency-policy-source.candidate.json"]),
    "scheme_semantic_palette.json": ("SEPARATE_UI", "DEFERRED", []),
    "scheme_view_contract.json": ("SEPARATE_UI", "DEFERRED", []),
}


def project():
    ledger = json.loads(LEDGER.read_text())
    prefix = "app/src/main/assets/technical/"
    rows = [row for row in ledger["rows"] if row["sourcePath"].startswith(prefix)]
    assert len(rows) == 70 and len({row["sourcePath"] for row in rows}) == 35
    assert {row["sourcePath"].removeprefix(prefix) for row in rows} == set(EVIDENCE)
    projected = []
    for row in rows:
        name = row["sourcePath"].removeprefix(prefix)
        phase, evidence_kind, paths = EVIDENCE[name]
        assert row["disposition"] == "PENDING_MAPPING"
        assert all((ROOT / path).is_file() for path in paths)
        projected.append({
            "sourcePath": row["sourcePath"],
            "sourceObjectId": row["sourceObjectId"],
            "sourceArtifactGitBlob": row["sourceArtifactGitBlob"],
            "sourceCount": row["sourceCount"],
            "discoveryDisposition": row["disposition"],
            "phase": phase,
            "evidenceKind": evidence_kind,
            "evidencePaths": paths,
            "publicationDecision": None,
        })
    return {
        "schemaVersion": 1,
        "donorCommit": ledger["sourceCommit"],
        "scope": "35 technical source files / 70 discovered field groups",
        "note": "Evidence pointer by discovery group; source-object checks remain in their independent projectors. No discovery status or publication authority is changed.",
        "rows": projected,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert DESTINATION.read_text() == encoded
    else:
        DESTINATION.write_text(encoded)
    print("TECHNICAL_DISCOVERY_EVIDENCE_PASS", 35, 70)


if __name__ == "__main__":
    main()
