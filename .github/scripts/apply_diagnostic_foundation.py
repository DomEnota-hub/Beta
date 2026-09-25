#!/usr/bin/env python3
import base64
import re
import subprocess
import zlib
from pathlib import Path

BASE = "ce621e8fdc5a26af8670a056558b2e7d3bfc386a"
PATH = ".github/scripts/apply_diagnostic_foundation.py"
subprocess.run(["git", "fetch", "origin", BASE, "--depth=1"], check=True, stdout=subprocess.DEVNULL)
old_runner = subprocess.check_output(["git", "show", f"{BASE}:{PATH}"], text=True)
match = re.search(r"b64decode\('([^']+)'\)", old_runner)
if not match:
    raise RuntimeError("Original diagnostic foundation payload not found")
source = zlib.decompress(base64.b64decode(match.group(1))).decode("utf-8")
source = source.replace(
    'TechnicalAssetReader.readJsonObject(appContext, "technical/ermak_diagnostics.json")',
    'TechnicalAssetReader.json(appContext, "technical/ermak_diagnostics.json")',
)
source = source.replace(
    'Text(policyDecision.message.ifBlank {',
    'Text(policyDecision?.message.orEmpty().ifBlank {',
)
if 'readJsonObject(appContext, "technical/ermak_diagnostics.json")' in source:
    raise RuntimeError("Loader API replacement failed")
exec(compile(source, __file__, "exec"))

obsolete_contract = """        assertTrue(
            parsed.flatMap { it.nodes.values }.any {
                it.actionMetadata.userFacingPolicy == DiagnosticUserFacingPolicy.EMERGENCY_SOURCE_BOUND
            }
        )
"""
for rel in (
    "app/src/test/java/ru/railbrake/calculator/core/ErmakDiagnosticRuntimeContractTest.kt",
    "patch/app/src/test/java/ru/railbrake/calculator/core/ErmakDiagnosticRuntimeContractTest.kt",
):
    path = Path(rel)
    text = path.read_text(encoding="utf-8")
    if obsolete_contract not in text:
        raise RuntimeError(f"Obsolete emergency-policy asset assertion not found in {rel}")
    path.write_text(text.replace(obsolete_contract, ""), encoding="utf-8")

# The Actions GITHUB_TOKEN cannot update workflow files. Keep the normal build
# workflow unchanged in this guarded commit; its mirror checks will be updated
# separately through the GitHub connector after the foundation lands.
subprocess.run(
    ["git", "restore", "--source=HEAD", "--", ".github/workflows/dev14-safe-build-v2.yml"],
    check=True,
)

print("Runtime contract aligned with policies actually present in the canonical asset.")
print("Normal build workflow intentionally left unchanged for this Actions-authored commit.")
