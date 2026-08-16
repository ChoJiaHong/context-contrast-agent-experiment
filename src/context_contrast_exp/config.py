from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel, Field

class ExperimentConfig(BaseModel):
    provider: Literal["mock", "openai"] = "mock"
    model: str = "mock-deterministic-v1"
    temperature: float = Field(0.0, ge=0, le=2)
    max_down_rounds: int = Field(3, ge=1)
    max_up_rounds: int = Field(3, ge=1)
    max_total_calls: int = Field(10, ge=2)
    patience: int = Field(1, ge=1)
    format_retries: int = Field(2, ge=0)
    budget_mode: Literal["equal_calls", "unrestricted"] = "equal_calls"
    equal_call_budget: int = Field(3, ge=1)
    approximate_input_cost_per_million: float = 0
    approximate_output_cost_per_million: float = 0

    @classmethod
    def load(cls, path: str | None) -> "ExperimentConfig":
        return cls() if not path else cls.model_validate(yaml.safe_load(Path(path).read_text()) or {})

    @property
    def effective_call_cap(self) -> int:
        return self.equal_call_budget if self.budget_mode == "equal_calls" else self.max_total_calls
