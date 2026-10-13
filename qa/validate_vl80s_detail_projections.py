#!/usr/bin/env python3
"""Check legacy detail-card projections against hotspots and pinned Kotlin."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content-packs/electric/vl80s/atlas/interactive"
INDEX = BASE / "detail-article-projections.json"
HOTSPOTS = BASE / "layout-hotspots.json"
SOURCE = ROOT / "content-packs/electric/vl80s/migration/source-assets/KnowledgeRepository.kt"
KNOWLEDGE = ROOT / "content-packs/electric/vl80s/technical-data/knowledge/legacy-articles.pack.json"


def validate():
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    atlas = json.loads(HOTSPOTS.read_text(encoding="utf-8"))
    knowledge = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
    kotlin = SOURCE.read_text(encoding="utf-8")
    assert index["modelId"] == atlas["modelId"] == "vl80s"
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["sourceSnapshot"]["blobSha"] == knowledge["manifest"]["checksums"]["KnowledgeRepository.gitBlob"]
    assert index["hotspotAsset"] == str(HOTSPOTS.relative_to(ROOT))
    rule = index["projectionRule"]
    assert rule["legacyId"] == "vl80-detail-${hotspot.id}"
    assert rule["title"] == "ВЛ80С: ${hotspot.title}"
    assert rule["category"] == "ВЛ80С · оборудование"
    assert rule["legacyStatus"] == "Подробная карточка"
    assert rule["source"] == {
        "title": "«Расположение оборудования на электровозе ВЛ 80С», учебная методическая разработка, Воронеж, 2019",
        "note": "Подробная карточка сформирована по встроенной схеме.",
    }
    assert 'id = "vl80-detail-${hotspot.id}"' in kotlin
    assert 'title = "ВЛ80С: ${hotspot.title}"' in kotlin
    assert 'body = listOf(hotspot.details) + hotspot.learnMore' in kotlin
    assert 'tags = listOf(hotspot.id, hotspot.title, hotspot.subtitle, "ВЛ80С", "оборудование")' in kotlin
    assert 'relatedArticleIds = if (hotspot.id == "mk") listOf("vl80-pneumatic-simulator", "vl80-pneumatic-groups") else listOf("vl80-layout")' in kotlin
    assert len(atlas["hotspots"]) == atlas["hotspotCount"] == len(index["projections"]) == 15
    legacy_ids = [entry["legacyId"] for entry in index["projections"]]
    assert len(legacy_ids) == len(set(legacy_ids))
    imported = {entry["aliases"][0] for entry in knowledge["entries"] if entry["type"] == "KNOWLEDGE"}
    for hotspot, projection in zip(atlas["hotspots"], index["projections"]):
        assert projection["hotspotId"] == hotspot["id"]
        assert projection["legacyId"] == "vl80-detail-" + hotspot["id"]
        assert projection["legacyId"] not in imported
        related = ["vl80-pneumatic-simulator", "vl80-pneumatic-groups"] if hotspot["id"] == "mk" else ["vl80-layout"]
        assert projection["relatedLegacyArticleIds"] == related
        assert set(related) <= imported
        assert projection["canonicalEquipmentId"] == hotspot.get("equipmentId")
        assert hotspot["title"] and hotspot["subtitle"] and hotspot["details"]
        assert isinstance(hotspot["learnMore"], list)
    assert sum(p["canonicalEquipmentId"] is not None for p in index["projections"]) == 4
    print("VL80S detail projections: 15 legacy card IDs resolve to 15 complete hotspots; 4 existing equipment links")


if __name__ == "__main__":
    validate()
