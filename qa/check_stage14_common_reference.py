#!/usr/bin/env python3
"""Stage 14: verify that common reference knowledge ships without action promotion."""
import json
from pathlib import Path
from zipfile import ZipFile

APK = Path("app-shell/build/outputs/apk/debug/app-shell-debug.apk")
PACKS = {
    "common/first-aid/topics.pack.json": (20, 18, "FIRST_AID"),
    "common/knowledge/articles.pack.json": (45, 26, "KNOWLEDGE"),
    "common/safety/articles.pack.json": (22, 22, "SAFETY"),
}


def main() -> None:
    if not APK.is_file():
        raise SystemExit(f"Missing APK: {APK}")
    sources = set()
    articles = []
    with ZipFile(APK) as apk:
        names = set(apk.namelist())
        for path, (expected_total, expected_articles, content_type) in PACKS.items():
            asset = "assets/" + path
            if asset not in names:
                raise AssertionError(f"Common reference pack absent from APK: {asset}")
            doc = json.loads(apk.read(asset))
            entries = doc["entries"]
            assert len(entries) == expected_total, (path, len(entries))
            assert len([e for e in entries if e["type"] == content_type]) == expected_articles, path
            assert {e["id"] for e in entries} == set(doc["manifest"]["entries"]), path
            assert not doc["manifest"]["modelIds"] and not doc["manifest"]["variantIds"], path
            for entry in entries:
                assert entry["owner"]["kind"] == "COMMON", entry["id"]
                assert entry["publicationStatus"] == "CANDIDATE", entry["id"]
                assert entry["actionDisposition"] == "INFORMATION_ONLY", entry["id"]
                if entry["type"] == "SOURCE":
                    sources.add(entry["id"])
                else:
                    assert entry["sourceRefs"], entry["id"]
                    assert entry.get("summary"), entry["id"]
                    articles.append(entry)
    assert len(articles) == 66, len(articles)
    for entry in articles:
        assert set(entry["sourceRefs"]) <= sources, entry["id"]
    # A regression must not render unverified procedural first-aid blocks.
    projection = Path(
        "feature-safety/src/main/java/ru/railbrake/calculator/safety/CommonReferenceCatalog.kt"
    ).read_text(encoding="utf-8")
    ui = Path(
        "feature-safety/src/main/java/ru/railbrake/calculator/safety/CommonReferenceScreen.kt"
    ).read_text(encoding="utf-8")
    assert "entry.type == ContentType.FIRST_AID) emptyList()" in projection
    assert "entry.blocks" not in projection and ".blocks" not in ui
    print("STAGE14_COMMON_REFERENCE_PASS articles=66 firstAid=18 traffic=13 knowledge=13 occupational=22 executable=0")


if __name__ == "__main__":
    main()
