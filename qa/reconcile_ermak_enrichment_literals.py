#!/usr/bin/env python3
"""Pin Ermak enrichment sources and compare their long literals to terminal source objects.

This is a textual preservation check, not proof of execution order, numerical
equivalence, variant applicability, source currency or permission to act.
"""

import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "content-packs/electric/ermak/migration/generator-source-assets"
OUTPUT = ROOT / "content-packs/electric/ermak/migration/enrichment-literal-parity.candidate.json"
REVIEW = ROOT / "docs/data-migration/pending-extraction-review.json"
PACKS = ROOT / "content-packs/electric/ermak"


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def terminal_objects():
    source_objects = []
    for path in sorted(PACKS.rglob("*.pack.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data.get("entries", []):
            if "sourceObject" in item:
                source_objects.append(item["sourceObject"]["object"])
    assert len(source_objects) == 558
    return source_objects


def static_value(node, values):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, (ast.List, ast.Tuple)):
        return [static_value(item, values) for item in node.elts]
    if isinstance(node, ast.Dict):
        return {static_value(key, values): static_value(value, values)
                for key, value in zip(node.keys, node.values)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -static_value(node.operand, values)
    raise ValueError(type(node).__name__)


def missing_role(node, parents):
    chain = []
    while node in parents:
        node = parents[node]
        chain.append(type(node).__name__)
    if chain[:4] == ["Call", "List", "Assign", "Module"]:
        return "INPUT_PATH"
    if chain[:3] == ["Call", "Expr", "Module"]:
        return "SCRIPT_COMPLETION_MESSAGE"
    if chain[:2] == ["Call", "Raise"] or chain[:3] == ["JoinedStr", "Call", "Raise"]:
        return "SCRIPT_GUARD_OR_ERROR"
    raise AssertionError(("unclassified missing literal", chain))


def project():
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    objects = terminal_objects()
    terminal = "".join(json.dumps(item, ensure_ascii=False) for item in objects)
    parameters = [param for item in objects if isinstance(item, dict)
                  for param in item.get("parameters", [])]
    references = [item["source"] for item in objects if isinstance(item, dict)
                  and isinstance(item.get("source"), dict)]
    references += [ref for item in objects if isinstance(item, dict)
                   for ref in item.get("sourceRefs", []) if isinstance(ref, dict)]
    rows = [row for row in review["rows"]
            if row["remainingGate"] == "SCRIPT_INTERMEDIATE_VALUES_AND_SOURCE_AUTHORITY"]
    assert len(rows) == 28
    result = []
    all_counts = Counter()
    for row in rows:
        source = row["sourcePath"]
        path = ARCHIVE / Path(source).name
        raw = path.read_bytes()
        assert git_blob(raw) == row["sourceArtifactGitBlob"], source
        tree = ast.parse(raw.decode("utf-8"), filename=source)
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        counts = Counter()
        unmatched = []
        values = {}
        for statement in tree.body:
            if not isinstance(statement, ast.Assign) or len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
                continue
            try:
                values[statement.targets[0].id] = static_value(statement.value, values)
            except (KeyError, ValueError, TypeError):
                continue
        for value in values.values():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and {"name", "value", "unit"} <= item.keys():
                        counts["staticParameters"] += 1
                        assert any(all(original.get(key) == field for key, field in item.items())
                                   for original in parameters), (source, item)
                        counts["exactTerminalParameters"] += 1
            elif isinstance(value, dict) and {"sourceId", "document", "title"} <= value.keys():
                counts["staticSourceReferences"] += 1
                assert value in references, (source, value)
                counts["exactTerminalSourceReferences"] += 1
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str) or len(node.value) < 30:
                continue
            counts["longStringLiterals"] += 1
            if node.value in terminal:
                counts["presentInPreservedTerminalSourceObjects"] += 1
            else:
                role = missing_role(node, parents)
                counts[role] += 1
                unmatched.append({"line": node.lineno, "role": role,
                                  "sha256": hashlib.sha256(node.value.encode("utf-8")).hexdigest()})
        all_counts.update(counts)
        result.append({"sourcePath": source, "sourceBlobSha": row["sourceArtifactGitBlob"],
                       "archivePath": path.relative_to(ROOT).as_posix(),
                       "literalCounts": dict(sorted(counts.items())),
                       "nonTerminalControlLiterals": unmatched})
    assert all_counts == {
        "longStringLiterals": 1457,
        "presentInPreservedTerminalSourceObjects": 1356,
        "INPUT_PATH": 28,
        "SCRIPT_COMPLETION_MESSAGE": 26,
        "SCRIPT_GUARD_OR_ERROR": 47,
        "staticParameters": 319,
        "exactTerminalParameters": 319,
        "staticSourceReferences": 88,
        "exactTerminalSourceReferences": 88,
    }, all_counts
    return {"schemaVersion": 1, "donorCommit": review["donorCommit"],
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "interpretation": "Long string literals only; numeric and short literal parity, execution order, source authority and variant applicability remain separate gates.",
            "totalCounts": dict(sorted(all_counts.items())), "scripts": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text(encoding="utf-8") == encoded
    else:
        OUTPUT.write_text(encoded, encoding="utf-8")
    print("ERMAK_ENRICHMENT_LITERAL_PASS 28 1356 101")


if __name__ == "__main__":
    main()
