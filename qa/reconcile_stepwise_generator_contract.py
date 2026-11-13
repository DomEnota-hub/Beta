#!/usr/bin/env python3
"""Compare pinned Package B scheme wording with preserved source metadata."""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/locomotive-migration/source-assets/build_package_b_stepwise_flows.py"
METADATA = ROOT / "content-packs/locomotive-migration/shared-scheme-source-metadata.candidate.json"
SOURCE_BLOB = "83ec7c878edddabdf181ae417a9794e52b6c560b"


def main():
    raw = SOURCE.read_bytes()
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == SOURCE_BLOB
    tree = ast.parse(raw.decode("utf-8"))
    assignments = {statement.targets[0].id: statement.value for statement in tree.body
                   if isinstance(statement, ast.Assign) and len(statement.targets) == 1
                   and isinstance(statement.targets[0], ast.Name)}
    legend = ast.literal_eval(assignments["FLOW_LEGEND"])
    assert len(legend) == 20
    original = assignments["CONTRACT"]
    assert isinstance(original, ast.Dict)
    fields = {ast.literal_eval(key): value for key, value in zip(original.keys, original.values)}
    assert set(fields) == {"representationKinds", "domains", "rules", "legend"}
    contract = {key: ast.literal_eval(fields[key]) for key in ("representationKinds", "domains", "rules")}
    contract["legend"] = [{"flowKind": key, "label": value[0], "lineStyle": value[1]}
                          for key, value in legend.items()]
    sources = json.loads(METADATA.read_text(encoding="utf-8"))["sources"]
    source = next(item for item in sources if item["sourcePath"].endswith("stepwise_scheme_flows.json"))
    assert source["metadata"]["contract"] == contract
    print("STEPWISE_GENERATOR_CONTRACT_PASS", len(contract["rules"]), len(contract["legend"]))


if __name__ == "__main__":
    main()
