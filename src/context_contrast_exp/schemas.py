from typing import Any, Literal
from pydantic import BaseModel, Field

class GroundTruth(BaseModel):
    relevant_context_differences: list[str] = Field(default_factory=list)
    changed_constraints: list[str] = Field(default_factory=list)
    available_resources: list[str] = Field(default_factory=list)
    changed_assumptions: list[str] = Field(default_factory=list)
    changed_cost_structure: list[str] = Field(default_factory=list)
    valid_strategy_families: list[str]
    essential_context_conditions: list[str] = Field(default_factory=list)
    aliases: dict[str, list[str]] = Field(default_factory=dict)

class ObjectiveEvaluator(BaseModel):
    type: Literal["rules", "numeric", "human"]
    spec: dict[str, Any] = Field(default_factory=dict)

class Task(BaseModel):
    id: str
    domain: str
    task_type: Literal["resource-emergence", "assumption-breaking", "constraint-changing", "cost-structure-changing", "negative-control-irrelevant", "negative-control-conventional"]
    specific_problem: str
    general_problem_class: str
    context_facts: list[str]
    ground_truth: GroundTruth
    objective_evaluator: ObjectiveEvaluator

class MethodOutput(BaseModel):
    problem_formulation: str
    relevant_context_differences: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    assumption_changes: list[str] = Field(default_factory=list)
    cost_structure_changes: list[str] = Field(default_factory=list)
    solution_strategy: str
    strategy_family: str
    essential_context_conditions: list[str] = Field(default_factory=list)
    reasoning_trace: list[dict[str, Any]] = Field(default_factory=list)
    stop_reason: str

class LLMResponse(BaseModel):
    raw_response: str
    parsed: MethodOutput
    input_tokens: int = 0
    output_tokens: int = 0
    latency_seconds: float = 0

class RunRecord(BaseModel):
    task_id: str
    domain: str
    task_type: str
    method: str
    run_id: int
    seed: int
    model: str
    output: MethodOutput
    raw_responses: list[str]
    calls: int
    input_tokens: int
    output_tokens: int
    latency_seconds: float
    approximate_cost: float
    metrics: dict[str, float | bool | None]
    configuration: dict[str, Any]
    is_mock: bool = False
