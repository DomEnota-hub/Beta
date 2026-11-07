#!/usr/bin/env python3
"""Relate the early CHME3 Atlas checkpoint to preserved source objects."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "content-packs/diesel/chme3-family/migration"
HISTORY = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
OUT = ROOT / "docs/data-migration/chme3-legacy-atlas-checkpoint-relations.json"
CHECKPOINT = "docs/locomotives/chme3/ATLAS_PASS_2_CHECKPOINT.md"
NOTES = "docs/locomotives/chme3/ATLAS_PASS_2_SOURCE_NOTES.md"
PREFIX = "docs/locomotives/chme3/"


def project():
    history = json.loads(HISTORY.read_text())
    documents = {d["sourcePath"]: d for d in history["documents"]}
    source_docs = {}
    for filename in ("atlas-source-index.json", "remaining-document-source-index.json"):
        index = json.loads((MIGRATION / filename).read_text())
        assert index["donorCommit"] == history["donorCommit"]
        for row in index["documents"]:
            assert row["sourcePath"] not in source_docs
            source_docs[row["sourcePath"]] = row
    registry = json.loads((MIGRATION / "source-registry-index.json").read_text())
    registry_docs = {d["sourcePath"]: d for d in registry["documents"]}

    def source(name):
        return source_docs[PREFIX + name]["sourceObject"]

    index = source("atlas_index.json")
    extension = source("atlas_index_extension.json")
    equipment = index["equipment"] + extension["equipment"]
    systems = index["systems"]
    card_names = ("atlas_cards_powerplant.json", "atlas_cards_running_auxiliary.json",
                  "atlas_cards_engine_control_remaining.json", "atlas_cards_electric_brake.json",
                  "atlas_cards_scheme_equipment.json")
    card_rows = [row for name in card_names for row in
                 source(name).get("records", source(name).get("equipment", []))]
    schemes = source("atlas_schemes_functional.json")["records"] + source("atlas_schemes_extension.json")["records"]
    designations = source("atlas_scheme_designations.json")
    bindings = designations["electrical"]["elements"] + designations["pneumatic"]["elements"]
    contract = source("atlas_id_contract.json")
    ids = {row["id"] for row in equipment}
    assert len(systems) == 13 and len(equipment) == len(ids) == 70
    assert len(card_rows) == len({row["id"] for row in card_rows}) == 70
    assert {row["id"] for row in card_rows} == ids
    assert len(schemes) == 12 and len(bindings) == 24
    assert len(contract["canonicalMappings"]) == 11
    assert {row["equipmentId"] for row in bindings} <= ids
    source_registry = registry_docs[PREFIX + "source_registry.json"]["sourceObject"]["sources"]
    atlas_addendum = registry_docs[PREFIX + "source_registry_addendum_atlas.json"]["sourceObject"]["sources"]
    assert len(source_registry) == 12 and len(atlas_addendum) == 4
    assert len({row["id"] for row in source_registry + atlas_addendum}) == 16

    aliases = {alias: mapping["canonical"] for mapping in contract["canonicalMappings"]
               for alias in mapping["aliases"]}
    assert aliases["CHME3-EQ-TRACTION-MOTOR"] == "CHME3-EQ-TRACTION-MOTORS"
    assert aliases["CHME3T-EQ-BRAKE-RESISTOR"] == "CHME3T-EQ-BRAKE-RESISTORS"
    assert aliases["CHME3-EQ-MAIN-CONTACTORS"] == "CHME3-EQ-TRAIN-CONTACTORS"
    assert "CHME3-EQ-CONTACTORS" in ids and "CHME3-EQ-TRAIN-CONTACTORS" in ids
    assert "CHME3-EQ-CONTACTORS" != aliases["CHME3-EQ-MAIN-CONTACTORS"]
    assert "CHME3-EQ-CONTACTORS" not in aliases
    edb = ("CHME3T-EQ-BRAKE-RESISTORS", "CHME3T-EQ-BRAKE-RESISTOR-FAN", "CHME3T-EQ-EDB-CONTROL")
    assert all(next(row for row in equipment if row["id"] == eid)["applicability"] == ["ЧМЭ3Т"] for eid in edb)
    for row in (documents[CHECKPOINT], documents[NOTES]):
        raw = row["exactSourceText"].encode()
        assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["sourceBlobSha"]
    checkpoint = documents[CHECKPOINT]["exactSourceText"]
    notes = documents[NOTES]["exactSourceText"]
    for phrase in ("16 зарегистрированных источников", "13 функциональных систем", "70 канонических ID",
                   "70 подробных карточек", "12 функциональных схем", "24 привязки"):
        assert phrase in checkpoint
    for phrase in ("TRACTION-MOTORS`/`TRACTION-MOTOR", "CONTACTORS`/`MAIN-CONTACTORS",
                   "BRAKE-RESISTORS`/`BRAKE-RESISTOR", "ЧМЭ3Т", "сам по себе не считается достаточным"):
        assert phrase in notes
    return {"schemaVersion": 1, "donorCommit": history["donorCommit"],
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "currentAuthorityVerified": False, "actionAuthorityGranted": False,
            "note": "The early Atlas checkpoint counts match preserved source objects. Its CONTACTORS/MAIN-CONTACTORS shorthand is not an identity merger: MAIN-CONTACTORS aliases TRAIN-CONTACTORS, while CONTACTORS is a distinct preserved equipment ID. Historical source descriptions do not prove present-day authority or execution applicability.",
            "checkpoint": {"path": CHECKPOINT, "blobSha": documents[CHECKPOINT]["sourceBlobSha"],
                           "textSha256": hashlib.sha256(checkpoint.encode()).hexdigest()},
            "sourceNotes": {"path": NOTES, "blobSha": documents[NOTES]["sourceBlobSha"],
                            "textSha256": hashlib.sha256(notes.encode()).hexdigest()},
            "counts": {"sourceRecords": 16, "systems": 13, "equipment": 70,
                       "detailCards": 70, "functionalSchemes": 12, "schemeDesignations": 24},
            "resolvedAliases": {key: aliases[key] for key in (
                "CHME3-EQ-TRACTION-MOTOR", "CHME3-EQ-MAIN-CONTACTORS",
                "CHME3T-EQ-BRAKE-RESISTOR")},
            "distinctEquipmentIds": ["CHME3-EQ-CONTACTORS", "CHME3-EQ-TRAIN-CONTACTORS"],
            "chme3tOnlyEquipmentIds": list(edb),
            "sourceIndexes": [str((MIGRATION / f).relative_to(ROOT)) for f in
                              ("atlas-source-index.json", "remaining-document-source-index.json",
                               "source-registry-index.json")]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.write_text(encoded)
    print("CHME3_LEGACY_ATLAS_CHECKPOINT_PASS 16 13 70 70 12 24")
