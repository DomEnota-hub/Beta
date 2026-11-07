#!/usr/bin/env python3
"""Stage17 composite aux-machines independent fail-closed and negative QA."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/diagnostics/STAGE17_AUX_MACHINES_FINAL_GAP_2026-11-05.json"
INVENTORY = ROOT / "content-packs/electric/vl80s/migration/diagnostics-inventory.json"
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "5f57ff2c98f02a04692e8553700ec8d23077d166"
QUESTIONS = [
    "Не работают все вспомогательные машины?",
    "ФР пытается разогнаться?",
    "Срабатывает защита конкретной машины?",
]
BOUNDARIES = {
    "vl80s.diag.phase-splitter-no-start",
    "vl80s.diag.aux-common-loss",
    "vl80s.diag.aux-machine-single-trip",
    "vl80s.diag.aux-relay-113-trip",
    "vl80s.diag.oil-pump-failure",
}
def req(ok, message):
    if not ok:
        raise AssertionError(message)

def validate(c, inv):
    source = {x["id"]: x for x in inv["scenarios"]}
    req(inv["scenarioCount"] == 103 and "aux-machines" in source, "donor count/id")
    d = source["aux-machines"]
    req(c["scenarioId"] == "vl80s.diag.aux-machines"
        and c["originalId"] == "aux-machines", "original ID")
    req(c["title"] == d["title"] and c["category"] == d["category"], "donor title/category")
    req(c["authoringProfileId"] == "vl80s-general"
        and d["applicableVariantIds"] == ["vl80s-general"], "profile")
    req(c["donorPinnedSha"] == PIN and c["donorOriginalBlobSha"] == BLOB, "pinned donor")
    req(c["donorOriginLayer"] == "DiagnosticRepository.kt", "origin layer")
    req(c["donorOriginalQuestions"] == QUESTIONS, "verbatim donor questions")
    req(set(c["mustRemainDistinctFrom"]) == BOUNDARIES, "distinct source IDs")
    req(c["publicationStatus"] == "CANDIDATE", "publication")
    for key in ("runtimeImport", "executable", "actionAuthorityGranted",
                "sourceAuthorityVerified", "exactInstalledVariantConfirmed",
                "substantiveSafetyReviewed"):
        req(c[key] is False, "authority " + key)
    req(c["exactInstalledVariant"] == "UNKNOWN"
        and c["unknownVariantDisposition"] == "BLOCKED", "variant")
    policy = c["safePolicy"]
    req(policy["observationOnly"] is True and policy["onlyPreviouslyRecorded"] is True, "recorded-only")
    req(policy["triState"] == ["YES", "NO", "UNKNOWN"]
        and policy["unknownMustStop"] is True and policy["unknownProfile"] == "BLOCKED"
        and policy["operationsAllowed"] == [], "policy fail-closed")
    gate = c["warningGate"]
    req(gate == {"default": "HIDDEN", "extendedEnabled": True,
                 "warningReadToEnd": True, "warningAcknowledged": True,
                 "warningGrantsActionAuthority": False}, "warning gate")
    sources = c["sourceRecords"]
    req(sources["donor"]["blobSha"] == BLOB and sources["donor"]["commit"] == PIN
        and sources["donor"]["originalQuestions"] == QUESTIONS
        and sources["donor"]["proceduresImported"] is False, "donor provenance")
    req(sources["donorSnapshot"]["blobSha"] == inv["sourceSnapshot"]["blobSha"]
        and sources["donorSnapshot"]["commit"] == PIN, "snapshot provenance")
    req(len(sources["manual1990"]["verifiedLocators"]) >= 4
        and sources["manual1990"]["currentOperatingAuthority"] is False
        and sources["manual1990"]["proceduresImported"] is False, "manual provenance")
    req(sources["practical2015"]["originalEditionIndependentlyVerified"] is False
        and sources["practical2015"]["currentOperatingAuthority"] is False, "practical provenance")
    req(sources["currentRequirements"]["status"] == "UNKNOWN"
        and sources["currentRequirements"]["actionAuthorityGranted"] is False, "modern authority")
    req(len(c["historicalEvidenceClaims"]) == 5, "claims")
    for claim in c["historicalEvidenceClaims"]:
        req(claim["sourceId"] in sources and claim["locator"]
            and claim["provesCurrentEquipment"] is False
            and claim["provesFaultCause"] is False
            and claim["authorizesAction"] is False, "claim authority")
    counts = []
    for mode, size in (("SHORT", 6), ("DETAILED", 12)):
        route = c["versions"][mode]
        nodes = route["nodes"]
        ids = {n["id"]: n for n in nodes}
        req(len(nodes) == size and len(ids) == size, "node count/IDs")
        req(route["operatingInstructionsIncluded"] is False
            and route["authoringStatus"] == "RESEARCH_DRAFT_BLOCKED", "version gate")
        seen, stack = set(), [route["startNodeId"]]
        while stack:
            node_id = stack.pop()
            req(node_id in ids, "missing edge")
            if node_id in seen:
                continue
            seen.add(node_id)
            n = ids[node_id]
            req(n["recordedOnly"] is True and n["operationRequested"] is False
                and n["causeConfirmed"] is False, "node operation/claim")
            req(n["sourceRefs"] and set(n["sourceRefs"]) <= set(sources), "node source")
            if n["type"] == "QUESTION":
                e = n["responses"]
                req(set(e) == {"YES", "NO", "UNKNOWN"}, "tri-state edges")
                req(ids.get(e["UNKNOWN"], {}).get("type") == "STOP", "UNKNOWN must STOP")
                stack.extend(e.values())
            else:
                req(n["type"] in {"STOP", "OBSERVATION_REPORT"} and n["responses"] == {}, "leaf")
        req(seen == set(ids), "unreachable")
        counts.append(len(nodes))
    extensions = c["informationExtensions"]
    req(len(extensions) == 5 and len({e["id"] for e in extensions}) == 5, "extensions")
    req([e["version"] for e in extensions] == ["SHORT", "SHORT", "DETAILED", "DETAILED", "DETAILED"], "extension version")
    req({e["sourceRefs"][0] for e in extensions} == {"donor", "manual1990", "practical2015"}, "source alternatives")
    for e in extensions:
        req(len(e["sourceRefs"]) == 1 and e["sourceRefs"][0] in sources
            and e["locator"] and e["text"], "extension provenance")
        req(e["warningRequired"] is True and e["actionAuthorityGranted"] is False
            and e["executable"] is False and e["operationalSteps"] == [], "extension no-action")
        req(e["visibility"] == gate
            and e["applicability"]["exactEquipmentProfileConfirmed"] is False
            and e["applicability"]["modernSchemeConfirmed"] is False, "extension gate")
    req(c["deviceQA"] == "DEFERRED_TO_POST_RELEASE_DEVICE_QA", "device QA")
    return counts + [len(extensions)]

def negatives(c, inv):
    # Mutations intentionally target different trust, graph, and authority gates.
    changes = [
        ("publication", lambda x: x.update(publicationStatus="ACTIVE")),
        ("runtime", lambda x: x.update(runtimeImport=True)),
        ("executable", lambda x: x.update(executable=True)),
        ("authority", lambda x: x.update(actionAuthorityGranted=True)),
        ("source_authority", lambda x: x.update(sourceAuthorityVerified=True)),
        ("variant_verified", lambda x: x.update(exactInstalledVariantConfirmed=True)),
        ("safety_review", lambda x: x.update(substantiveSafetyReviewed=True)),
        ("donor_pin", lambda x: x.update(donorPinnedSha="unverified")),
        ("donor_blob", lambda x: x.update(donorOriginalBlobSha="unverified")),
        ("wrong_id", lambda x: x.update(originalId="phase-splitter-no-start")),
        ("wrong_title", lambda x: x.update(title="Выдуманное название")),
        ("wrong_profile", lambda x: x.update(authoringProfileId="unknown-profile")),
        ("wrong_variant", lambda x: x.update(exactInstalledVariant="CONFIRMED")),
        ("wrong_variant_disposition", lambda x: x.update(unknownVariantDisposition="ALLOWED")),
        ("questions", lambda x: x["donorOriginalQuestions"].pop()),
        ("boundary", lambda x: x["mustRemainDistinctFrom"].pop()),
        ("policy_operations", lambda x: x["safePolicy"]["operationsAllowed"].append("switch")),
        ("policy_unknown", lambda x: x["safePolicy"].update(unknownMustStop=False)),
        ("policy_profile", lambda x: x["safePolicy"].update(unknownProfile="ALLOWED")),
        ("policy_record", lambda x: x["safePolicy"].update(onlyPreviouslyRecorded=False)),
        ("warning_visible", lambda x: x["warningGate"].update(default="VISIBLE")),
        ("warning_scroll", lambda x: x["warningGate"].update(warningReadToEnd=False)),
        ("warning_ack", lambda x: x["warningGate"].update(warningAcknowledged=False)),
        ("warning_authority", lambda x: x["warningGate"].update(warningGrantsActionAuthority=True)),
        ("manual_authority", lambda x: x["sourceRecords"]["manual1990"].update(currentOperatingAuthority=True)),
        ("practical_authority", lambda x: x["sourceRecords"]["practical2015"].update(currentOperatingAuthority=True)),
        ("donor_questions", lambda x: x["sourceRecords"]["donor"]["originalQuestions"].pop()),
        ("claim_authority", lambda x: x["historicalEvidenceClaims"][0].update(authorizesAction=True)),
        ("short_operation", lambda x: x["versions"]["SHORT"]["nodes"][0].update(operationRequested=True)),
        ("detailed_record", lambda x: x["versions"]["DETAILED"]["nodes"][0].update(recordedOnly=False)),
        ("unknown_edge", lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="report-classified")),
        ("missing_edge", lambda x: x["versions"]["DETAILED"]["nodes"][0]["responses"].pop("NO")),
        ("unreachable", lambda x: x["versions"]["DETAILED"]["nodes"][1]["responses"].update(YES="q-individual")),
        ("extension_authority", lambda x: x["informationExtensions"][0].update(actionAuthorityGranted=True)),
        ("extension_warning", lambda x: x["informationExtensions"][1].update(warningRequired=False)),
        ("extension_provenance", lambda x: x["informationExtensions"][2].update(sourceRefs=["fake"])),
        ("extension_count", lambda x: x["informationExtensions"].pop()),
        ("device_pass", lambda x: x.update(deviceQA="PASS")),
    ]
    for name, change in changes:
        altered = copy.deepcopy(c)
        change(altered)
        try:
            validate(altered, inv)
        except AssertionError:
            continue
        raise AssertionError("negative mutation escaped: " + name)
    return len(changes)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    req(len(doc["candidates"]) == 1 and doc["ledger"]["publicationStatus"] == "CANDIDATE", "ledger")
    c = doc["candidates"][0]
    counts = validate(c, inv)
    print("STAGE17_AUX_MACHINES_PASS original=aux-machines nodes=%s extensions=5 source/role/safety=BLOCKED" % counts)
    if args.negative:
        n = negatives(c, inv)
        print("STAGE17_AUX_MACHINES_NEGATIVE_PASS %d" % n)
    print("CANDIDATE_ONLY: no runtime authority, device QA deferred")
if __name__ == "__main__":
    main()
