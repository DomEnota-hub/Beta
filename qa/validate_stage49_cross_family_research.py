#!/usr/bin/env python3
"""Stage 49: cross-family research inventory and non-promotion regression.

This checks research authoring, NOT runtime graph parity, operational approval,
installed equipment or device QA. No network access or donor modification.
"""
import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/diagnostics"
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
DEFERRED = {"DEFERRED_TO_POST_RELEASE_DEVICE_QA", "NOT_RUN_DEFERRED"}
EXPECTED = {"VL80S_BATCH": 95, "ERMAK": 136, "CHME3": 68, "TEM2": 24}


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def inventory():
    groups = {"VL80S_BATCH": {}, "ERMAK": {}, "CHME3": {}, "TEM2": {}}
    gaps = []
    for path in sorted(DOCS.glob("STAGE*.json")):
        match = re.match(r"STAGE(\d+)_", path.name)
        if not match:
            continue
        stage = int(match.group(1))
        if not (7 <= stage <= 18):
            continue
        family = "ERMAK" if stage == 18 and "_ERMAK_" in path.name else (
            "VL80S_BATCH" if 7 <= stage <= 17 else None)
        if family is None:
            continue
        data = load(path)
        if not isinstance(data.get("candidates"), list):
            continue
        if family == "ERMAK" and not re.search(r"_BATCH\d+_", path.name):
            continue
        for c in data["candidates"]:
            ident = c["originalId"]
            need(ident not in groups[family],
                 f"duplicate {family}/{ident}: {path} and {groups[family].get(ident)}")
            groups[family][ident] = (c, path)
    for family, directory, pattern in (
        ("CHME3", ROOT / "content-packs/diesel/chme3-family/diagnostics/authoring",
         "chme3*-diag-*.research.json"),
        ("TEM2", ROOT / "content-packs/diesel/tem2-family/diagnostics/authoring",
         "tem2-diag-*.research.json"),
    ):
        for path in sorted(directory.glob(pattern)):
            c = load(path)
            ident = c["originalId"]
            need(ident not in groups[family], f"duplicate {family}/{ident}: {path}")
            groups[family][ident] = (c, path)
    for family, expected in EXPECTED.items():
        need(len(groups[family]) == expected,
             f"{family} candidate inventory {len(groups[family])} != {expected}")
    # The older CHME3 rheostatic research overlay is not a 69th scenario.
    overlay = load(ROOT / "content-packs/diesel/chme3-family/diagnostics/authoring/"
                   "stage4-rheostatic.research.json")
    need(overlay["originalId"] in groups["CHME3"] and
         overlay["publicationStatus"] == "CANDIDATE" and
         overlay["runtimeImport"] is False and
         overlay["actionAuthorityGranted"] is False and
         overlay["executable"] is False,
         "CHME3 rheostatic overlay must remain blocked and not double counted")
    # The pinned VL80S source snapshot has 103 IDs; this inventory intentionally
    # covers the 95 later batch candidates only. Earlier eight require a separate
    # source-to-authoring reconciliation, not invented replacements.
    migration = load(ROOT / "content-packs/electric/vl80s/diagnostics/migration/"
                     "diagnostics-source.candidate.json")
    need(migration["donorCommit"] == PIN, "VL80S donor pin")
    source_ids = {s["id"] for s in migration["sourceObject"]["scenarios"]}
    need(len(source_ids) == 103, "VL80S pinned source count")
    need(set(groups["VL80S_BATCH"]) <= source_ids, "VL80S foreign source IDs")
    early = sorted(source_ids - set(groups["VL80S_BATCH"]))
    need(len(early) == 8, "VL80S early-source reconciliation boundary")
    gaps.append({"type": "EARLY_VL80S_RECONCILIATION_REQUIRED", "ids": early})
    return groups, gaps


def check_graph(graph, label, sources):
    nodes = graph["nodes"]
    by_id = {n["id"]: n for n in nodes}
    start = graph.get("startNodeId", nodes[0]["id"] if nodes else None)
    need(len(nodes) == len(by_id) and start in by_id,
         label + " duplicate/dangling start")
    visited, pending = set(), [start]
    while pending:
        ident = pending.pop()
        need(ident in by_id, label + " dangling " + ident)
        if ident in visited:
            continue
        visited.add(ident)
        n = by_id[ident]
        need(n.get("permittedAction") is not True and
             n.get("operationRequested") is not True and
             n.get("causeConfirmed") is not True, label + " unsafe node " + ident)
        if "recordedOnly" in n:
            need(n["recordedOnly"] is True, label + " non-recorded node")
        if n.get("sourceRefs"):
            need(set(n["sourceRefs"]) <= sources, label + " unknown source ref")
        if n["type"] == "QUESTION":
            responses = n["responses"]
            need(set(responses) == {"YES", "NO", "UNKNOWN"},
                 label + " non-tristate question")
            need(responses["UNKNOWN"] in by_id and
                 by_id[responses["UNKNOWN"]]["type"] == "STOP",
                 label + " UNKNOWN does not STOP")
            pending.extend(responses.values())
        else:
            need(n["type"] in {"STOP", "OBSERVATION_REPORT"} and
                 n.get("responses") == {}, label + " invalid terminal")
    need(visited == set(by_id), label + " unreachable graph nodes")


def check_candidate(c, family):
    ident = c["originalId"]
    label = family + "/" + ident
    need(c["publicationStatus"] == "CANDIDATE", label + " publication")
    for key in ("runtimeImport", "executable", "actionAuthorityGranted",
                "sourceAuthorityVerified", "humanSafetyReviewPassed",
                "exactInstalledVariantConfirmed", "substantiveSafetyReviewed"):
        if key in c:
            need(c[key] is False, label + " " + key)
    donor = c.get("donor", {})
    pinned = donor.get("commit", c.get("donorPinnedSha"))
    if pinned is None:
        pinned = c.get("sourceRecords", {}).get("donor", {}).get("commit")
    need(pinned == PIN, label + " donor commit")
    if "applicability" in c:
        app = c["applicability"]
        need(app["unknownProfile"] == "BLOCKED" and
             app["confirmedVariant"] is None and
             app["installedSchemeVerified"] is False,
             label + " unknown installed variant")
    else:
        need(c.get("unknownVariantDisposition",
                   c.get("safePolicy", {}).get("unknownProfile")) == "BLOCKED",
             label + " unknown variant gate")
    warning = c.get("warning", c.get("extendedWarning", c.get("warningGate")))
    need(isinstance(warning, dict), label + " missing warning")
    if "extendedHiddenByDefault" in warning:
        need(warning["extendedHiddenByDefault"] is True and
             warning["readToEndRequired"] is True and
             warning["separateAcknowledgmentRequired"] is True and
             warning["grantsActionAuthority"] is False,
             label + " warning bypass")
    else:
        need(warning["default"] == "HIDDEN" and
             warning.get("warningReadToEnd", warning.get("requiresReadToEnd")) is True and
             warning.get("warningAcknowledged",
                         warning.get("requiresAcknowledgement")) is True and
             warning["warningGrantsActionAuthority"] is False,
             label + " warning bypass")
    policy = c.get("safePolicy", c.get("safety"))
    need(isinstance(policy, dict), label + " safety policy missing")
    if "operationsAllowed" in policy:
        need(policy["operationsAllowed"] == [] and
             policy["unknownMustStop"] is True, label + " operations allowed")
    else:
        need(all(value is False for value in policy.values()),
             label + " unsafe permission flag")
    device = c.get("deviceQA")
    if isinstance(device, dict):
        device = device.get("status")
    if device is not None:
        need(device in DEFERRED, label + " false device QA PASS")
    source_records = c.get("sourceRecords", {})
    source_ids = set(source_records)
    if "sources" in c:
        source_ids = {s["id"] for s in c["sources"]}
        need(len(source_ids) == len(c["sources"]), label + " duplicate source")
        for s in c["sources"]:
            need(s.get("currentVerified") is not True and
                 s.get("installedProfileVerified") is not True and
                 s.get("authority") != "OPERATIONAL",
                 label + " unverified source promoted")
    else:
        for s in source_records.values():
            if isinstance(s, dict):
                need(s.get("currentOperatingAuthority") is not True and
                     s.get("proceduresImported") is not True,
                     label + " source authority promoted")
    need(set(c["versions"]) == {"SHORT", "DETAILED"}, label + " modes")
    for mode, graph in c["versions"].items():
        check_graph(graph, label + "/" + mode, source_ids)
    extensions = c.get("extensions", c.get("informationExtensions"))
    if extensions is None:
        extensions = (c["versions"]["SHORT"].get("extendedRoutes", []) +
                      c["versions"]["DETAILED"].get("extendedRoutes", []))
    need(len(extensions) == 5, label + " five extensions")
    for ext in extensions:
        need(ext.get("executable") is not True and
             ext.get("actionAuthorityGranted") is not True and
             ext.get("operationalSteps", ext.get("procedureSteps", [])) == [],
             label + " unsafe extension")
        if "nodes" in ext:
            check_graph(ext, label + "/EXT/" + ext.get("id", ext.get("approachId", "route")), source_ids)
        if "visibility" in ext:
            visibility = ext["visibility"]
            if "hiddenByDefault" in visibility:
                need(visibility["hiddenByDefault"] is True and
                     visibility["warningReadToEndRequired"] is True and
                     visibility["warningAcknowledgedRequired"] is True,
                     label + " extension visibility")
            elif "default" in visibility:
                need(visibility["default"] == "HIDDEN" and
                     visibility["warningReadToEnd"] is True and
                     visibility["warningAcknowledged"] is True,
                     label + " extension visibility")
    return device is None


def run():
    groups, gaps = inventory()
    missing_device = []
    for family, catalog in groups.items():
        for ident, (candidate, path) in sorted(catalog.items()):
            if check_candidate(candidate, family):
                missing_device.append(f"{family}:{ident}")
    if missing_device:
        gaps.append({"type": "MISSING_PER_CANDIDATE_DEVICE_QA_MARKER",
                     "ids": missing_device})
    return groups, gaps


def negative(groups):
    count = 0
    for family, catalog in groups.items():
        original = next(iter(catalog.values()))[0]
        changes = [
            lambda c: c.update(runtimeImport=True),
            lambda c: c.update(publicationStatus="PUBLISHED"),
            lambda c: c.update(actionAuthorityGranted=True),
            lambda c: c["versions"]["SHORT"]["nodes"][0].update(
                operationRequested=True),
            lambda c: c["versions"]["SHORT"]["nodes"][0]["responses"].update(
                UNKNOWN=c["versions"]["SHORT"]["startNodeId"]),
        ]
        for change in changes:
            modified = copy.deepcopy(original)
            change(modified)
            try:
                check_candidate(modified, family)
            except (AssertionError, KeyError):
                count += 1
            else:
                raise AssertionError(f"{family} unsafe mutation escaped")
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    groups, gaps = run()
    result = {
        "status": "RESEARCH_GATE_AUDITED_NOT_RUNTIME_APPROVED",
        "counts": {name: len(catalog) for name, catalog in groups.items()},
        "totalBatchCandidates": sum(len(c) for c in groups.values()),
        "gaps": gaps,
        "deviceQA": "NOT_RUN_DEFERRED",
    }
    if args.negative:
        result["rejectedUnsafeMutations"] = negative(groups)
    print("STAGE49_CROSS_FAMILY_AUDIT " + json.dumps(result, ensure_ascii=False))
