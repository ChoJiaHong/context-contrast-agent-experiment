import json, os, time
from typing import Protocol
from .schemas import LLMResponse, MethodOutput, Task

class LLMClient(Protocol):
    model: str
    def generate(self, *, system: str, user: str, seed: int | None = None) -> LLMResponse: ...

class MockLLMClient:
    """Deterministic, task-text-only fixture; never treat its output as evidence."""
    model = "mock-deterministic-v1"
    def generate(self, *, system: str, user: str, seed: int | None = None) -> LLMResponse:
        started=time.perf_counter(); payload=json.loads(user); task=Task.model_validate(payload["task"]); method=payload["method"]
        text=" ".join([task.specific_problem,*task.context_facts]).lower(); rich=method not in {"direct", "generic_reframe"}
        rules=[("refrigerated",("existing ferry cold-chain capacity",[],["certified refrigerated ferry lockers"],[],[],"shared cold-chain transport")),("reconnect",("clients reconnect out of order",[],[],["all clients upgrade together"],[],"backward-compatible expand-contract migration")),("allergen",("regulatory segregation requirement",["never mix allergen and non-allergen tools"],[],[],[],"segregated batch scheduling")),("demand charge",("peak demand dominates marginal energy price",[],[],[],["monthly peak demand charge"],"peak-aware load shaping")),("paint",("",[],[],[],[],"conventional shortest-path routing")),("meeting room",("",[],[],[],[],"standard calendar booking"))]
        match=next(value for needle,value in rules if needle in text); difference,constraints,resources,assumptions,costs,strategy=match
        removed=payload.get("removed_condition"); essential=[removed] if removed and any(word in removed for word in ("refrigerated","order","forbidden","demand charge")) else []
        output=MethodOutput(problem_formulation=task.specific_problem,relevant_context_differences=[difference] if rich and difference else [],constraints=constraints if rich else [],resources=resources if rich else [],assumption_changes=assumptions if rich else [],cost_structure_changes=costs if rich else [],solution_strategy=f"Apply {strategy} while satisfying the stated conditions.",strategy_family=strategy,essential_context_conditions=essential,reasoning_trace=[{"action":payload.get("action","fixture")}],stop_reason="mock_fixture_complete")
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
