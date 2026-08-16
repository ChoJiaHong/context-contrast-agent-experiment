from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from .common import merge_outputs

if TYPE_CHECKING:
    from ..schemas import LLMResponse, MethodOutput, Task

Generate = Callable[[str, dict], Any]


def should_stop(history: list[dict[str, Any]], max_rounds: int) -> tuple[bool, str]:
    if len(history) >= max_rounds:
        return True, "max_up_rounds"
    if history and not history[-1].get("incidental_removed", False):
        return True, "no_incidental_context"
    return False, ""


def execute(task: Task, generate: Generate, *, max_rounds: int, max_total_calls: int = 10, **_: object) -> tuple[MethodOutput, list[LLMResponse]]:
    candidate = generate("produce_candidate_solution", {"task": task.model_dump()})
    responses = [candidate]
    conditions = list(task.context_facts)
    history: list[dict[str, Any]] = []
    final = candidate.parsed
    while conditions:
        if len(responses) >= max_total_calls:
            return merge_outputs([item.parsed for item in responses], reasoning_trace=history, stop_reason="max_total_calls"), responses
        removed = conditions.pop(0)
        response = generate("counterfactual_removal_test", {"task": task.model_dump(), "candidate": candidate.parsed.model_dump(), "removed_condition": removed, "remaining_conditions": conditions})
        responses.append(response); final = response.parsed
        essential = removed in response.parsed.essential_context_conditions
        history.append({"round": len(history) + 1, "removed_condition": removed, "solution_failed_or_degraded": essential, "incidental_removed": not essential})
        stop, reason = should_stop(history, max_rounds)
        if stop:
            return merge_outputs([item.parsed for item in responses], reasoning_trace=history, stop_reason=reason), responses
    return merge_outputs([item.parsed for item in responses], reasoning_trace=history, stop_reason="all_conditions_tested"), responses
