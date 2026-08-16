from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from .common import merge_outputs

if TYPE_CHECKING:
    from ..schemas import LLMResponse, MethodOutput, Task

Generate = Callable[[str, dict], Any]


def should_stop(history: list[dict[str, Any]], patience: int, max_rounds: int) -> tuple[bool, str]:
    if len(history) >= max_rounds:
        return True, "max_down_rounds"
    misses = 0
    for state in reversed(history):
        if state.get("meaningful_new_difference"):
            break
        misses += 1
    return (True, "patience_exhausted") if misses >= patience else (False, "")


def execute(task: Task, generate: Generate, *, max_rounds: int, patience: int, **_: object) -> tuple[MethodOutput, list[LLMResponse]]:
    responses: list[LLMResponse] = []
    history: list[dict[str, Any]] = []
    seen: set[str] = set()
    while True:
        response = generate("downward_discovery_round", {"task": task.model_dump(), "round": len(history) + 1, "prior_states": history})
        responses.append(response)
        current = set(response.parsed.relevant_context_differences)
        structural = bool(response.parsed.constraints or response.parsed.resources or response.parsed.assumption_changes or response.parsed.cost_structure_changes)
        new = current - seen
        state = {"round": len(history) + 1, "new_differences": sorted(new), "meaningful_new_difference": bool(new and structural)}
        history.append(state)
        seen |= current
        stop, reason = should_stop(history, patience, max_rounds)
        if stop:
            output = merge_outputs([item.parsed for item in responses], reasoning_trace=history, stop_reason=reason)
            return output, responses
