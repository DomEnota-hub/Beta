#!/usr/bin/env python3
"""Verify the five model-scoped legacy cards against the pinned Kotlin source."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/electric/vl80s/migration/source-assets/KnowledgeRepository.kt"
PACK = ROOT / "content-packs/electric/vl80s/technical-data/knowledge/legacy-articles.pack.json"
IDS = (
    "vl80-layout", "vl80-pneumatic-groups", "vl80-service-brake-route",
    "vl80-pneumatic-simulator", "vl80-electrical-simulator",
)
FLAGS = ("hasInteractiveDiagram", "hasAirRoute", "hasPneumaticSimulator", "hasElectricalSimulator")
EXPECTED_BLOB = "b37ead2d66c0c976bcc850f9cde4fddc0e198fb3"


def balanced(text, start):
    depth = 0
    quoted = escaped = False
    for pos in range(start, len(text)):
        char = text[pos]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start:pos + 1]
    raise AssertionError("Unclosed Kotlin call")


LITERAL = r'"(?:\\.|[^"\\])*"'


def value(block, field, default=None):
    match = re.search(r"\b" + field + r"\s*=\s*(" + LITERAL + r"|true|false)", block)
    if not match:
        return default
    return json.loads(match.group(1))


def values(block, field):
    match = re.search(r"\b" + field + r"\s*=\s*listOf\(", block)
    if not match:
        return []
    call = balanced(block, match.end() - 1)
    return [json.loads(m.group()) for m in re.finditer(LITERAL, call)]


def extract(source, legacy_id):
    anchor = source.index('id = "' + legacy_id + '"')
    start = source.rfind("KnowledgeArticle(", 0, anchor)
    block = balanced(source, start + len("KnowledgeArticle"))
    assert value(block, "id") == legacy_id
    source_start = block.index("KnowledgeSource(") + len("KnowledgeSource")
    attribution = balanced(block, source_start)
    return {
        "id": legacy_id,
        "title": value(block, "title"),
        "category": value(block, "category"),
        "status": value(block, "status"),
        "summary": value(block, "summary"),
        "body": values(block, "body"),
        "tags": values(block, "tags"),
        "source": {key: val for key in ("title", "note", "externalUrl")
                   if (val := value(attribution, key)) is not None},
        "relatedArticleIds": values(block, "relatedArticleIds"),
        "flags": {key: value(block, key, False) for key in FLAGS},
    }


def validate():
    source_bytes = SOURCE.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes).hexdigest()
    assert git_blob == EXPECTED_BLOB, (git_blob, EXPECTED_BLOB)
    source = source_bytes.decode("utf-8")
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    entries = pack["entries"]
    ids = [entry["id"] for entry in entries]
    assert len(ids) == len(set(ids)) == 8
    assert ids == pack["manifest"]["entries"]
    for other_path in (ROOT / "content-packs").rglob("*.pack.json"):
        if other_path == PACK:
            continue
        other = json.loads(other_path.read_text(encoding="utf-8"))
        if isinstance(other, dict) and isinstance(other.get("entries"), list):
            duplicate = set(ids) & {
                item.get("id") for item in other["entries"] if isinstance(item, dict)
            }
            assert not duplicate, (str(other_path.relative_to(ROOT)), duplicate)
    assert pack["manifest"]["modelIds"] == ["vl80s"]
    assert pack["manifest"]["checksums"]["KnowledgeRepository.gitBlob"] == EXPECTED_BLOB
    source_entries = {entry["id"]: entry for entry in entries if entry["type"] == "SOURCE"}
    assert len(source_entries) == 3
    assert len({entry["title"] for entry in source_entries.values()}) == 3
    cards = entries[:5]
    assert [entry["aliases"][0] for entry in cards] == list(IDS)
    for entry, legacy_id in zip(cards, IDS):
        original = extract(source, legacy_id)
        assert entry["sourceObject"]["object"] == original, legacy_id
        assert entry["sourceObject"]["origin"]["blobSha"] == EXPECTED_BLOB
        assert entry["id"] == "vl80s.knowledge." + legacy_id
        assert entry["title"] == original["title"]
        assert entry["summary"] == original["summary"]
        assert entry["details"] == original["body"]
        assert entry["searchTerms"] == original["tags"]
        assert entry["blocks"][0]["lines"] == [original["category"], original["status"]]
        assert entry["blocks"][1]["lines"] == (original["relatedArticleIds"] or ["Связи не указаны"])
        assert entry["blocks"][2]["lines"] == ([key for key in FLAGS if original["flags"][key]] or ["Не указаны"])
        assert entry["sourceRefs"] == [entry["links"][0]["targetId"]]
        assert source_entries[entry["sourceRefs"][0]]["title"] == original["source"]["title"]
        assert entry["owner"] == {"kind": "MODEL", "modelId": "vl80s"}
        assert entry["applicability"] == {"modelIds": ["vl80s"]}
        assert entry["publicationStatus"] == "CANDIDATE"
        assert entry["actionDisposition"] == "INFORMATION_ONLY"
    for entry in source_entries.values():
        assert entry["owner"] == {"kind": "MODEL", "modelId": "vl80s"}
        assert entry["applicability"] == {"modelIds": ["vl80s"]}
        assert entry["publicationStatus"] == "CANDIDATE"
        assert entry["actionDisposition"] == "INFORMATION_ONLY"
    print("VL80S legacy knowledge: 5 exact cards, 3 unique attributions, model scope and candidate status OK")


if __name__ == "__main__":
    validate()
