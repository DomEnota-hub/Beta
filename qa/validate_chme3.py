#!/usr/bin/env python3
"""Validate exact CHME3 family variant isolation and source accounting."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

from migrate_chme3 import PINS, ROOT, VARIANTS, build, read_assets

OUTPUT_SHA256 = {
    "diagnostics-01.pack.json": "85658ef1cb10f09298014bfabae15814580e5a2c04c4ebc5c2cb09e5e4a5f66f",
    "diagnostics-02.pack.json": "923c4657728c9d0a2db84fd8069ab956d789e4dd8093fcf71a1c1bbd13dfcce8",
    "diagnostics-03.pack.json": "87c52bb3fda4901a04acd38d3e16a640c8ce175dfc65512e38a66157402b12e1",
    "diagnostics-04.pack.json": "125275c934f978ea2bc0c59163b2e0c3178e7af94683ae0b16783967030dde90",
    "catalog-01.pack.json": "5bf9d43b34ed5da8577c5a8779a5b01dd5f80f577feaf72d641739b3d50a2740",
    "catalog-02.pack.json": "df145f7dce8369bb6eb1f8092255b72611fe196b5bae89a6f9deeefcccb0b8f4",
    "catalog-03.pack.json": "9c7452ece8383a7905c1e026bfd19cdf03bd910b2826fef9d3a747b804ccf161",
    "catalog-04.pack.json": "939dc817b4136062e7d4bfc238e93dec6bab0895aa6dd2690e2d1158b107f8b1",
    "catalog-05.pack.json": "a9ae849f758fa4cd9c9db66168067465c014c6cc6bb5bc0332b1956c67cce7be",
    "catalog-06.pack.json": "aee6af281077630d4fc39ad6f068682bd82868f8cc091c8e3f719c54e332b4f3",
    "catalog-07.pack.json": "178a064947444ad433f17a81423bd3d89b58e905140db922ff3a0edccc6617f2",
    "catalog-08.pack.json": "4a2ea783b9199708a1e189fb11fa9e77fca5de6657798c713fcc0b11b501699d",
    "catalog-09.pack.json": "f40b0d16595188cccead46f5e3883e6af998f80713addbea9a967ce403e45b97",
    "catalog-10.pack.json": "c1d218a7a5b57408453738e2cf7b980cadb80ebe535e4590598c84a85175a879",
    "catalog-11.pack.json": "054a3ac1f19ba4146210bcdf07e492cd77635ff45776b7c47acfb93196e70d7f",
    "catalog-12.pack.json": "d31803f2c3f800b45d06432c408760be7206867013c82161abe0b2ab7b304e5a",
    "catalog-13.pack.json": "2f7cb8a6d8e5102875b3b9afa203b829ff57d0d135a53e67db10240c7a1d5a89",
    "catalog-14.pack.json": "a639a44c6b244c4697ac2ecabfee929841192e284ae45d5ea12fcc7757d82c79",
    "catalog-15.pack.json": "07690c173b5c615d300096ff6178a7facad4b8e9a8f165d72cfa9fa11910db91",
    "catalog-16.pack.json": "f0e5c33a6f26790ef9ed4830e1d1c6b4d0a00c6a068c3a674d967d930b50f7b2",
    "catalog-17.pack.json": "80a3db80f39e4b0d11196240ab683a536a8875f6519cdac9e3f8fd2f0798b9b3",
    "catalog-18.pack.json": "6d69002c8e1e1f7b2eb284423ef56b83c21c0c5ec1e2b34b42ddf3e84b27eb4b",
    "catalog-19.pack.json": "71cd1022141bda4b6d4aa97b3f811a7a4230424bbcb6da98f3dd20675e5dcc3e",
    "catalog-20.pack.json": "4af711dd4384787126833c6da13eb2f661965ac3bfe907e89c790f1057c72c05",
    "catalog-21.pack.json": "e4e0978744ef563d93131ce459a92589d85c129fa75eac378d4c952125329046",
    "catalog-22.pack.json": "9069e065496922ce086804b20482daaa5e6c4ccc2eb404edacefb217f346522a",
    "catalog-23.pack.json": "15538ae65f50664977ae788c5ea55adf2d16ceea0a9e6bf49be7c4b1dda1f496",
    "catalog-24.pack.json": "7a632ccb6ec829eba5c57cbf0f077a91da3243d8f1f821a4ce37b78f7125c95d",
    "catalog-25.pack.json": "ab651da749bbddf2e70a04c0513ffd2a2e581995d856047c951c80adbac3c099",
    "catalog-26.pack.json": "70090f9b028c86c218577b45db4abaedd420bb4043bc5d6ec9549df6240d97a0",
    "catalog-27.pack.json": "e6d956f5cfd96471c21495830c973a9ef039548780799fdaf9413dadf24ad13d",
    "catalog-28.pack.json": "0dfc0b63426dda545403836044e9767e271aaae90584228d0afbcc2968cc1b2f",
    "catalog-29.pack.json": "9b9c2f3d948288832a4dd263a1fbc51b272d68b296c90c5549eb7a4ce812bc8d",
    "catalog-30.pack.json": "ade4cd55ed25555e2ad4fb40ff75224f6cddf9bd36e9e6718b58aea62027e38d",
    "catalog-31.pack.json": "b75ee21aa11460fe0fab8bae199900a3741f749d3a7493c54b26c95f616220ee",
    "catalog-32.pack.json": "5d6359581f842a6216335a3435c0bed0230aaba0856d5aed7f766d27654d54fd",
    "catalog-33.pack.json": "feaba1a3aa632fb23507d0c61a85b18c9b8e83b3fe060431af98a795aee86342",
    "catalog-34.pack.json": "39108204220b3be345ee98ebfe4403ab9d7c58cc16cf6dab19bcdacf9e936824",
}
COUNTS = {"chme3.catalog":306,"chme3.diagnostics":55,
          "chme3t.catalog":319,"chme3t.diagnostics":56,
          "chme3e.catalog":428,"chme3e.diagnostics":67}


def validate(root, donor_dir=None):
    groups={}
    entries=[]
    for kind, relative, count in (("catalog","technical-data/catalog",670),
                                  ("diagnostics","diagnostics/recommended",68)):
        paths=sorted((root/ROOT/relative).glob(f"{kind}-*.pack.json"))
        assert len(paths)==(count+19)//20
        group=[]
        for p in paths:
            assert hashlib.sha256(p.read_bytes()).hexdigest()==OUTPUT_SHA256[p.name]
            pack=json.loads(p.read_text())
            m=pack["manifest"]
            assert m["entries"]==[e["id"] for e in pack["entries"]]
            assert m["modelIds"]==["chme3-family"]
            assert m["variantIds"]==sorted({v for e in pack["entries"]
                                             for v in e["applicability"]["variantIds"]})
            assert m["checksums"]=={f"{v}.{kind}.gitBlob":PINS[(v,kind)] for v in VARIANTS}
            group+=pack["entries"]
        assert len(group)==count
        groups[kind]=group
        entries+=group
    ids={e["id"]:e for e in entries}
    assert len(ids)==len(entries)==738
    links=0
    for e in entries:
        assert e["owner"]=={"kind":"MODEL","modelId":"chme3-family"}
        assert e["publicationStatus"]=="CANDIDATE"
        assert e["actionDisposition"]=="INFORMATION_ONLY"
        assert e["provenance"]==e["sourceStatus"]=="UNKNOWN"
        assert e["applicability"]["modelIds"]==["chme3-family"]
        variants=set(e["applicability"]["variantIds"])
        assert variants and variants <= set(VARIANTS)
        source=e["sourceObject"]
        assert source["sourceBlobSha"] in PINS.values()
        assert source["object"]["id"].lower() in e["id"]
        for l in e["links"]:
            links+=1
            target=ids[l["targetId"]]
            edge_variant,=l["applicability"]["variantIds"]
            assert edge_variant in variants
            assert edge_variant in target["applicability"]["variantIds"]
            assert l["type"]=={"DIAGNOSTIC_SCENARIO":"RELATED_SCENARIO"}.get(target["type"],target["type"])
    assert links==5421
    nodes=branches=0
    for e in groups["diagnostics"]:
        graph=e["sourceObject"]["object"]["graph"]
        ns=graph["nodes"]
        node_ids={n["id"] for n in ns}
        assert len(node_ids)==len(ns) and graph["startNodeId"] in node_ids
        nodes+=len(ns)
        for n in ns:
            for choice in n.get("choices",[]):
                branches+=1
                assert choice.get("nextNodeId") in node_ids or choice.get("nextScenarioId")
    assert (nodes,branches)==(898,639)
    audit=json.loads((root/ROOT/"migration/source-audit.json").read_text())
    assert audit["sourceCounts"]==COUNTS
    assert audit["canonicalCounts"]=={"catalog":670,"diagnostics":68}
    assert len(audit["mappings"])==1231
    assert collections.Counter(m["disposition"] for m in audit["mappings"])=={
        "MIGRATED":738,"MERGED_WITH_CANONICAL":493}
    assert len(audit["unresolvedReferences"])==610
    assert audit["linkCount"]==5421
    for m in audit["mappings"]:
        e=ids[m["canonicalId"]]
        assert m["variant"] in e["applicability"]["variantIds"]
        assert m["gitBlob"]==PINS[(m["variant"],m["sourceKind"])]
    if donor_dir:
        arrays=read_assets(donor_dir)
        for m in audit["mappings"]:
            original=arrays[(m["variant"],m["sourceKind"])][m["sourceIndex"]]
            assert original==ids[m["canonicalId"]]["sourceObject"]["object"]
        for p,content in build(donor_dir).items():
            assert (root/p).read_text()==content,p
    return groups


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--donor-dir",type=Path)
    a=p.parse_args()
    groups=validate(a.root,a.donor_dir)
    print("CHME3_VARIANT_ISOLATION_PASS",{k:len(v) for k,v in groups.items()})
