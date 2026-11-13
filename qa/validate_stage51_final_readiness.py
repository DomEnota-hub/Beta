#!/usr/bin/env python3
"""Stage 51: source/QA APK handoff gate, never operational or device approval."""
import argparse
import copy
import hashlib
import json
import os
import re
import zipfile
from pathlib import Path

from validate_stage49_cross_family_research import run as stage49_run, negative as stage49_negative
from validate_stage50_runtime_boundary import audit as stage50_audit, negative as stage50_negative, check_apk

ROOT = Path(__file__).resolve().parents[1]
DEVICE_REGISTER = ROOT / "docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md"
EXPECTED = {"VL80S_BATCH": 95, "ERMAK": 136, "CHME3": 68, "TEM2": 24}


def need(condition, reason):
    if not condition:
        raise AssertionError(reason)


def check_device_register(content):
    need("## Статус: DEFERRED_TO_POST_RELEASE_DEVICE_QA" in content,
         "device QA register status changed without physical testing")
    need("NOT_RUN / DEFERRED" in content and "не ставить PASS" in content,
         "device QA falsely promoted or handoff criteria missing")
    need("после компиляции кода и выпуска тестовой сборки" in content,
         "device QA timing rule missing")


def audit_source():
    groups, gaps = stage49_run()
    counts = {name: len(candidates) for name, candidates in groups.items()}
    need(counts == EXPECTED, "cross-family research count drift")
    need(not any(g["type"] == "MISSING_PER_CANDIDATE_DEVICE_QA_MARKER"
                 for g in gaps), "missing per-candidate deferred device QA marker")
    stage50 = stage50_audit()
    need(stage50["earlySourceIdentities"] == 8 and
         stage50["chme3DeviceQAMarkersRepaired"] == 12 and
         stage50["runtimeApproval"] is False and
         stage50["earlyGraphParity"] == "NOT_VERIFIED",
         "Stage 50 reconciliation or blocked gate drift")
    check_device_register(DEVICE_REGISTER.read_text(encoding="utf-8"))
    gradle = (ROOT / "app-shell/build.gradle.kts").read_text(encoding="utf-8")
    match = re.search(r'versionName\s*=\s*"([^"]+)"', gradle)
    need(match is not None and "alpha" in match.group(1).lower(),
         "expected non-production alpha version label")
    need(re.search(r'applicationId\s*=\s*"ru\.railbrake\.calculator"', gradle),
         "application ID changed without release review")
    return {"counts": counts, "researchCandidates": sum(counts.values()) + 8,
            "earlyVL80S": 8, "deviceQA": "NOT_RUN_DEFERRED",
            "runtimeApproval": False, "productionApproved": False,
            "installedVariantVerified": False, "earlyGraphParity": "NOT_VERIFIED",
            "buildVersion": match.group(1)}


def make_evidence(apk, source):
    need(apk.is_file(), "debug APK not assembled")
    with zipfile.ZipFile(apk) as archive:
        check_apk(archive)
    source_head = os.environ.get("SOURCE_HEAD_SHA", "")
    build_sha = os.environ.get("GITHUB_SHA", "")
    need(re.fullmatch(r"[0-9a-f]{40}", source_head) is not None,
         "missing exact source HEAD for QA artifact")
    need(re.fullmatch(r"[0-9a-f]{40}", build_sha) is not None,
         "missing CI build commit for QA artifact")
    return {"schema": "railbrake.stage51.debug-evidence.v1",
            "artifactKind": "INTERNAL_DEBUG_QA_APK_NOT_PRODUCTION",
            "sourceHeadSha": source_head, "ciBuildSha": build_sha,
            "apkFilename": apk.name, "apkBytes": apk.stat().st_size,
            "apkSha256": hashlib.sha256(apk.read_bytes()).hexdigest(),
            "buildVersion": source["buildVersion"],
            "researchCandidates": source["researchCandidates"],
            "publicationStatus": "QA_ARTIFACT_ONLY_NOT_RELEASED",
            "deviceQA": "NOT_RUN_DEFERRED", "runtimeResearchImport": False,
            "productionApproved": False, "operationallyApproved": False,
            "sourceRoleSafetyGates": "UNVERIFIED_BLOCKED"}


def check_evidence_contract(data):
    need(data.get("schema") == "railbrake.stage51.debug-evidence.v1" and
         data.get("artifactKind") == "INTERNAL_DEBUG_QA_APK_NOT_PRODUCTION" and
         data.get("publicationStatus") == "QA_ARTIFACT_ONLY_NOT_RELEASED",
         "QA artifact must not claim a production release")
    need(data.get("deviceQA") == "NOT_RUN_DEFERRED" and
         data.get("runtimeResearchImport") is False and
         data.get("productionApproved") is False and
         data.get("operationallyApproved") is False and
         data.get("sourceRoleSafetyGates") == "UNVERIFIED_BLOCKED",
         "QA artifact claims unearned authorization")
    need(data.get("researchCandidates") == 331 and
         data.get("apkFilename") == "app-shell-debug.apk",
         "QA evidence corpus or APK identity drift")
    need(re.fullmatch(r"[0-9a-f]{40}", data.get("sourceHeadSha", "")) is not None and
         re.fullmatch(r"[0-9a-f]{40}", data.get("ciBuildSha", "")) is not None,
         "QA evidence source/build commit invalid")
    need(re.fullmatch(r"[0-9a-f]{64}", data.get("apkSha256", "")) is not None and
         isinstance(data.get("apkBytes"), int) and data["apkBytes"] > 0,
         "QA evidence APK hash/size invalid")


def verify_evidence(data, apk):
    check_evidence_contract(data)
    need(apk.stat().st_size == data["apkBytes"] and
         hashlib.sha256(apk.read_bytes()).hexdigest() == data["apkSha256"],
         "APK content differs from evidence manifest")
    with zipfile.ZipFile(apk) as archive:
        check_apk(archive)


def negative(source):
    groups, _ = stage49_run()
    count = stage49_negative(groups) + stage50_negative()
    original = DEVICE_REGISTER.read_text(encoding="utf-8")
    try:
        check_device_register(original.replace(
            "## Статус: DEFERRED_TO_POST_RELEASE_DEVICE_QA",
            "## Статус: PASS", 1))
    except AssertionError:
        count += 1
    else:
        raise AssertionError("device QA PASS mutation escaped")
    sample = {"schema": "railbrake.stage51.debug-evidence.v1",
              "artifactKind": "INTERNAL_DEBUG_QA_APK_NOT_PRODUCTION",
              "publicationStatus": "QA_ARTIFACT_ONLY_NOT_RELEASED",
              "deviceQA": "NOT_RUN_DEFERRED", "runtimeResearchImport": False,
              "productionApproved": False, "operationallyApproved": False,
              "sourceRoleSafetyGates": "UNVERIFIED_BLOCKED",
              "researchCandidates": source["researchCandidates"],
              "apkFilename": "app-shell-debug.apk", "sourceHeadSha": "a" * 40,
              "ciBuildSha": "b" * 40, "apkSha256": "c" * 64, "apkBytes": 1}
    check_evidence_contract(sample)
    for key, value in (("deviceQA", "PASS"), ("productionApproved", True),
                       ("runtimeResearchImport", True), ("researchCandidates", 332),
                       ("publicationStatus", "PRODUCTION"),
                       ("sourceRoleSafetyGates", "APPROVED")):
        modified = copy.deepcopy(sample)
        modified[key] = value
        try:
            check_evidence_contract(modified)
        except AssertionError:
            count += 1
        else:
            raise AssertionError("unsafe evidence mutation escaped: " + key)
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    parser.add_argument("--apk", type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--verify-evidence", type=Path)
    args = parser.parse_args()
    need(not args.evidence or args.apk, "--evidence requires --apk")
    need(not args.verify_evidence or args.apk, "--verify-evidence requires --apk")
    source = audit_source()
    if args.negative:
        source["rejectedUnsafeMutations"] = negative(source)
    if args.apk:
        need(args.apk.is_file(), "APK missing")
        with zipfile.ZipFile(args.apk) as archive:
            check_apk(archive)
        source["apkResearchIsolation"] = "PASS"
    if args.evidence:
        data = make_evidence(args.apk, source)
        check_evidence_contract(data)
        args.evidence.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        source["evidencePath"] = str(args.evidence)
    if args.verify_evidence:
        verify_evidence(json.loads(args.verify_evidence.read_text(encoding="utf-8")), args.apk)
        source["evidenceVerified"] = True
    print("STAGE51_FINAL_HANDOFF " + json.dumps(source, ensure_ascii=False))


if __name__ == "__main__":
    main()
