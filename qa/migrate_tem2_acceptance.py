#!/usr/bin/env python3
"""Import pinned TEM2 Stage-4 acceptance observations without publishing rules."""
import hashlib
import json
from pathlib import Path

SOURCE="docs/locomotives/diesel/tem2-family/common/stage4_acceptance.json"
BLOB="2e3454b9e75141ff211918acab527ff228e56363"
ROOT=Path("content-packs/diesel/tem2-family")
PROFILE={"tem2-base":"tem2","tem2u-improved":"tem2u"}


def read_source(donor_root):
    raw=(donor_root/SOURCE).read_bytes()
    def git_blob(data):
        return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if git_blob(raw)!=BLOB and raw.endswith(b"\n"):
        raw=raw[:-1]
    assert git_blob(raw)==BLOB
    return json.loads(raw)


def build(donor_root, model_root):
    d=read_source(donor_root)
    audit=json.loads((model_root/ROOT/"migration/source-audit.json").read_text())
    lookup={(m["variant"],m["sourceKind"],m["sourceId"]):m["canonicalId"]
            for m in audit["mappings"]}
    entries=[];unresolved=[]
    for record in [*d["coreChecks"],*d["profileChecks"]]:
        variants=sorted({PROFILE[x] for x in record["profiles"]})
        links=[]
        for variant in variants:
            for field,kind,link_type in (("equipmentRefs","catalog","EQUIPMENT"),
                                          ("diagnosticRefs","diagnostics","RELATED_SCENARIO")):
                for target_id in record.get(field,[]):
                    target=lookup.get((variant,kind,target_id))
                    if target is None:
                        unresolved.append({"itemId":record["id"],"variant":variant,
                                           "field":field,"sourceTargetId":target_id})
                    else:
                        links.append({"type":link_type,"targetId":target,"role":field,
                                      "applicability":{"variantIds":[variant]}})
        entries.append({"id":"tem2.acceptance."+record["id"].lower(),
                        "type":"ACCEPTANCE_ITEM",
                        "owner":{"kind":"MODEL","modelId":"tem2-family"},
                        "applicability":{"modelIds":["tem2-family"],"variantIds":variants},
                        "layer":"STANDARD","publicationStatus":"CANDIDATE",
                        "provenance":"UNKNOWN","sourceStatus":"UNKNOWN",
                        "actionDisposition":"INFORMATION_ONLY",
                        "title":record["title"],"summary":record.get("observation"),
                        "sourceRefs":record.get("sourceRefs",[]),"links":links,
                        "sourceObject":{"sourcePath":SOURCE,"sourceBlobSha":BLOB,
                                        "object":record}})
    manifest={"schemaVersion":1,"packId":"tem2-family.acceptance.stage4",
              "packVersion":"0.1.0","family":"DIESEL","modelIds":["tem2-family"],
              "variantIds":["tem2","tem2u"],"locale":"ru-RU",
              "entries":[e["id"] for e in entries],"requiresRuntime":"1.1.0",
              "sourceCatalogVersion":"test-3176d6ee-tem2-stage4",
              "checksums":{"stage4_acceptance.json.gitBlob":BLOB}}
    route_index={"schemaVersion":1,"donorGitBlob":BLOB,"sourcePath":SOURCE,
                 "routes":[{"sourceObject":r,"canonicalId":"tem2.route."+r["id"].lower()}
                           for r in d["routes"]],
                 "rootMetadata":{k:v for k,v in d.items()
                                 if k not in ("coreChecks","profileChecks","routes")},
                 "unresolvedItemReferences":unresolved,
                 "publicationStatus":"CANDIDATE"}
    return {
        ROOT/"acceptance/items-stage4.pack.json":
            json.dumps({"manifest":manifest,"entries":entries},ensure_ascii=False,
                       separators=(",",":"))+"\n",
        ROOT/"acceptance/routes-stage4.json":
            json.dumps(route_index,ensure_ascii=False,separators=(",",":"))+"\n",
    }


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--donor-root",type=Path,required=True)
    p.add_argument("--model-root",type=Path,required=True)
    p.add_argument("--output-root",type=Path,default=Path("."));a=p.parse_args()
    outputs=build(a.donor_root,a.model_root)
    for path,content in outputs.items():
        target=a.output_root/path;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(content)
    print("TEM2_ACCEPTANCE_SOURCE",16,2)
