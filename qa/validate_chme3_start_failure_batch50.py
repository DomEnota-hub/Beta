#!/usr/bin/env python3
"""CHME3-DIAG-001 research-only graph and source safety gate."""
import argparse, copy, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = "content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-001-start-failure.research.json"
I = "content-packs/diesel/chme3-family/migration/diagnostic-source-index.json"
K = "content-packs/diesel/chme3-family/diagnostics/recommended/diagnostics-01.pack.json"
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
def load(p): return json.loads((ROOT / p).read_text(encoding="utf-8"))
def check(c,i,k):
    assert c["originalId"] == "CHME3-DIAG-001"
    assert c["scenarioId"] == "chme3.diagnostics.chme3-diag-001"
    assert c["donor"]["commit"] == i["donorCommit"] == PIN
    assert c["donor"]["documentBlob"] == "63988703bb795e82f40335a756b8b9bd3cad8e0a"
    assert c["donor"]["documentPointer"] == "/scenarios/0"
    assert c["donor"]["gzipIndependentlyDecoded"] is False
    assert c["donor"]["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    doc = next(x for x in i["documents"] if x["sourcePath"] == c["donor"]["documentPath"])
    assert doc["sourceBlobSha"] == c["donor"]["documentBlob"]
    src = doc["sourceObject"]["scenarios"][0]
    assert (src["id"],src["title"],src["riskClass"]) == (c["originalId"],c["title"],c["donor"]["riskClass"])
    assert src["equipmentIds"] == c["donor"]["equipmentIds"]
    assert src["evidenceRefs"] == c["donor"]["evidenceRefs"]
    assert src["profiles"] == ["ЧМЭ3","ЧМЭ3Т","ЧМЭ3Э"]
    match = next(x for x in i["matches"] if x["sourceId"] == c["originalId"])
    assert (match["canonicalId"],match["canonicalPack"]) == (c["scenarioId"],c["donor"]["canonicalPack"])
    entry = next(x for x in k["entries"] if x["id"] == c["scenarioId"])
    assert entry["title"] == c["title"] and entry["publicationStatus"] == "CANDIDATE"
    assert set(entry["applicability"]["variantIds"]) == set(c["applicability"]["possibleVariants"])
    assert c["applicability"]["confirmedVariant"] is None and c["applicability"]["installedSchemeVerified"] is False
    assert c["applicability"]["unknownProfile"] == "BLOCKED"
    assert c["publicationStatus"] == "CANDIDATE" and c["actionDisposition"] == "TRIAGE_ONLY_NO_REPAIR"
    for key in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"):
        assert c[key] is False
    assert c["warning"] == {"extendedHiddenByDefault":True,"readToEndRequired":True,"separateAcknowledgmentRequired":True,"grantsActionAuthority":False}
    assert all(x is False for x in c["safety"].values())
    assert len(c["sources"]) == 6 and all(s["currentVerified"] is False and s["installedProfileVerified"] is False for s in c["sources"])
    source_ids = {s["id"] for s in c["sources"]}
    assert len(source_ids) == 6
    def graph(nodes,start):
        lookup = {n["id"]:n for n in nodes}
        assert len(lookup) == len(nodes) and start in lookup
        seen=set(); todo=[start]
        while todo:
            key=todo.pop()
            assert key in lookup
            if key in seen: continue
            seen.add(key); n=lookup[key]
            assert n["permittedAction"] is False and set(n["sourceRefs"]) <= source_ids
            assert n["type"] in ("QUESTION","OBSERVATION_REPORT","STOP")
            if n["type"] == "QUESTION":
                assert set(n["responses"]) == {"YES","NO","UNKNOWN"}
                assert lookup[n["responses"]["UNKNOWN"]]["type"] == "STOP"
            else:
                assert n["responses"] == {} and n["causeConfirmed"] is False
            todo.extend(n["responses"].values())
        assert seen == set(lookup)
    assert len(c["versions"]["SHORT"]["nodes"]) == 8
    assert len(c["versions"]["DETAILED"]["nodes"]) == 12
    for v in c["versions"].values(): graph(v["nodes"],v["startNodeId"])
    assert len(c["extensions"]) == 5
    for e in c["extensions"]:
        assert e["sourceId"] in source_ids
        assert e["displayMode"] == "EXTENDED_ONLY"
        assert e["visibility"] == {"hiddenByDefault":True,"warningReadToEndRequired":True,"warningAcknowledgedRequired":True}
        assert e["actionDisposition"] == "INFORMATION_ONLY"
        assert e["executable"] is False and e["actionAuthorityGranted"] is False and e["procedureSteps"] == []
        graph(e["nodes"],e["nodes"][0]["id"])
def negatives(c,i,k):
    muts=[
        lambda x:x.update(runtimeImport=True),lambda x:x.update(executable=True),
        lambda x:x.update(actionAuthorityGranted=True),lambda x:x.update(publicationStatus="PUBLISHED"),
        lambda x:x["applicability"].update(confirmedVariant="chme3e"),
        lambda x:x["applicability"].update(unknownProfile="ALLOW"),
        lambda x:x["donor"].update(commit="HEAD"),
        lambda x:x["donor"].update(documentPointer="/scenarios/1"),
        lambda x:x["warning"].update(readToEndRequired=False),
        lambda x:x["warning"].update(grantsActionAuthority=True),
        lambda x:x["safety"].update(bypassProtection=True),
        lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s4"),
        lambda x:x["versions"]["DETAILED"]["nodes"][0]["responses"].update(YES="absent"),
        lambda x:x["extensions"][0].update(executable=True),
        lambda x:x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False)]
    for n,mut in enumerate(muts,1):
        changed=copy.deepcopy(c);mut(changed)
        try: check(changed,i,k)
        except (AssertionError,KeyError): continue
        raise AssertionError("negative mutation escaped: "+str(n))
    return len(muts)
if __name__ == "__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--negative",action="store_true");a=ap.parse_args()
    c,i,k=load(P),load(I),load(K);check(c,i,k);print("CHME3_001_PASS")
    if a.negative: print("CHME3_001_NEGATIVE_PASS",negatives(c,i,k))
