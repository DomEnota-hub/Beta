#!/usr/bin/env python3
"""Stage 18 Ermak corpus-wide candidate audit; no runtime publication."""
import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/diagnostics"
PACKS = ROOT / "content-packs/electric/ermak/diagnostics/recommended"
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
GZIP = "c3a22c62db42308eb4b7ee44ff2da02f47686625"
DEFERRED = "DEFERRED_TO_POST_RELEASE_DEVICE_QA"
FIELDS = (
    ("originalId", "id"), ("title", "title"), ("symptom", "symptom"),
    ("sourceObjectStatus", "status"),
    ("sourceObjectApplicability", "applicability"),
    ("sourceObjectSystemIds", "systemIds"),
    ("sourceObjectEquipmentRefs", "equipmentRefs"),
    ("sourceObjectSourceRefs", "sourceRefs"),
)
WARNING = {
    "default": "HIDDEN", "warningReadToEnd": True,
    "warningAcknowledged": True, "warningGrantsActionAuthority": False,
}
BLOCKED_FLAGS = (
    "runtimeImport", "executable", "actionAuthorityGranted",
    "sourceAuthorityVerified", "exactInstalledVariantConfirmed",
    "substantiveSafetyReviewed",
)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def donor_catalog():
    entries = []
    paths = sorted(PACKS.glob("diagnostics-*.pack.json"))
    need(len(paths) == 7, "seven pinned Ermak diagnostic packs")
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        need(data["manifest"]["entries"] == [e["id"] for e in data["entries"]],
             "pack manifest " + path.name)
        entries.extend(data["entries"])
    ids = [e["id"] for e in entries]
    need(len(ids) == len(set(ids)) == 136, "donor projection count/uniqueness")
    return {e["id"]: e["sourceObject"]["object"] for e in entries}


def check_candidate(c, source):
    ident = c["originalId"]
    for left, right in FIELDS:
        if left == "sourceObjectSourceRefs":
            projected, pinned = c[left], source[right]
            need(len(projected) == len(pinned), ident + " source ref count")
            for partial, full in zip(projected, pinned):
                need(isinstance(partial, dict) and "sourceId" in partial and
                     all(k in full and full[k] == v for k, v in partial.items()),
                     ident + " source ref projection drift")
        else:
            need(c[left] == source[right], ident + " donor field " + left)
    need(c["scenarioId"] == "ermak.diag." + ident, ident + " scenarioId")
    need(c["publicationStatus"] == "CANDIDATE", ident + " publication")
    for flag in BLOCKED_FLAGS:
        need(c[flag] is False, ident + " " + flag)
    need(c["exactInstalledVariant"] == "UNKNOWN" and
         c["unknownVariantDisposition"] == "BLOCKED", ident + " unknown profile")
    need(isinstance(c["lateMsud"], str) and any(t in c["lateMsud"] for t in ("NOT", "REVALIDATION", "BLOCKED", "UNVERIFIED", "REQUIRED", "UNKNOWN")), ident + " late MSUD must explicitly limit applicability")
    need(c["deviceQA"] == DEFERRED, ident + " device QA")
    need(c["warningGate"] == WARNING, ident + " warning gate")
    policy = c["safePolicy"]
    for key in ("observationOnly", "onlyPreviouslyRecorded", "unknownMustStop"):
        need(policy[key] is True, ident + " policy " + key)
    need(policy["triState"] == ["YES", "NO", "UNKNOWN"] and
         policy["unknownProfile"] == "BLOCKED" and
         policy["operationsAllowed"] == [], ident + " safe policy")
    sources = c["sourceRecords"]
    need("donor" in sources, ident + " donor record")
    donor = sources["donor"]
    need(donor["commit"] == PIN and donor["blobSha"] == GZIP and
         donor["objectId"] == ident, ident + " pinned provenance")
    need(donor.get("proceduresImported", False) is False, ident + " donor procedures")
    raw = donor.get("rawGzipIndependentlyDecoded")
    if raw is True:
        need(donor.get("status") == "RAW_GZIP_PARITY_VERIFIED" and
             "RAW_GZIP_VERIFIED" in donor.get("sourceKind", ""),
             ident + " unsupported raw parity claim")
    else:
        need(raw is False or raw is None, ident + " raw parity flag")
    for key, record in sources.items():
        if "currentOperatingAuthority" in record:
            need(record["currentOperatingAuthority"] is False,
                 ident + " unverified authority " + key)
    distinct = c["mustRemainDistinctFrom"]
    need(isinstance(distinct, list) and ident not in distinct and
         len(distinct) == len(set(distinct)), ident + " separation references")
    totals = [0, 0, 0]
    for mode_index, mode in enumerate(("SHORT", "DETAILED")):
        graph = c["versions"][mode]
        nodes = graph["nodes"]
        by_id = {node["id"]: node for node in nodes}
        need(len(nodes) == len(by_id) and len(nodes) >= (6 if mode == "SHORT" else 12),
             ident + " " + mode + " node count/IDs")
        need(graph["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED" and
             graph["operatingInstructionsIncluded"] is False,
             ident + " " + mode + " draft gate")
        need(graph["startNodeId"] in by_id, ident + " " + mode + " start")
        visited = set()
        pending = [graph["startNodeId"]]
        while pending:
            node_id = pending.pop()
            need(node_id in by_id, ident + " " + mode + " dangling " + node_id)
            if node_id in visited:
                continue
            visited.add(node_id)
            node = by_id[node_id]
            need(node["recordedOnly"] is True and
                 node["operationRequested"] is False and
                 node["causeConfirmed"] is False, ident + " unsafe graph node")
            need(node["sourceRefs"] and
                 set(node["sourceRefs"]) <= set(sources), ident + " graph sources")
            if node["type"] == "QUESTION":
                responses = node["responses"]
                need(set(responses) == {"YES", "NO", "UNKNOWN"},
                     ident + " incomplete tri-state")
                unknown_target = responses["UNKNOWN"]
                need(unknown_target in by_id and
                     by_id[unknown_target]["type"] == "STOP",
                     ident + " UNKNOWN must STOP")
                pending.extend(responses.values())
            else:
                need(node["type"] in ("STOP", "OBSERVATION_REPORT") and
                     node["responses"] == {}, ident + " terminal")
        need(len(visited) == len(nodes), ident + " " + mode + " unreachable nodes")
        totals[mode_index] = len(nodes)
    extensions = c["informationExtensions"]
    need(len(extensions) == 5 and
         len({e["id"] for e in extensions}) == 5,
         ident + " five distinct extensions")
    need([e["version"] for e in extensions] ==
         ["SHORT", "SHORT", "DETAILED", "DETAILED", "DETAILED"],
         ident + " extension mode distribution")
    for extension in extensions:
        need(extension["visibility"] == WARNING and
             extension["warningRequired"] is True and
             extension["executable"] is False and
             extension["actionAuthorityGranted"] is False and
             extension["operationalSteps"] == [], ident + " extension safety")
        need(extension["sourceRefs"] and
             set(extension["sourceRefs"]) <= set(sources),
             ident + " extension provenance")
    totals[2] = len(extensions)
    return totals


def audit():
    original = donor_catalog()
    documents = sorted(DOCS.glob("STAGE18_ERMAK_*_BATCH*.json"))
    need(len(documents) == 47, "47 research batch JSONs")
    batch_numbers = [int(re.search(r"_BATCH(\d+)_", p.name).group(1))
                     for p in documents]
    need(sorted(batch_numbers) == list(range(1, 48)), "batch numbers 1..47")
    catalog = {}
    totals = [0, 0, 0]
    for path in documents:
        data = json.loads(path.read_text(encoding="utf-8"))
        ledger = data["ledger"]
        candidates = data["candidates"]
        ids = [c["originalId"] for c in candidates]
        need(ledger["scenarioIds"] == ids and len(ids) == len(set(ids)),
             path.name + " membership")
        need(ledger["donorPinnedSha"] == PIN and
             ledger["donorGzipBlobSha"] == GZIP and
             ledger["sourceCatalogCount"] == 136, path.name + " pin")
        need(ledger["status"] == "CANDIDATE" and
             ledger["runtimeImport"] is False and
             ledger["actionAuthorityGranted"] is False and
             ledger["deviceQA"] == DEFERRED, path.name + " ledger gate")
        for c in candidates:
            ident = c["originalId"]
            need(ident in original, "non-donor candidate " + ident)
            need(ident not in catalog, "duplicate candidate " + ident)
            metrics = check_candidate(c, original[ident])
            totals = [a + b for a, b in zip(totals, metrics)]
            catalog[ident] = c
    need(set(catalog) == set(original), "missing donor scenario IDs: " +
         str(sorted(set(original) - set(catalog))))
    for ident, c in catalog.items():
        for other in c["mustRemainDistinctFrom"]:
            need(other in original, ident + " unknown separation target " + other)
    workflow = (ROOT / ".github/workflows/modular-bootstrap.yml").read_text(
        encoding="utf-8")
    scripts = {p.name for p in (ROOT / "qa").glob(
        "validate_stage18_ermak_*batch*.py")}
    need(len(scripts) == 47, "47 batch validators present")
    registered = set(re.findall(
        r"run:\s*python3\s+qa/(validate_stage18_ermak_[\w]+\.py)\s+--negative",
        workflow))
    need(registered == scripts | {"validate_stage18_ermak_corpus_audit.py"},
         "CI missing batch/global negative validators: " +
         str(sorted((scripts | {"validate_stage18_ermak_corpus_audit.py"}) -
                    registered)))
    reduced_refs = sum(c["sourceObjectSourceRefs"] != original[i]["sourceRefs"]
                       for i, c in catalog.items())
    return catalog, original, totals, reduced_refs


def negative(catalog, original):
    sample_id = "ER-DIAG-001"
    sample = catalog[sample_id]
    cases = [
        ("runtime promotion", lambda c: c.update(runtimeImport=True)),
        ("published draft", lambda c: c.update(publicationStatus="ACTIVE")),
        ("profile bypass", lambda c: c.update(unknownVariantDisposition="ALLOWED")),
        ("warning bypass", lambda c: c["warningGate"].update(default="VISIBLE")),
        ("operation allowed", lambda c: c["safePolicy"].update(operationsAllowed=["reset"])),
        ("donor title drift", lambda c: c.update(title="changed")),
        ("donor blob drift", lambda c: c["sourceRecords"]["donor"].update(blobSha="wrong")),
        ("unapproved authority", lambda c: c["sourceRecords"]["donor"].update(currentOperatingAuthority=True)),
        ("self-linked fault", lambda c: c.update(mustRemainDistinctFrom=[sample_id])),
        ("device QA falsified", lambda c: c.update(deviceQA="PASSED")),
        ("unsafe extension", lambda c: c["informationExtensions"][0].update(executable=True)),
        ("unknown branch bypass", lambda c: c["versions"]["SHORT"]["nodes"][0]["responses"].update(
            UNKNOWN=c["versions"]["SHORT"]["startNodeId"])),
    ]
    for label, mutate in cases:
        changed = copy.deepcopy(sample)
        mutate(changed)
        try:
            check_candidate(changed, original[sample_id])
        except (AssertionError, KeyError):
            continue
        raise AssertionError("negative mutation escaped: " + label)
    return len(cases)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    catalog, original, totals, reduced_refs = audit()
    print("STAGE18_ERMAK_CORPUS_PASS batches=47 ids=136 missing=0 duplicate=0 "
          "short_nodes=%d detailed_nodes=%d extensions=%d reduced_source_ref_projections=%d"
          % (*totals, reduced_refs))
    if args.negative:
        print("STAGE18_ERMAK_CORPUS_NEGATIVE_PASS", negative(catalog, original))
