from typing import Any

def should_stop(history: list[dict[str, Any]], patience: int, max_rounds: int) -> tuple[bool, str]:
    if len(history) >= max_rounds:
        return True, "max_down_rounds"
    misses = 0
    for state in reversed(history):
        if state.get("meaningful_new_difference"):
            break
        misses += 1
    return (True, "patience_exhausted") if misses >= patience else (False, "")
