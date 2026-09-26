#!/usr/bin/env python3
from deepen_ermak_p0_safety_batch7a import ROUTES, main, q, finding

# ER-DIAG-089 keeps an explicit route-back when the observed indication is not
# actually related to EPK. The other safety routes reject an incompatible
# equipment profile through profile-required, so their shared not-this terminal
# is intentionally unnecessary and must not remain as a dead graph node.
nodes = ROUTES["ER-DIAG-089"]["nodes"]
index = next(i for i, node in enumerate(nodes) if node.get("id") == "indication")
nodes[index:index + 1] = [
    q("indication", "При отсутствии фактического торможения ненормальная индикация прямо относится к ЭПК/его состоянию?", [
        ("Да", "indication-finding"),
        ("Нет, это другой симптом", "not-this-scenario"),
        ("Не уверен", "profile"),
    ]),
    finding("indication-finding", "При отсутствии фактического торможения отделите отказ индикации/обратной связи от состояния ЭПК; не создавать торможение специально ради проверки.", "profile"),
]

for scenario_id in ("ER-DIAG-093", "ER-DIAG-094", "ER-DIAG-095", "ER-DIAG-096", "ER-DIAG-097"):
    ROUTES[scenario_id]["nodes"] = [
        node for node in ROUTES[scenario_id]["nodes"] if node.get("id") != "not-this-scenario"
    ]

if __name__ == "__main__":
    main()
