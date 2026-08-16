from collections.abc import Callable

from ..schemas import LLMResponse, MethodOutput, Task
from .common import task_input

Generate = Callable[[str, dict], LLMResponse]


def execute(task: Task, generate: Generate, **_: object) -> tuple[MethodOutput, list[LLMResponse]]:
    response = generate("solve_directly", {"task": task_input(task)})
    return response.parsed, [response]
