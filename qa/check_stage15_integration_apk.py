#!/usr/bin/env python3
"""Stage 15 cross-feature audit of the ACTUAL built APK.

This is a packaging and source-boundary check, not device execution, a
normative approval, or proof that all donor features have been migrated.
Reference-only CANDIDATE knowledge is intentionally retained; action grants
are not inferred from the presence of an asset.
"""
from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

APK = Path("app-shell/build/outputs/apk/debug/app-shell-debug.apk")
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
EXPECTED_MODELS = {"2es5k", "3es5k", "chme3", "chme3t", "chme3e", "tem2", "tem2u"}
COMMON_PACKS = {
    "common/knowledge/articles.pack.json": (45, {"KNOWLEDGE": 26}),
    "common/safety/articles.pack.json": (22, {"SAFETY": 22}),
    "common/first-aid/topics.pack.json": (20, {"FIRST_AID": 18}),
}
FORBIDDEN_ROOTS = (
    "assets/electric/ermak/",
    "assets/diesel/chme3-family/",
    "assets/diesel/tem2-family/",
    "assets/locomotive-migration/",
    "assets/assistant_voice/",
)
PROCEDURE_FIELDS = {
    "blocks", "steps", "actions", "procedure", "instructions",
    "actionDisposition", "execution", "links",
}


class ApkAuditError(ValueError):
    """APK cannot be accepted as the Stage 15 reference-safe QA baseline."""


def check_apk(path: Path) -> dict[str, int]:
    if not path.is_file():
        raise ApkAuditError(f"Debug APK missing: {path}")
    with ZipFile(path) as apk:
        names = apk.namelist()
        assets = {n for n in names if n.startswith("assets/")}
        if len(names) != len(set(names)):
            raise ApkAuditError("Duplicate ZIP member paths in APK")
        if "AndroidManifest.xml" not in names or "classes.dex" not in names:
            raise ApkAuditError("Android manifest or primary dex absent")
        leaks = [
            n for n in assets
            if n.lower().startswith(FORBIDDEN_ROOTS)
            or any(part in {"migration", "authoring"} for part in n.lower().split("/"))
            or ".candidate." in n.lower() or ".research." in n.lower()
            or "sherpa" in n.lower() or n.lower().endswith(".onnx")
        ]
        if leaks:
            raise ApkAuditError(f"Unreviewed/research/voice assets in APK: {leaks[:5]}")

        def read_json(asset: str) -> dict:
            if asset not in assets:
                raise ApkAuditError(f"Missing APK asset: {asset}")
            try:
                return json.loads(apk.read(asset).decode("utf-8"))
            except (ValueError, UnicodeError) as exc:
                raise ApkAuditError(f"Invalid JSON: {asset}") from exc

        index = read_json("assets/electric/vl80s/runtime-index.json")
        if index.get("schemaVersion") != 1 or index.get("modelId") != "vl80s":
            raise ApkAuditError("Published VL80S runtime index changed identity")
        packs = index.get("packs")
        if not isinstance(packs, list) or len(packs) != len(set(packs)):
            raise ApkAuditError("VL80S pack index is missing/duplicated")
        published_core = [
            p for p in packs
            if "/recommended/" not in p and "/extended/" not in p
        ]
        if len(published_core) != 28:
            raise ApkAuditError(f"VL80S core index changed unexpectedly: {len(published_core)}")
        referenced = published_core + [index.get("profileCatalog")]
        referenced += list(index.get("featureIndexes", {}).values())
        if not all(isinstance(p, str) and p.startswith("electric/vl80s/") for p in referenced):
            raise ApkAuditError("VL80S core index contains invalid or cross-model references")
        for relative in referenced:
            if "assets/" + relative not in assets:
                raise ApkAuditError(f"VL80S referenced core asset absent: {relative}")

        all_common = []
        for relative, (count, types) in COMMON_PACKS.items():
            pack = read_json("assets/" + relative)
            entries = pack.get("entries", [])
            manifest = pack.get("manifest", {})
            if len(entries) != count or set(manifest.get("entries", [])) != {e.get("id") for e in entries}:
                raise ApkAuditError(f"Common pack count/manifest mismatch: {relative}")
            if manifest.get("modelIds") or manifest.get("variantIds"):
                raise ApkAuditError(f"Common pack incorrectly model-scoped: {relative}")
            for kind, expected in types.items():
                if sum(e.get("type") == kind for e in entries) != expected:
                    raise ApkAuditError(f"Common type partition mismatch: {relative}/{kind}")
            for e in entries:
                if e.get("owner", {}).get("kind") != "COMMON" or e.get("publicationStatus") != "CANDIDATE" or e.get("actionDisposition") != "INFORMATION_ONLY":
                    raise ApkAuditError(f"Common entry silently promoted or foreign: {e.get('id')}")
            all_common.extend(entries)
        source_ids = {e["id"] for e in all_common if e.get("type") == "SOURCE"}
        articles = [e for e in all_common if e.get("type") != "SOURCE"]
        if len(articles) != 66 or len({e["id"] for e in articles}) != 66:
            raise ApkAuditError("Expected 66 unique common reference cards")
        for e in articles:
            refs = e.get("sourceRefs", [])
            if not refs or not set(refs) <= source_ids or not e.get("summary"):
                raise ApkAuditError(f"Common reference missing provenance/summary: {e.get('id')}")

        preview = read_json("assets/crew-reference/summaries.json")
        entries = preview.get("entries", [])
        if preview.get("schemaVersion") != 1 or preview.get("donorCommit") != DONOR or len(entries) != 7:
            raise ApkAuditError("Pinned donor reference identity/count mismatch")
        if {e.get("modelId") for e in entries} != EXPECTED_MODELS:
            raise ApkAuditError("Family reference coverage or model identity mismatch")
        for e in entries:
            if PROCEDURE_FIELDS.intersection(e) or not e.get("title") or not e.get("summary"):
                raise ApkAuditError(f"Executable/empty family preview: {e.get('id')}")
            if e.get("scope") not in {"DONOR_VARIANT", "EXECUTION_UNVERIFIED"}:
                raise ApkAuditError(f"Unknown family reference scope: {e.get('id')}")
            if (e.get("scope") == "DONOR_VARIANT") != (e.get("executionId") is not None):
                raise ApkAuditError(f"Unverified family execution silently asserted: {e.get('id')}")
            if not isinstance(e.get("donorBlobSha"), str) or len(e["donorBlobSha"]) != 40:
                raise ApkAuditError(f"Family donor provenance missing: {e.get('id')}")

        return {
            "vl80s_core_packs": len(published_core),
            "common_references": len(articles),
            "family_previews": len(entries),
            "forbidden_assets": 0,
        }


def main() -> None:
    result = check_apk(APK)
    print("STAGE15_APK_INTEGRATION_PASS " + " ".join(f"{k}={v}" for k, v in result.items()))


if __name__ == "__main__":
    main()
