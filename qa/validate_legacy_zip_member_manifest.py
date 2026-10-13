#!/usr/bin/env python3
"""Verify a read-only pinned donor ZIP and its member inventory."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path("docs/data-migration")
MANIFEST = ROOT / "legacy-zip-member-manifest.json"
HISTORY_GATE = Path("feature-history/src/main/kotlin/ru/railbrake/calculator/history/HistoryContracts.kt")


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def validate(root: Path, archive_path: Path) -> int:
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == 1
    assert manifest["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    archive = manifest["archive"]
    assert archive["sourcePath"] == "RailBrakeCalculator.zip"
    assert archive["retrievalUrl"] == ("https://raw.githubusercontent.com/DomEnota-hub/Test-/"
                                      "3176d6ee228f0ed4b78371f45209e10c1c724eff/RailBrakeCalculator.zip")
    assert archive["copyInDestination"] is False
    assert archive["publicationStatus"] == "CANDIDATE" and archive["runtimeImport"] is False
    raw = archive_path.read_bytes()
    assert git_blob(raw) == archive["gitBlobSha"] == "6c3c7edc1713c1c901a566fd8a81a2494ee4ac58"
    assert hashlib.sha256(raw).hexdigest() == archive["sha256"]
    with zipfile.ZipFile(archive_path) as z:
        assert z.testzip() is None
        info = z.infolist()
        files = [x for x in info if not x.is_dir()]
        assert len(info) == manifest["counts"]["allEntries"] == 92
        assert len(files) == len(manifest["members"]) == manifest["counts"]["fileMembers"] == 60
        names = [x.filename for x in files]
        assert len(set(names)) == len(names)
        assert all(name.startswith("RailBrakeCalculator/") and ".." not in Path(name).parts for name in names)
        assert len({r["gitBlobSha"] for r in manifest["members"]}) == manifest["counts"]["uniqueFileBlobs"] == 59
        exact = 0
        for source, entry in zip(files, manifest["members"]):
            assert source.filename == "RailBrakeCalculator/" + entry["path"]
            contents = z.read(source)
            assert source.file_size == entry["bytes"] == len(contents)
            assert git_blob(contents) == entry["gitBlobSha"]
            matches = entry["pinnedTreeExactPaths"]
            if matches:
                exact += 1
                assert entry["comparison"] == "EXACT_BLOB_IN_PINNED_TREE"
                assert all(path and path != "RailBrakeCalculator.zip" for path in matches)
            else:
                assert entry["comparison"] == "NO_EXACT_BLOB_IN_PINNED_TREE"
            if not entry["path"].startswith("app/"):
                assert entry["pinnedPatchBlob"] is None
        assert exact == manifest["counts"]["exactBlobMatchesInPinnedTree"] == 14
        assert len(files) - exact == manifest["counts"]["differentOrNoExactCounterpart"] == 46
        history = manifest["historyFormat"]
        member = history["memberPath"]
        assert member.endswith("/data/HistoryRepository.kt")
        assert git_blob(z.read(member)) == history["gitBlobSha"] == "d95a2ce465e2f09bb96d74b8318f36b16d21afd0"
        code = z.read(member).decode("utf-8")
        assert 'getSharedPreferences("calculation_history", Context.MODE_PRIVATE)' in code
        assert 'private const val KEY = "records"' in code and 'private const val MAX = 30' in code
        assert 'current.distinctBy { it.timestampMillis }.take(MAX)' in code
        assert '.sortedByDescending { it.timestampMillis }' in code
        assert 'if (p.size != 5) return null' in code
        assert 'Base64.NO_WRAP or Base64.URL_SAFE' in code
        assert history["preferencesFile"] == "calculation_history" and history["key"] == "records"
        assert history["container"] == "SharedPreferences StringSet" and history["maxRecords"] == 30
        assert history["recordFormat"] == "timestampMillis|base64url(mode)|base64url(title)|base64url(summary)|base64url(details)"
        assert history["migrationStatus"] == "FORMAT_OBSERVED_MIGRATION_PENDING" and history["runtimeImport"] is False
        media = manifest["media"]
        assert len(media) == 2 and len({item["memberPath"] for item in media}) == 2
        for item in media:
            assert item["memberPath"] in names
            assert git_blob(z.read(item["memberPath"])) == item["gitBlobSha"]
            assert item["ownerCandidate"] == "vl80s"
            assert item["publicationStatus"] == "CANDIDATE" and item["runtimeImport"] is False
            assert item["width"] > 0 and item["height"] > 0
        assert media[0]["format"] == "JPEG" and media[1]["format"] == "PNG"
    contract = (root / HISTORY_GATE).read_text(encoding="utf-8")
    assert "const val legacyFormatVerified: Boolean = false" in contract
    return len(files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    print("LEGACY_ZIP_MEMBER_MANIFEST_PASS", validate(args.root, args.archive))
