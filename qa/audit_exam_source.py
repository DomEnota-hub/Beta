#!/usr/bin/env python3
"""Audit pinned encrypted exam source in memory, without publishing its contents.

The original Android app embeds the decoder key in ExamQuestionRepository.kt.
This audit reads only that pinned Kotlin source and the pinned encrypted asset,
checks both Git blobs, and writes aggregate metadata without question text.
"""
import argparse
import base64
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + bytes([0]) + raw).hexdigest()

ROOT = Path(__file__).resolve().parents[1]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
KOTLIN_PATH = "app/src/main/java/ru/railbrake/calculator/core/ExamQuestionRepository.kt"
KOTLIN_SHA = "d0f1dee6b3e32c64cf20f7b5110d0f6455c1fae1"
ASSET_PATH = "app/src/main/assets/exam_questions.json"


def derive_embedded_key(kotlin):
    parts = []
    for label in ("keyPartA", "keyPartB"):
        match = re.search(r"private val " + label + r"\s*=\s*byteArrayOf\((.*?)\)", kotlin, re.S)
        assert match, label
        values = [int(n) for n in re.findall(r"-?\d+", match.group(1))]
        assert len(values) == 32, (label, len(values))
        assert all(-128 <= n <= 127 for n in values)
        parts.append(values)
    return bytes((a ^ b) & 255 for a, b in zip(*parts))


def decode(raw, kotlin):
    packed = base64.b64decode(raw)
    assert len(packed) > 32 and (len(packed) - 16) % 16 == 0
    key = derive_embedded_key(kotlin)
    result = subprocess.run(
        ["openssl", "enc", "-d", "-aes-256-cbc", "-K", key.hex(),
         "-iv", packed[:16].hex()],
        input=packed[16:], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False)
    assert result.returncode == 0, "Pinned exam payload failed AES-CBC decode"
    return json.loads(result.stdout.decode("utf-8-sig"))


def audit(root, donor):
    manifest = json.loads((root / "docs/migration/donor-asset-crosswalk.json").read_text())
    assert manifest["donor"]["commit"] == DONOR
    row, = (a for a in manifest["assets"] if a["sourcePath"] == ASSET_PATH)
    raw = (donor / ASSET_PATH).read_bytes()
    kotlin_raw = (donor / KOTLIN_PATH).read_bytes()
    assert len(raw) == row["compressedBytes"]
    assert git_blob(raw) == row["gitBlobSha"]
    assert git_blob(kotlin_raw) == KOTLIN_SHA
    root_data = decode(raw, kotlin_raw.decode("utf-8"))
    assert root_data["questionCount"] == 329
    questions = root_data["questions"]
    assert len(questions) == 329
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids))
    fields = {"id", "blockId", "blockTitle", "sourceNumber", "question",
              "correctAnswer", "category", "keywords", "requiresImage",
              "diagnosticScenarioIds", "equipmentIds", "knowledgeTopics",
              "sourceVersion"}
    assert all(fields <= set(q) for q in questions)
    assert all(isinstance(q["diagnosticScenarioIds"], list) and
               isinstance(q["equipmentIds"], list) and
               isinstance(q["keywords"], list) for q in questions)
    source_diagnostics = json.loads((root / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text())
    known_diagnostics = {q["id"] for q in source_diagnostics["sourceObject"]["scenarios"]}
    equipment_paths = (root / "content-packs/electric/vl80s/atlas/equipment").glob("*.pack.json")
    equipment_entries = [e for path in equipment_paths
                         for e in json.loads(path.read_text())["entries"]]
    known_equipment = {e["id"] for e in equipment_entries}
    known_equipment |= {e["migrationRefs"].get("legacyId") for e in equipment_entries}
    referenced_diagnostics = {s for q in questions for s in q["diagnosticScenarioIds"]}
    referenced_equipment = {s for q in questions for s in q["equipmentIds"]}
    summary = {
        "schemaVersion": 1, "donorCommit": DONOR,
        "assetPath": ASSET_PATH, "assetBlobSha": row["gitBlobSha"],
        "decoderSourcePath": KOTLIN_PATH, "decoderBlobSha": KOTLIN_SHA,
        "status": "DECODED_SOURCE_AUDIT_ONLY_NOT_MIGRATED",
        "publicationStatus": "CANDIDATE", "runtimeImport": False,
        "actionAuthorityGranted": False,
        "questionCount": len(questions),
        "uniqueQuestionIds": len(set(ids)),
        "questionIdSetSha256": hashlib.sha256(json.dumps(sorted(ids), ensure_ascii=False).encode()).hexdigest(),
        "requiresImageCount": sum(q["requiresImage"] is True for q in questions),
        "blockCount": len({q["blockId"] for q in questions}),
        "categoryCount": len({q["category"] for q in questions}),
        "sourceVersionCounts": dict(sorted(collections.Counter(q["sourceVersion"] for q in questions).items())),
        "questionsWithDiagnosticLinks": sum(bool(q["diagnosticScenarioIds"]) for q in questions),
        "questionsWithEquipmentLinks": sum(bool(q["equipmentIds"]) for q in questions),
        "distinctDiagnosticRefs": len(referenced_diagnostics),
        "distinctEquipmentRefs": len(referenced_equipment),
        "diagnosticIdsMissingFromVl80sSource": sorted(referenced_diagnostics - known_diagnostics),
        "equipmentIdsMissingFromVl80sCanonicalOrLegacy": sorted(referenced_equipment - known_equipment),
        "notes": "No plaintext questions are written to disk; applicability, source authority and runtime integration remain unverified.",
    }
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--donor-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.root, args.donor_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("EXAM_SOURCE_DECODED_AUDIT_PASS", result["questionCount"],
          "missingDiagnosticRefs=", len(result["diagnosticIdsMissingFromVl80sSource"]),
          "missingEquipmentRefs=", len(result["equipmentIdsMissingFromVl80sCanonicalOrLegacy"]))
