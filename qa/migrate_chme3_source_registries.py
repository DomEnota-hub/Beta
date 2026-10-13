#!/usr/bin/env python3
"""Preserve pinned registries and resolve Notik bibliography/material identities."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

DEST = Path("content-packs/diesel/chme3-family/migration/source-registry-index.json")
PINS = {
    "docs/locomotives/chme3/acceptance_source_registry_addendum.json": "8ce0ae39a92f649fa2a34cda2d6c050f11b17769",
    "docs/locomotives/chme3/diagnostic_source_registry_addendum.json": "be74b1b6b3082a7962a30cf6e8a5c877be7cacac",
    "docs/locomotives/chme3/source_registry.json": "e4aa3273316358bcc2692a70768e6f067a7bd14c",
    "docs/locomotives/chme3/source_registry_addendum_atlas.json": "0530baec0f0180ef92c65943197579bf6f478c03",
    "docs/locomotives/diesel/chme3-family/chme3e/source_registry.json": "f95f8fa25a3331b7ad015da2c426bf1ceda3085f",
    "docs/locomotives/diesel/chme3-family/chme3e/source_registry_stage2.json": "ebd2cbd10543bc112ae141f3dfef52ed01dbcab0",
}

NOTIK = "CHME3-SRC-NOTIK-1996"
NOTIK_MATERIALS = (
    ("docs/locomotives/chme3/source_registry.json", "/sources/2",
     "CHME3-MAT-NOTIK-1996-SCHEME-INSERT", "SCHEME_INSERT",
     "https://zdsim.com/library/116/vkladysh_teplovozy_chmeh3_chmeh3t_chmeh3eh_notik_1"),
    ("docs/locomotives/diesel/chme3-family/chme3e/source_registry.json", "/sources/0",
     "CHME3-MAT-NOTIK-1996-BOOK", "FULL_EDITION_LISTING",
     "https://scbist.com/kachegaroff-line/books/pages/ISBN_5-277-01904-9.HTML"),
)


def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_pinned(root, path, sha):
    raw = (root / path).read_bytes()
    if blob_sha(raw) != sha and raw.endswith(b"\n"):
        raw = raw[:-1]  # Retrieval added one transport newline to some donor files.
    assert blob_sha(raw) == sha, path
    return json.loads(raw)


def build(donor_root):
    documents = []
    occurrences = defaultdict(list)
    for path, sha in PINS.items():
        obj = read_pinned(donor_root, path, sha)
        assert isinstance(obj, dict) and isinstance(obj.get("sources"), list), path
        documents.append({"sourcePath": path, "sourceBlobSha": sha, "sourceObject": obj})
        for i, source in enumerate(obj["sources"]):
            assert isinstance(source.get("id"), str) and source["id"], (path, i)
            occurrences[source["id"]].append({"sourcePath": path, "sourcePointer": f"/sources/{i}"})
    duplicates = [{"sourceId": key, "occurrences": value} for key, value in sorted(occurrences.items()) if len(value) > 1]
    assert [d["sourceId"] for d in duplicates] == [NOTIK]
    source_by_path = {d["sourcePath"]: d["sourceObject"] for d in documents}
    materials = []
    for path, pointer, material_id, role, url in NOTIK_MATERIALS:
        record = source_by_path[path]["sources"][int(pointer.rsplit("/", 1)[1])]
        assert record["id"] == NOTIK and record["url"] == url
        assert record["title"] == "Тепловозы ЧМЭ3, ЧМЭ3Т, ЧМЭ3Э. Пособие машинисту, 2-е изд."
        assert record.get("author", record.get("authors")) in ("З. Х. Нотик", ["З. Х. Нотик"])
        assert record["year"] == 1996 and record["kind"] == "TRAINING"
        assert record["authorityForAction"] == "NO_BY_ITSELF"
        materials.append({"materialId": material_id, "materialRole": role,
                          "bibliographicSourceId": NOTIK, "sourcePath": path,
                          "sourcePointer": pointer, "url": url,
                          "binaryContentVerified": False})
    assert len({m["materialId"] for m in materials}) == len(materials) == 2
    assert duplicates[0]["occurrences"] == [
        {"sourcePath": m["sourcePath"], "sourcePointer": m["sourcePointer"]}
        for m in materials]
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
            "runtimeImport": False, "sourceIdPolicy": "BIBLIOGRAPHIC_ID_WITH_DISTINCT_MATERIAL_IDS",
            "sourceRecordOccurrences": sum(map(len, occurrences.values())),
            "distinctSourceIds": len(occurrences), "duplicateSourceIds": duplicates,
            "unresolvedDuplicateSourceIds": [],
            "identityResolution": {"bibliographicSourceId": NOTIK,
                                   "author": "З. Х. Нотик", "edition": "2-е, переработанное и дополненное",
                                   "publisher": "Транспорт", "year": 1996,
                                   "isbn": "5-277-01904-9", "kind": "TRAINING",
                                   "authorityForAction": "NO_BY_ITSELF",
                                   "materials": materials},
            "documents": documents}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root), ensure_ascii=False, separators=(",", ":")) + "\n")
    print("CHME3_SOURCE_REGISTRIES", len(PINS))
