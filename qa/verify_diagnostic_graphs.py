#!/usr/bin/env python3
"""Validate diagnostic graph integrity without starting Android."""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path


PROFILE_MIRRORS = (
    "src/main/java/ru/railbrake/calculator/core/LocomotiveProfile.kt",
    "src/main/java/ru/railbrake/calculator/data/LocomotiveProfileRepository.kt",
    "src/main/java/ru/railbrake/calculator/core/DiagnosticPolicyEngine.kt",
    "src/main/java/ru/railbrake/calculator/core/DiagnosticProfileContext.kt",
    "src/main/java/ru/railbrake/calculator/core/ErmakDiagnosticRepository.kt",
    "src/main/java/ru/railbrake/calculator/ui/ErmakProfileContextCard.kt",
    "src/test/java/ru/railbrake/calculator/core/LocomotiveProfileTest.kt",
    "src/test/java/ru/railbrake/calculator/core/DiagnosticPolicyEngineTest.kt",
    "src/test/java/ru/railbrake/calculator/core/DiagnosticProfileContextTest.kt",
)


def load_json(assets: Path, name: str) -> dict:
    plain = assets / "technical" / f"{name}.json"
    packed = assets / "technical" / f"{name}.json.gz"
    path = plain if plain.exists() else packed
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as source:
        return json.load(source)


def validate_profile_mirrors(repo_root: Path) -> list[str]:
    app_root = repo_root / "app"
    patch_root = repo_root / "patch" / "app"
    if not patch_root.is_dir():
        return []

    errors: list[str] = []
    for relative in PROFILE_MIRRORS:
        app_file = app_root / relative
        patch_file = patch_root / relative
        if not app_file.is_file():
            errors.append(f"profile mirror: отсутствует {app_file.as_posix()}")
            continue
        if not patch_file.is_file():
            errors.append(f"profile mirror: отсутствует {patch_file.as_posix()}")
            continue
        if app_file.read_bytes() != patch_file.read_bytes():
            errors.append(f"profile mirror: app/patch различаются для {relative}")
    return errors


def validate_ermak(assets: Path) -> tuple[int, list[str]]:
    scenarios = load_json(assets, "ermak_diagnostics").get("scenarios", [])
    errors: list[str] = []
    ids = {item.get("id") for item in scenarios}
    for scenario in scenarios:
        scenario_id = scenario.get("id", "<без id>")
        graph = scenario.get("graph", {})
        nodes = {node.get("id"): node for node in graph.get("nodes", []) if node.get("id")}
        start = graph.get("startNodeId")
        if start not in nodes:
            errors.append(f"{scenario_id}: отсутствует стартовый узел {start!r}")
            continue

        reachable: set[str] = set()
        pending = [start]
        while pending:
            node_id = pending.pop()
            if node_id in reachable or node_id not in nodes:
                continue
            reachable.add(node_id)
            node = nodes[node_id]
            targets = [node.get("nextNodeId")]
            targets.extend(choice.get("nextNodeId") for choice in node.get("choices", []))
            for target in filter(None, targets):
                if target not in nodes:
                    errors.append(f"{scenario_id}/{node_id}: переход в отсутствующий узел {target}")
                else:
                    pending.append(target)

            if node.get("type") == "question" and not node.get("choices"):
                errors.append(f"{scenario_id}/{node_id}: вопрос без вариантов ответа")

        unreachable = sorted(set(nodes) - reachable)
        if unreachable:
            errors.append(f"{scenario_id}: недостижимые узлы: {', '.join(unreachable)}")

        for related in scenario.get("relatedScenarioIds", []):
            if related not in ids:
                errors.append(f"{scenario_id}: отсутствует связанный сценарий {related}")

    return len(scenarios), errors


def main() -> int:
    assets = Path(sys.argv[1] if len(sys.argv) > 1 else "app/src/main/assets")
    count, errors = validate_ermak(assets)
    errors.extend(validate_profile_mirrors(Path.cwd()))
    if errors:
        print("DIAGNOSTIC GRAPH CONTRACT FAIL")
        print("\n".join(f" - {error}" for error in errors))
        return 1
    print(f"DIAGNOSTIC GRAPH CONTRACT PASS: {count} Ermak scenarios; profile mirrors OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
