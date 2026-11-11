#!/usr/bin/env python3
"""Group 3: verify actual APK source lineage and internal reference graph."""
import json
from pathlib import Path
from zipfile import ZipFile

APK = Path("app-shell/build/outputs/apk/debug/app-shell-debug.apk")
PACKS = (
    "common/knowledge/articles.pack.json",
    "common/safety/articles.pack.json",
    "common/first-aid/topics.pack.json",
)


def audit(archive):
    entries = {}
    for pack in PACKS:
        raw = json.loads(archive.read("assets/" + pack))
        assert {e["id"] for e in raw["entries"]} == set(raw["manifest"]["entries"])
        for entry in raw["entries"]:
            assert entry["id"] not in entries
            assert entry["publicationStatus"] == "CANDIDATE"
            assert entry["actionDisposition"] == "INFORMATION_ONLY"
            entries[entry["id"]] = entry
    sources = [e for e in entries.values() if e["type"] == "SOURCE"]
    articles = [e for e in entries.values() if e["type"] != "SOURCE"]
    assert len(sources) == 21 and len(articles) == 66
    assert all(e["sourceStatus"] == "UNKNOWN" for e in sources)
    related = 0
    for entry in articles:
        assert entry["sourceRefs"] and all(
            entries[s]["type"] == "SOURCE" for s in entry["sourceRefs"]
        )
        for link in entry.get("links", []):
            if link["type"] == "SOURCE":
                continue
            assert link["scope"] == "COMMON_INTERNAL"
            target = entries[link["targetId"]]
            assert target["type"] == link["type"]
            assert target["publicationStatus"] == "CANDIDATE"
            assert entry["type"] == target["type"]
            if entry["type"] == "KNOWLEDGE":
                section = lambda e: e["id"].startswith(
                    ("common.knowledge.signals-", "common.knowledge.movement-")
                )
                assert section(entry) == section(target)
            related += 1
    assert related == 11, related
    assert sum(e["type"] == "FIRST_AID" for e in articles) == 18
    return len(articles), len(sources), related


def main():
    assert APK.is_file(), "APK not built"
    with ZipFile(APK) as apk:
        counts = audit(apk)
    policy = Path(
        "feature-safety/src/main/java/ru/railbrake/calculator/safety/CommonReferenceCatalog.kt"
    ).read_text(encoding="utf-8")
    screen = Path(
        "feature-safety/src/main/java/ru/railbrake/calculator/safety/CommonReferenceScreen.kt"
    ).read_text(encoding="utf-8")
    assert "entry.type == ContentType.FIRST_AID) emptyList()" in policy
    assert "entry.blocks" not in policy and ".blocks" not in screen
    assert "sourceEvidence" in policy and "opened.relatedCards" in screen
    assert "CommonReferencePolicy.search(cards, searchQuery)" in screen
    print(
        "POST15_GROUP3_COMMON_PASS "
        f"articles={counts[0]} sources_unverified={counts[1]} "
        f"safe_internal_links={counts[2]} executable=0"
    )


if __name__ == "__main__":
    main()
