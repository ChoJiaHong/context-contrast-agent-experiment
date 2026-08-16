def evaluate_strategy(strategy_family: str, evaluator: dict) -> bool | None:
    if evaluator["type"] == "human":
        return None
    allowed=evaluator.get("spec",{}).get("allowed_strategy_families",[])
    return strategy_family in allowed
