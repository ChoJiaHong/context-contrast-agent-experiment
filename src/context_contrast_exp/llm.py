import json, os, time
from typing import Protocol
from .schemas import LLMResponse, MethodOutput, Task

class LLMClient(Protocol):
    model: str
    def generate(self, *, system: str, user: str, seed: int | None = None) -> LLMResponse: ...

class MockLLMClient:
    """Deterministic fixture client. It uses benchmark labels and is not evidence."""
    model = "mock-deterministic-v1"
    def generate(self, *, system: str, user: str, seed: int | None = None) -> LLMResponse:
        started=time.perf_counter(); payload=json.loads(user); task=Task.model_validate(payload["task"]); method=payload["method"]; gt=task.ground_truth
        rich=method not in {"direct", "generic_reframe"}; upward=method in {"upward_loop", "bidirectional_loop"}
        output=MethodOutput(problem_formulation=task.specific_problem,relevant_context_differences=gt.relevant_context_differences if rich else [],constraints=gt.changed_constraints if rich else [],resources=gt.available_resources if rich else [],assumption_changes=gt.changed_assumptions if rich else [],cost_structure_changes=gt.changed_cost_structure if rich else [],solution_strategy=f"Apply {gt.valid_strategy_families[0]} while satisfying the stated conditions.",strategy_family=gt.valid_strategy_families[0],essential_context_conditions=gt.essential_context_conditions if upward else [],reasoning_trace=[{"action":"condition_output","method":method}],stop_reason="mock_fixture_complete")
        raw=output.model_dump_json()
        return LLMResponse(raw_response=raw,parsed=output,input_tokens=len(user.split()),output_tokens=len(raw.split()),latency_seconds=time.perf_counter()-started)

class OpenAIClient:
    def __init__(self, model: str, temperature: float=0):
        from openai import OpenAI
        self.client=OpenAI(api_key=os.environ.get("OPENAI_API_KEY")); self.model=model; self.temperature=temperature
    def generate(self, *, system: str, user: str, seed: int | None=None) -> LLMResponse:
        started=time.perf_counter()
        response=self.client.chat.completions.create(model=self.model,temperature=self.temperature,seed=seed,response_format={"type":"json_object"},messages=[{"role":"system","content":system},{"role":"user","content":user}])
        raw=response.choices[0].message.content or ""; parsed=MethodOutput.model_validate_json(raw); usage=response.usage
        return LLMResponse(raw_response=raw,parsed=parsed,input_tokens=usage.prompt_tokens if usage else 0,output_tokens=usage.completion_tokens if usage else 0,latency_seconds=time.perf_counter()-started)
