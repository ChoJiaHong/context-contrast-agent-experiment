from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from .common import merge_outputs, task_input
from .downward_loop import execute as downward

if TYPE_CHECKING:
    from ..schemas import LLMResponse, MethodOutput, Task

Generate = Callable[[str, dict], Any]


def execute(
    task: Task,
    generate: Generate,
    *,
    max_rounds: int,
    patience: int,
    max_total_calls: int,
    max_up_rounds: int,
    **_: object,
) -> tuple[MethodOutput, list[LLMResponse]]:
    discovered, responses = downward(task, generate, max_rounds=max_rounds, patience=patience)
    trace = list(discovered.reasoning_trace)
    visible_task = task_input(task)

    while len(responses) < max_total_calls:
        candidate = generate("solve_using_discovered_context", {"task": visible_task, "discovery": discovered.model_dump()})
        responses.append(candidate)
        current = merge_outputs([discovered, candidate.parsed])
        missing: set[str] = set()

        for condition in task.context_facts[:max_up_rounds]:
            if len(responses) >= max_total_calls:
                return merge_outputs([discovered, current], reasoning_trace=trace, stop_reason="max_total_calls"), responses
            checked = generate("validate_counterfactual_removal", {"task": visible_task, "candidate": current.model_dump(), "removed_condition": condition})
            responses.append(checked)
            current = merge_outputs([current, checked.parsed])
            essential = condition in checked.parsed.essential_context_conditions
            trace.append({"action": "upward_validation", "condition": condition, "essential": essential})
            missing.update(set(checked.parsed.relevant_context_differences) - set(discovered.relevant_context_differences))

        if not missing:
            return current.model_copy(update={"reasoning_trace": trace, "stop_reason": "validation_complete"}), responses

        trace.append({"action": "return_to_downward", "missing_differences": sorted(missing)})
        remaining = max_total_calls - len(responses)
        if remaining <= 1:
            return current.model_copy(update={"reasoning_trace": trace, "stop_reason": "max_total_calls"}), responses
        refined, extra = downward(
            task,
            generate,
            max_rounds=min(max_rounds, remaining - 1),
            patience=patience,
            initial_seen=set(discovered.relevant_context_differences),
            validation_feedback=sorted(missing),
        )
        responses.extend(extra)
        discovered = merge_outputs([discovered, refined])

    return discovered.model_copy(update={"reasoning_trace": trace, "stop_reason": "max_total_calls"}), responses
