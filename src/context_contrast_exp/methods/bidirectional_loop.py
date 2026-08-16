from .direct import Generate
from .downward_loop import execute as downward
from ..schemas import LLMResponse, MethodOutput, Task


def execute(task: Task, generate: Generate, *, max_rounds: int, patience: int, max_total_calls: int, max_up_rounds: int, **_: object) -> tuple[MethodOutput, list[LLMResponse]]:
    discovered, responses = downward(task, generate, max_rounds=max_rounds, patience=patience)
    if len(responses) >= max_total_calls:
        return discovered.model_copy(update={"stop_reason": "max_total_calls"}), responses
    candidate = generate("solve_using_discovered_context", {"task": task.model_dump(), "discovery": discovered.model_dump()})
    responses.append(candidate); current = candidate.parsed
    trace = list(discovered.reasoning_trace)
    for condition in task.context_facts[:max_up_rounds]:
        if len(responses) >= max_total_calls:
            return current.model_copy(update={"reasoning_trace": trace, "stop_reason": "max_total_calls"}), responses
        checked = generate("validate_counterfactual_removal", {"task": task.model_dump(), "candidate": current.model_dump(), "removed_condition": condition})
        responses.append(checked); current = checked.parsed
        essential = condition in current.essential_context_conditions
        trace.append({"action": "upward_validation", "condition": condition, "essential": essential})
        known = set(discovered.relevant_context_differences)
        missing = set(current.relevant_context_differences) - known
        if missing and len(responses) < max_total_calls:
            trace.append({"action": "return_to_downward", "missing_differences": sorted(missing)})
            remaining = max_total_calls - len(responses)
            refined, extra = downward(task, generate, max_rounds=min(max_rounds, remaining), patience=patience)
            responses.extend(extra); discovered = refined; current = refined
    return current.model_copy(update={"reasoning_trace": trace, "stop_reason": "validation_complete"}), responses
