#!/usr/bin/env python3
"""Index exact historical source sections without interpreting or publishing them."""

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
OUTPUT = ROOT / "content-packs/locomotive-migration/migration/historical-section-index.candidate.json"
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*\r?\n?$")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def project():
    source = json.loads(SOURCE.read_text())
    documents = []
    total = 0
    for document in source["documents"]:
        original = document["exactSourceText"]
        lines = original.splitlines(keepends=True)
        headings = [(i, match) for i, line in enumerate(lines)
                    if (match := HEADING.match(line))]
        starts = ([0] if not headings or headings[0][0] != 0 else []) + [i for i, _ in headings]
        if not starts:
            starts = [0]
        sections = []
        stack = []
        for ordinal, start in enumerate(starts):
            end = starts[ordinal + 1] if ordinal + 1 < len(starts) else len(lines)
            segment = "".join(lines[start:end])
            match = HEADING.match(lines[start]) if start < len(lines) else None
            level = len(match.group(1)) if match else None
            while stack and (level is None or stack[-1][0] >= level):
                stack.pop()
            parent = stack[-1][1] if stack else None
            section_id = f"historical-document.{sha(document['sourcePath'])[:16]}.section-{ordinal:03}"
            sections.append({"candidateId": section_id, "ordinal": ordinal,
                             "startLine": start + 1, "endLineExclusive": end + 1,
                             "headingLevel": level,
                             "heading": match.group(2).strip() if match else None,
                             "parentCandidateId": parent,
                             "sourceTextSha256": sha(segment)})
            if level is not None:
                stack.append((level, section_id))
        assert "".join("".join(lines[s["startLine"] - 1:s["endLineExclusive"] - 1])
                       for s in sections) == original
        total += len(sections)
        documents.append({"sourcePath": document["sourcePath"],
                          "sourceBlobSha": document["sourceBlobSha"],
                          "sourceTextSha256": sha(original),
                          "sections": sections})
    assert len(documents) == source["documentCount"] == 50
    return {"schemaVersion": 1, "donorCommit": source["donorCommit"],
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "currentAuthorityVerified": False, "actionAuthorityGranted": False,
            "sourceTextPath": str(SOURCE.relative_to(ROOT)),
            "interpretation": "Exact nonoverlapping source line spans. Headings and hierarchy are documentary only; no canonical technical assertion, current rule or action is inferred.",
            "documentCount": len(documents), "sectionCount": total, "documents": documents}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text() == encoded
    else:
        OUTPUT.write_text(encoded)
    print("HISTORICAL_SECTION_INDEX_PASS", project()["documentCount"], project()["sectionCount"])


if __name__ == "__main__":
    main()
