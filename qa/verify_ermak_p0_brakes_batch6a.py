#!/usr/bin/env python3
import gzip
import json
from collections import deque
from pathlib import Path

APP = Path("app/src/main/assets/technical/ermak_diagnostics.json.gz")
PATCH = Path("patch/app/src/main/assets/technical/ermak_diagnostics.json.gz")
TARGETS = {f"ER-DIAG-{n:03d}" for n in range(81, 87)}
GENERIC = "Отказ локальный (одна секция/узел) или общий?"


def load(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def reachable(scenario: dict) -> set[str]:
    nodes = {n["id"]: n for n in scenario["graph"]["nodes"]}
    queue = deque([scenario["graph"]["startNodeId"]])
    seen: set[str] = set()
    while queue:
        node_id = queue.popleft()
        if node_id in seen:
            continue
        assert node_id in nodes, (scenario["id"], node_id)
        seen.add(node_id)
        node = nodes[node_id]
        if node.get("nextNodeId"):
            queue.append(node["nextNodeId"])
        for choice in node.get("choices", []):
            queue.append(choice["nextNodeId"])
    return seen


app = load(APP)
patch = load(PATCH)
assert app == patch, "app/patch diagnostics differ"
scenarios = app["scenarios"]
assert len(scenarios) == 136, len(scenarios)
by_id = {s["id"]: s for s in scenarios}
assert TARGETS <= by_id.keys(), sorted(TARGETS - by_id.keys())

signatures = {}
for sid in sorted(TARGETS):
    scenario = by_id[sid]
    nodes = scenario["graph"]["nodes"]
    ids = {n["id"] for n in nodes}
    assert len(ids) == len(nodes), f"{sid}: duplicate node ids"
    assert scenario["graph"]["startNodeId"] == "start"
    seen = reachable(scenario)
    assert seen == ids, (sid, sorted(ids - seen))
    prompts = [n.get("prompt", "") for n in nodes if n.get("type") == "question"]
    assert GENERIC not in prompts, sid
    assert len(set(prompts)) >= 3, (sid, prompts)
    assert not any(n.get("type") == "source_action" for n in nodes), sid
    assert "profile-required" in ids, sid
    projection = scenario.get("vl80sUiProjection", {})
    assert len(projection.get("probableCauses", [])) >= 5, sid
    assert len(projection.get("checks", [])) >= 3, sid
    assert len(projection.get("prohibited", [])) >= 3, sid
    signatures[sid] = tuple(prompts)

assert len(set(signatures.values())) == len(TARGETS), "batch6a contains duplicate question trees"

p081 = " ".join(signatures["ER-DIAG-081"]).lower()
assert "давлен" in p081 and "тележ" in p081 and "отпуск" in p081
assert "механ" in " ".join(by_id["ER-DIAG-081"]["vl80sUiProjection"]["probableCauses"]).lower()

p082 = " ".join(signatures["ER-DIAG-082"]).lower()
assert "одной тележ" in p082 and "другая тележ" in p082 and "управля" in p082

p083 = " ".join(signatures["ER-DIAG-083"]).lower()
assert "тормозн" in p083 and "одной тележ" in p083 and "прямодейств" in p083

# Spontaneous braking must route by the first event, not by generic scope first.
s084 = by_id["ER-DIAG-084"]
start084 = next(n for n in s084["graph"]["nodes"] if n["id"] == "start")
labels084 = " ".join(c["label"] for c in start084["choices"]).lower()
assert "тм" in labels084 and "эпк" in labels084 and "тц" in labels084 and "электр" in labels084

# Direct brake route compares its own command with the automatic channel.
p085 = " ".join(signatures["ER-DIAG-085"]).lower()
assert "прямодейств" in p085 and "автоматичес" in p085 and "секц" in p085

# Automatic brake route must separate command->TM from TM->TC and shared execution.
p086 = " ".join(signatures["ER-DIAG-086"]).lower()
assert "тормозной магистрал" in p086 and "тц" in p086 and "прямодейств" in p086

# Profile-sensitive brake scenarios must remain structurally fail-closed.
# Validate the actual route edge to profile-required instead of depending on wording.
for sid in ("ER-DIAG-081", "ER-DIAG-082", "ER-DIAG-084", "ER-DIAG-085", "ER-DIAG-086"):
    nodes = by_id[sid]["graph"]["nodes"]
    profile_node = next((n for n in nodes if n.get("id") == "profile"), None)
    assert profile_node is not None and profile_node.get("type") == "question", sid
    targets = {choice.get("nextNodeId") for choice in profile_node.get("choices", [])}
    assert "profile-required" in targets, (sid, targets)
    assert "reassess" in targets, (sid, targets)

# The two most execution-sensitive routes must explicitly distinguish brake equipment families.
assert all(token in " ".join(signatures["ER-DIAG-086"]) for token in ("№395", "№130", "№130-2"))
assert "исполн" in " ".join(signatures["ER-DIAG-085"]).lower()

strict_generic = sum(
    any(n.get("prompt") == GENERIC for n in s.get("graph", {}).get("nodes", []))
    for s in scenarios
)
print(f"ERMAK_STRICT_GENERIC_ROUTES={strict_generic}")
assert strict_generic <= 67, strict_generic
print("ERMAK P0 BRAKES BATCH6A CONTRACT PASS")
