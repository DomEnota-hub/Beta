#!/usr/bin/env python3
"""TEM2/TEM2U source equivalence and variant isolation."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

from migrate_tem2 import PINS, ROOT, build, read_assets

OUTPUT_SHA256 = {
    "layouts-01.pack.json": "d79d5f0e0332d6b0c1c1083cad7b070902b995000b07fff1f667d20d4550d01b",
    "sequences-01.pack.json": "32ad5da16048eceae81f48cc3c5f62c24a4f3f0e91a6ac6b65b7779d21195d5d",
    "diagnostics-01.pack.json": "24f26e288912d8e067f8f25fd8c32ff5958f63f3d3e9d8d3f55b724a7d031de6",
    "diagnostics-02.pack.json": "f5a80b8c93f9b06d2c95066b4cc5f9596e2bd041717ac466c400dae0218fabf0",
    "catalog-01.pack.json": "0f5cd45d3b73a553feb05b2a1a911c00a5930031b9da2c80e0993f8e275cef0b",
    "catalog-02.pack.json": "f465ec02001788bf096af803ba14ccb896fda4aa984e7c5800b24d8ff89f9d3b",
    "catalog-03.pack.json": "b906370fb1eea57dae1aefa6701f77421d655e4a2f5a5fb8fb0e5ff89be70565",
    "catalog-04.pack.json": "2b2c1290502678eb07c52380ce24fdf66c9b1679c4343c3232ac77c149238bb5",
    "catalog-05.pack.json": "28c980170d60a53330c7d0bc38d7d9bbcfc4c4aafd07c8978904cf8443d3e5b2",
    "catalog-06.pack.json": "c6f7367f45ea6cb56cf9fae2d96500b85089d7b8975068175bee48c32ddbcd11",
    "catalog-07.pack.json": "d60a75644a4fb914c9a14298109bf5812e573094da1d76d37bad80ad7a0114dd",
    "catalog-08.pack.json": "8a30a520d545edd2e4963ce7f2b8a979a46dc706ea21edcec4e2485607d27ab4",
    "catalog-09.pack.json": "62c98210f7303e21616bda9c50c3426138991207373ff772e2b066f5dde4fedb",
    "catalog-10.pack.json": "bff5edd727fcbfd1549bcc56b8e2fa8a0fba6752e3664eaf70f0c4c9795f5d44",
    "catalog-11.pack.json": "8b89d6ef0c074937eedcc8789ba3bfc586c47a52f3718ab7c8defd7506fcdc6a",
    "catalog-12.pack.json": "c1c583cac0a18cf15366b92ea43533cbd33c767768dc9175caa69b59fa1bc36d",
    "catalog-13.pack.json": "993ebff8e6973e2571577179705ea1f1582d0e0621c13241e4f84b772fe33f7a",
}
COUNTS={"tem2.catalog":122,"tem2.diagnostics":22,
        "tem2u.catalog":131,"tem2u.diagnostics":24,
        "shared.layouts":17,"shared.sequences":17}
EXPECTED={"catalog":253,"diagnostics":33,"layouts":17,"sequences":17}
SUBDIRS={"catalog":"technical-data/catalog","diagnostics":"diagnostics/recommended",
         "layouts":"atlas/layouts","sequences":"atlas/sequences"}


def validate(root,donor_dir=None):
    entries=[];groups={}
    for kind,count in EXPECTED.items():
        paths=sorted((root/ROOT/SUBDIRS[kind]).glob(f"{kind}-*.pack.json"))
        assert len(paths)==(count+19)//20
        group=[]
        for p in paths:
            assert hashlib.sha256(p.read_bytes()).hexdigest()==OUTPUT_SHA256[p.name]
            pack=json.loads(p.read_text());m=pack["manifest"]
            assert m["modelIds"]==["tem2-family"]
            assert m["entries"]==[e["id"] for e in pack["entries"]]
            assert m["variantIds"]==sorted({v for e in pack["entries"]
                                             for v in e["applicability"]["variantIds"]})
            assert m["checksums"]=={f"{v}.{k}.gitBlob":sha for (v,k),sha in PINS.items() if k==kind}
            group+=pack["entries"]
        assert len(group)==count
        groups[kind]=group;entries+=group
    ids={e["id"]:e for e in entries}
    assert len(ids)==len(entries)==320
    links=0
    for e in entries:
        assert e["owner"]=={"kind":"MODEL","modelId":"tem2-family"}
        assert e["publicationStatus"]=="CANDIDATE"
        assert e["provenance"]==e["sourceStatus"]=="UNKNOWN"
        assert e["actionDisposition"]=="INFORMATION_ONLY"
        assert e["applicability"]["modelIds"]==["tem2-family"]
        variants=set(e["applicability"]["variantIds"])
        assert variants and variants <= {"tem2","tem2u"}
        assert e["sourceObject"]["sourceBlobSha"] in PINS.values()
        assert all(isinstance(ref, str) for ref in e.get("sourceRefs", []))
        for link in e["links"]:
            links+=1
            target=ids[link["targetId"]]
            edge_variant,=link["applicability"]["variantIds"]
            assert edge_variant in variants and edge_variant in target["applicability"]["variantIds"]
            assert link["type"]=={"DIAGNOSTIC_SCENARIO":"RELATED_SCENARIO"}.get(
                target["type"],target["type"])
    assert links==1073
    nodes=choices=0
    for e in groups["diagnostics"]:
        graph=e["sourceObject"]["object"]["graph"]
        ns=graph["nodes"];node_ids={n["id"] for n in ns}
        assert len(node_ids)==len(ns) and graph["startNodeId"] in node_ids
        nodes+=len(ns)
        for n in ns:
            for choice in n.get("choices",[]):
                choices+=1
                assert choice.get("nextNodeId") in node_ids or choice.get("nextScenarioId")
    assert (nodes,choices)==(151,99)
    audit=json.loads((root/ROOT/"migration/source-audit.json").read_text())
    assert audit["sourceCounts"]==COUNTS
    assert audit["canonicalCounts"]==EXPECTED
    assert len(audit["mappings"])==333
    assert collections.Counter(m["disposition"] for m in audit["mappings"])=={
        "MIGRATED":320,"MERGED_WITH_CANONICAL":13}
    assert audit["unresolvedReferences"]==[] and audit["linkCount"]==1073
    assert audit["layoutPolicy"].startswith("training geometry")
    if donor_dir:
        arrays=read_assets(donor_dir)
        for m in audit["mappings"]:
            source_variant=m["variant"] if m["sourceKind"] in ("catalog","diagnostics") else "shared"
            original=arrays[(source_variant,m["sourceKind"])][m["sourceIndex"]]
            assert original==ids[m["canonicalId"]]["sourceObject"]["object"]
        for p,content in build(donor_dir).items():
            assert (root/p).read_text()==content,p
    return groups


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--donor-dir",type=Path);a=p.parse_args()
    groups=validate(a.root,a.donor_dir)
    print("TEM2_VARIANT_AND_SCHEME_PASS",{k:len(v) for k,v in groups.items()})
