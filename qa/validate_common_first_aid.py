#!/usr/bin/env python3
"""Fail-closed structural gate for the first Common content migration."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

PACK = Path("content-packs/common/first-aid/topics.pack.json")
EXPECTED_IDS = (
    "unconscious","cpr","bleeding","nosebleed","airway","trauma",
    "chest_abdomen","burn","heat","electric","poisoning","chemical",
    "hypothermia","frostbite","bites","stress","seizure",
)
SOURCE_BLOB = "09587b2da7f23ac532755fd8aad4ced100d369fa"
PACK_SHA256 = "99e94a306290cb6d106d6be264c2dfbc079daa79e2e77576dd39066b9cd4ff40"
SOURCE_ID = "common.source.first-aid-donor"
KIT_SOURCE_ID = "common.source.worker-kit-262n-donor"

def validate(d):
    m=d["manifest"]
    assert m["packId"]=="common.first-aid.topics-001"
    assert m["modelIds"]==[] and m["variantIds"]==[]
    assert m["checksums"]["sourceGitBlob"]==SOURCE_BLOB
    entries=d["entries"]
    ids=[e["id"] for e in entries]
    assert ids==["common.first-aid."+x for x in EXPECTED_IDS]+[
        "common.first-aid.worker-kit",SOURCE_ID,KIT_SOURCE_ID]
    assert m["entries"]==ids and len(ids)==len(set(ids))
    for e in entries:
        assert e["owner"]=={"kind":"COMMON"}
        assert e["publicationStatus"]=="CANDIDATE"
        assert e["sourceStatus"]=="UNKNOWN"
        assert e["actionDisposition"]=="INFORMATION_ONLY"
        assert e["provenance"]=="UNKNOWN"
        if e["id"] in (SOURCE_ID,KIT_SOURCE_ID):
            assert e["type"]=="SOURCE"
            assert SOURCE_BLOB in e["details"][2]
        elif e["id"]=="common.first-aid.worker-kit":
            assert e["type"]=="FIRST_AID" and len(e["blocks"])==1
            assert len(e["blocks"][0]["lines"])==10
            assert e["sourceRefs"]==[KIT_SOURCE_ID]
            assert e["links"]==[{"type":"SOURCE","targetId":KIT_SOURCE_ID,"scope":"COMMON_INTERNAL"}]
        else:
            assert e["type"]=="FIRST_AID"
            assert len(e["blocks"])>=3
            assert [b["title"] for b in e["blocks"][:3]]==[
                "Когда применять","Действия — исходный текст, требует проверки",
                "Не делать — исходный текст, требует проверки"]
            assert all(isinstance(b["lines"],list) and b["lines"] for b in e["blocks"][:3])
            assert e["searchTerms"] and e["sourceRefs"]==[SOURCE_ID]
            assert e["links"]==[{"type":"SOURCE","targetId":SOURCE_ID,"scope":"COMMON_INTERNAL"}]
    assert ids.index("common.first-aid.hypothermia")!=ids.index("common.first-aid.frostbite")

def negative_cases(d):
    variants=[]
    q=copy.deepcopy(d);q["entries"][0]["publicationStatus"]="ACTIVE";variants.append(q)
    q=copy.deepcopy(d);q["entries"][0]["owner"]={"kind":"MODEL","modelId":"vl80s"};variants.append(q)
    q=copy.deepcopy(d);q["entries"][0]["links"][0]["targetId"]="missing";variants.append(q)
    q=copy.deepcopy(d);q["entries"][0]["blocks"][1]["lines"]=[];variants.append(q)
    q=copy.deepcopy(d);q["entries"][13]["id"]=q["entries"][12]["id"];variants.append(q)
    for q in variants:
        try: validate(q)
        except (AssertionError,KeyError): pass
        else: raise AssertionError("negative mutation accepted")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pack",type=Path,default=PACK)
    parser.add_argument("--verify-pinned-output",action="store_true")
    args=parser.parse_args()
    raw=args.pack.read_bytes()
    d=json.loads(raw)
    validate(d)
    negative_cases(d)
    if args.verify_pinned_output:
        assert hashlib.sha256(raw).hexdigest()==PACK_SHA256
    print("COMMON_FIRST_AID_STRUCTURE_PASS",len(d["entries"])-2)

if __name__=="__main__":main()
