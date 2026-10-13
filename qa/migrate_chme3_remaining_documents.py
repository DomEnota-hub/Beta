#!/usr/bin/env python3
"""Preserve remaining pinned CHME3 documents as closed source evidence."""
import argparse
import hashlib
import json
from pathlib import Path

DEST = Path("content-packs/diesel/chme3-family/migration/remaining-document-source-index.json")
PINS = {
    "docs/locomotives/chme3/atlas_id_contract.json": "370d66b72f913636f8fec66540b89ca52180a466",
    "docs/locomotives/chme3/atlas_scheme_designations.json": "401c04007c02c7fa12a1266e7b24d7244400e611",
    "docs/locomotives/chme3/atlas_schemes_extension.json": "9070839292255a28be68043d851d8f89e47948cc",
    "docs/locomotives/chme3/atlas_schemes_functional.json": "ec31051ec39e0053141d173729913e3abcabd1e5",
    "docs/locomotives/chme3/diagnostic_field_observations.json": "416bf49c9303aa1b2186c037b347bb5d272925ff",
    "docs/locomotives/chme3/diagnostic_research_sources_2026.json": "1ab07a982c2d5b87d9cb3cb49e693fdc3de20834",
    "docs/locomotives/chme3/diagnostic_search_vocabulary_addendum.json": "0a93d32f1c73f414b0ae7f6985b619980b409e8e",
    "docs/locomotives/chme3/diagnostic_source_matrix.json": "7a23d9304110e1f26119aac34f6d3fdb87dcf0d9",
    "docs/locomotives/chme3/search_vocabulary_diagnostics_996r_pass3.json": "15b25e9f11d1391727e8c0c9945c2b36e0002038",
    "docs/locomotives/chme3/search_vocabulary_diagnostics_extended_pass3.json": "e1b7bc65b5b753cba2540b1a601c007bb226b48e",
    "docs/locomotives/chme3/search_vocabulary_diagnostics_pass3.json": "84cac38d64dc86479fb7c0532bb68e78815afebc",
    "docs/locomotives/chme3/search_vocabulary.json": "58539ecdcfdda0f8ae7d9640292197647328eb26",
    "docs/locomotives/diesel/chme3-family/chme3/interactive_schemes.json": "6264c992f53d098b49cc90a4a83d56f488aab2ce",
    "docs/locomotives/diesel/chme3-family/chme3e/assistant_semantics_stage3.json": "b456935c5b07d807b90bfc774b5dd27e589a047c",
    "docs/locomotives/diesel/chme3-family/chme3e/interactive_schemes.json": "a45d2665c8734a8f65ebc226ac676309ca7d49e5",
    "docs/locomotives/diesel/chme3-family/chme3e/scheme_designations.json": "e846d6103fddb040b454618e0c8d4ec0b60e6e38",
    "docs/locomotives/diesel/chme3-family/chme3e/schemes_variant.json": "77ecbdd591e5271b78ad4f8e63a3af950e190cc6",
    "docs/locomotives/diesel/chme3-family/chme3t/interactive_schemes.json": "3e0f44209f84dbd77d9a1f2b8b06c3e113858f73",
    "docs/locomotives/diesel/chme3-family/common/diagnostics_manifest.json": "032397b18568fb7f86c3e587c57e9a99ae488808",
    "docs/locomotives/diesel/chme3-family/common/interactive_scheme_contract.json": "4503cd65b8b70975a2e5da8bf3f4fee2013ed3a4",
    "docs/locomotives/diesel/chme3-family/common/interactive_shared_views.json": "97338ef9019e8b2533dbd512ef011def44ad2b1b",
}


def read_pinned(root, path, sha):
    raw = (root / path).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != sha and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == sha, path
    return json.loads(raw)


def build(donor_root):
    documents = [{"sourcePath": p, "sourceBlobSha": sha,
                  "sourceObject": read_pinned(donor_root, p, sha)} for p, sha in PINS.items()]
    assert len(documents) == 21
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
            "runtimeImport": False, "identityPolicy": "NO_CANONICAL_ID_OR_AUTHORITY_ASSIGNED",
            "documents": documents}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root), ensure_ascii=False, separators=(",", ":")) + "\n")
    print("CHME3_REMAINING_DOCUMENT_SOURCES", len(PINS))
