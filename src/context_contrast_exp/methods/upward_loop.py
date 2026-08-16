from typing import Any

def should_stop(history: list[dict[str, Any]], max_rounds: int) -> tuple[bool, str]:
    if len(history) >= max_rounds:
        return True, "max_up_rounds"
    if history and not history[-1].get("incidental_removed", False):
        return True, "no_incidental_context"
    return False, ""
