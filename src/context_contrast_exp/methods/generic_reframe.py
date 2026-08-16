from .direct import Generate
from ..schemas import LLMResponse, MethodOutput, Task


def execute(task: Task, generate: Generate, **_: object) -> tuple[MethodOutput, list[LLMResponse]]:
    response = generate("generically_reframe_then_solve", {"task": task.model_dump()})
    return response.parsed, [response]
