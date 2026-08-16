from collections.abc import Callable

from ..schemas import LLMResponse, MethodOutput, Task

Generate = Callable[[str, dict], LLMResponse]


def execute(task: Task, generate: Generate, **_: object) -> tuple[MethodOutput, list[LLMResponse]]:
    response = generate("solve_directly", {"task": task.model_dump()})
    return response.parsed, [response]
