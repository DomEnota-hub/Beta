#!/usr/bin/env python3
"""Project nine pinned Kotlin reference templates into 18 non-runtime family objects."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from migrate_common_first_aid import matched, strings
from migrate_common_knowledge import named

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content-packs/common/knowledge/migration"
INPUT = BASE / "embedded-reference-sources.candidate.json"
OUTPUT = BASE / "embedded-reference-cards.candidate.json"
FAMILIES = (("vl80s", "VL80S"), ("ermak", "ERMAK"))


def blocks(fragment):
    result = []
    for match in re.finditer(r"\bTechnicalBlock\(", fragment):
        body, _ = matched(fragment, match.end() - 1)
        values = strings(body)
        assert len(values) >= 2
        result.append({"title": values[0], "lines": values[1:]})
    assert result
    return result


def quoted(expr):
    values = strings(expr)
    assert len(values) == 1 and expr.strip().startswith('"'), expr
    return values[0]


def technical_entry(fragment, group, family, key):
    start = fragment.index("TechnicalEntry(")
    raw, _ = matched(fragment, start + len("TechnicalEntry"))
    fields = named(raw)
    assert fields["section"] == "TechnicalSection.KNOWLEDGE"
    assert fields["id"] == "id"
    suffix = "vl80-brake-jam" if group == "loadBrakeJamReference" else "vl80-wheel-flats"
    if family == "ermak":
        suffix = "ER-KB-BRAKE-JAM" if group == "loadBrakeJamReference" else "ER-KB-WHEEL-FLATS"
    search = quoted(fields["searchText"])
    return {"sourceId": suffix, "section": "KNOWLEDGE", "title": quoted(fields["title"]),
            "subtitle": quoted(fields["subtitle"]), "originalStatus": quoted(fields["status"]),
            "blocks": blocks(fields["blocks"]), "searchText": search.lower()}


def safety_entries(fragment, family, key):
    entries = []
    for match in re.finditer(r"\n\s+item\(\n", fragment):
        body, _ = matched(fragment, fragment.index("(", match.start()))
        fields = named(body)
        assert {"suffix", "title", "subtitle", "blocks"} <= set(fields)
        suffix = quoted(fields["suffix"])
        parts = blocks(fields["blocks"])
        title, subtitle = quoted(fields["title"]), quoted(fields["subtitle"])
        text = " ".join([title, subtitle] + [part for block in parts
                                                 for part in [block["title"], *block["lines"]]])
        entries.append({"sourceId": f"SAFETY-{key}-{suffix}", "section": "SAFETY",
                        "title": title, "subtitle": subtitle,
                        "originalStatus": quoted(fields["status"]) if "status" in fields else "INFORMATION",
                        "blocks": parts, "searchText": text.lower()})
    assert len(entries) == 7
    return entries


def project():
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    entries = []
    for group in source["groups"]:
        fragment = group["sourceFragment"]
        assert hashlib.sha256(fragment.encode("utf-8")).hexdigest() == group["sourceFragmentSha256"]
        for family, key in FAMILIES:
            originals = (safety_entries(fragment, family, key)
                         if group["function"] == "loadSafety" else
                         [technical_entry(fragment, group["function"], family, key)])
            for record in originals:
                entries.append({"candidateId": f"{family}.historical-reference.{record['sourceId'].lower()}",
                                "family": family, "sourceFunction": group["function"],
                                "injectorSourcePath": group["injectorSourcePath"],
                                "sourceFragmentSha256": group["sourceFragmentSha256"],
                                "publicationStatus": "CANDIDATE", "runtimeImport": False,
                                "requiresWarnedExtendedMode": True,
                                "currentAuthorityVerified": False,
                                "actionAuthorityGranted": False,
                                "actionDisposition": "INFORMATION_ONLY", "original": record})
    assert len(entries) == 18 and len({item["candidateId"] for item in entries}) == 18
    assert len([e for e in entries if e["sourceFunction"] == "loadSafety"]) == 14
    return {"schemaVersion": 1, "donorCommit": source["donorCommit"],
            "interpretation": "Historical Kotlin text, including procedural and normative claims; source status and actual locomotive applicability are not established.",
            "entries": entries}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text(encoding="utf-8") == encoded
    else:
        OUTPUT.write_text(encoded, encoding="utf-8")
    print("EMBEDDED_REFERENCE_CARD_PASS 9 18")


if __name__ == "__main__":
    main()
