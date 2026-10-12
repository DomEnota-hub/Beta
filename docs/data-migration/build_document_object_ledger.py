#!/usr/bin/env python3
"""Inventory pinned donor locomotive documents at top-level logical object scope."""
import argparse
import hashlib
import json
from pathlib import Path

DONOR="3176d6ee228f0ed4b78371f45209e10c1c724eff"


def owner(path):
    value=path.as_posix()
    if "/chme3/" in value or "/chme3-family/" in value:
        return "chme3-family"
    if "/tem2-family/" in value:
        return "tem2-family"
    if "/ermak/" in value:
        return "ermak"
    if "/vl80s/" in value:
        return "vl80s"
    return "MIXED_REVIEW_REQUIRED"


def build(donor_root):
    tree={x["path"]:x for x in json.loads((donor_root/"donor-tree.json").read_text())}
    paths=sorted((donor_root/"docs/locomotives").rglob("*.json"))
    rows=[]
    for file in paths:
        relative=file.relative_to(donor_root).as_posix()
        raw=file.read_bytes()
        def blob_sha(data):
            return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        # Text retrieval added a single transport newline for 17 documents.
        if blob_sha(raw)!=tree[relative]["sha"] and raw.endswith(b"\n"):
            raw=raw[:-1]
        git_sha=blob_sha(raw)
        assert tree[relative]["sha"]==git_sha,relative
        doc=json.loads(raw)
        assert isinstance(doc,dict)
        for field,value in doc.items():
            items=(list(enumerate(value)) if isinstance(value,list) else
                   list(value.items()) if isinstance(value,dict) else [(None,value)])
            for index,item in items:
                pointer="/"+field.replace("~","~0").replace("/","~1")
                if index is not None:
                    pointer+="/"+str(index).replace("~","~0").replace("/","~1")
                canonical=json.dumps(item,sort_keys=True,ensure_ascii=False,separators=(",",":"))
                rows.append({
                    "ownerGuess":owner(Path(relative)),
                    "sourcePath":relative,
                    "sourceBlobSha":git_sha,
                    "sourcePointer":pointer,
                    "sourceId":item.get("id") if isinstance(item,dict) else None,
                    "jsonType":type(item).__name__,
                    "sha256":hashlib.sha256(canonical.encode()).hexdigest(),
                    "disposition":"PENDING_MAPPING",
                    "canonicalId":None,
                })
    return {"schemaVersion":1,"donorCommit":DONOR,"status":"OBJECT_DISCOVERY_PENDING_DISPOSITIONS",
            "files":len(paths),"objects":len(rows),"rows":rows}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--donor-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    ledger=build(a.donor_root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n")
    print("DOCUMENT_OBJECT_DISCOVERY",ledger["files"],ledger["objects"])
