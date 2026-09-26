#!/usr/bin/env python3
from deepen_ermak_p0_safety_batch7a import ROUTES, main, q, finding

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

if __name__ == "__main__":
    main()
