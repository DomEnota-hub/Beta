#!/usr/bin/env python3
"""Validate pinned Common knowledge/safety packs without publication authority."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

PACKS={
    "knowledge":("content-packs/common/knowledge/articles.pack.json",
                 "e57d8be5431ccb25cb69e792005dfed3480debd9eb9fc7b70108fdfc0ebfb65f",45),
    "safety":("content-packs/common/safety/articles.pack.json",
              "b91fa3b2b882b469b51cc2f5d799044e8589bbeb6993bfc0fe8dfdaf0c23e91c",22),
}
PINS={"KnowledgeRepository.gitBlob":"b37ead2d66c0c976bcc850f9cde4fddc0e198fb3",
      "KnowledgeFirstWave.gitBlob":"b12651f2e4dde65e0b5f50277c8928a97809afdd"}

def validate(docs):
    entries=[e for pack in docs.values() for e in pack["entries"]]
    ids={e["id"]:e for e in entries}
    assert len(entries)==len(ids)==67
    assert sum(e["type"]=="SOURCE" for e in entries)==19
    assert sum(e["type"]=="KNOWLEDGE" for e in entries)==26
    assert sum(e["type"]=="SAFETY" for e in entries)==22
    for kind,d in docs.items():
        m=d["manifest"]
        assert m["packId"]==f"common.{kind}.articles-001"
        assert m["modelIds"]==[] and m["variantIds"]==[]
        assert m["checksums"]==PINS
        assert m["entries"]==[e["id"] for e in d["entries"]]
        for e in d["entries"]:
            assert e["owner"]=={"kind":"COMMON"}
            assert e["publicationStatus"]=="CANDIDATE"
            assert e["sourceStatus"]=="UNKNOWN"
            assert e["provenance"]=="UNKNOWN"
            assert e["actionDisposition"]=="INFORMATION_ONLY"
            if e["type"]!="SOURCE":
                assert e["details"] and len(e["blocks"])==3
                assert e["blocks"][2]["lines"][2] in PINS.values()
                assert len(e["sourceRefs"])==1
            for link in e["links"]:
                target=ids[link["targetId"]]
                assert link["scope"]=="COMMON_INTERNAL"
                assert link["type"]==target["type"]
    assert ids["common.knowledge.appendix12"]["publicationStatus"]=="CANDIDATE"
    assert ids["common.safety.safety-electrical"]["publicationStatus"]=="CANDIDATE"

def negative_cases(docs):
    for change in (
        lambda q: q["knowledge"]["entries"][0].update(publicationStatus="ACTIVE"),
        lambda q: q["safety"]["entries"][0].update(owner={"kind":"MODEL","modelId":"vl80s"}),
        lambda q: q["knowledge"]["entries"][0]["links"][0].update(targetId="vl80s.source.foreign"),
    ):
        q=copy.deepcopy(docs);change(q)
        try:validate(q)
        except (AssertionError,KeyError):pass
        else:raise AssertionError("unsafe Common mutation accepted")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path("."))
    parser.add_argument("--verify-pinned-output",action="store_true")
    args=parser.parse_args()
    docs={}
    for kind,(path,sha,count) in PACKS.items():
        raw=(args.root/path).read_bytes()
        docs[kind]=json.loads(raw)
        assert len(docs[kind]["entries"])==count
        if args.verify_pinned_output:
            assert hashlib.sha256(raw).hexdigest()==sha
    validate(docs);negative_cases(docs)
    print("COMMON_KNOWLEDGE_SAFETY_STRUCTURE_PASS",len(docs["knowledge"]["entries"]),len(docs["safety"]["entries"]))

if __name__=="__main__":main()
