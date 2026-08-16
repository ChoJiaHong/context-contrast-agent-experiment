# Codex Implementation Task

Implement the experiment described in `EXPERIMENT_SPEC.md` as a reproducible Python research project.

## Goal

Build a pilot that can falsify or support the hypothesis that **Context-Contrast-Driven Problem Formulation** improves downstream LLM/agent problem solving.

Do not optimize the implementation to make the proposed method win. The code and benchmark must make negative results easy to observe.

## Required repository structure

```text
.
├── README.md
├── EXPERIMENT_SPEC.md
├── CODEX_TASK.md
├── pyproject.toml
├── .env.example
├── config.example.yaml
├── src/
│   └── context_contrast_exp/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── schemas.py
│       ├── llm.py
│       ├── runner.py
│       ├── methods/
│       │   ├── __init__.py
│       │   ├── direct.py
│       │   ├── generic_reframe.py
│       │   ├── context_contrast_single.py
│       │   ├── downward_loop.py
│       │   ├── upward_loop.py
│       │   └── bidirectional_loop.py
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── matching.py
│       │   ├── objective.py
│       │   ├── metrics.py
│       │   └── statistics.py
│       └── reporting/
│           ├── __init__.py
│           └── markdown_report.py
├── tasks/
│   └── pilot.jsonl
├── prompts/
│   ├── direct.md
│   ├── generic_reframe.md
│   ├── context_contrast_single.md
│   ├── downward_loop.md
│   ├── upward_loop.md
│   └── bidirectional_loop.md
├── tests/
│   ├── test_schemas.py
│   ├── test_metrics.py
│   └── test_stopping.py
├── results/
│   └── .gitkeep
└── reports/
    └── .gitkeep
```

## LLM adapter

Implement a provider abstraction so the experiment is not coupled to one model vendor.

Minimum interface:

```python
class LLMClient(Protocol):
    def generate(self, *, system: str, user: str, seed: int | None = None) -> LLMResponse: ...
```

Track for every call:

- model
- method
- task id
- run id
- input tokens
- output tokens
- latency
- raw response
- parsed structured response

Support JSON structured output when the provider allows it; otherwise parse and validate with Pydantic.

## Method outputs

All methods must ultimately emit the same comparable schema:

```json
{
  "problem_formulation": "...",
  "relevant_context_differences": [],
  "constraints": [],
  "resources": [],
  "assumption_changes": [],
  "cost_structure_changes": [],
  "solution_strategy": "...",
  "strategy_family": "...",
  "essential_context_conditions": [],
  "reasoning_trace": [],
  "stop_reason": "..."
}
```

`reasoning_trace` should contain concise state transitions, not hidden chain-of-thought. Store only explicit method outputs such as identified differences, decisions, validation results, and loop actions.

## Downward loop

The downward method must repeatedly:

1. Form or refine a general reference for the current problem.
2. Specialize one contextual dimension.
3. Compare specific vs reference context.
4. Keep a difference only if it changes at least one of:
   - constraint
   - resource
   - assumption
   - cost structure
5. Estimate whether the difference changes solution validity or strategy choice.
6. Stop if no meaningful new difference is found for `patience` rounds or `max_down_rounds` is reached.

The loop must expose its state after every round.

## Upward loop

The upward method must use counterfactual context removal rather than free-form abstraction.

For each candidate context condition:

1. Remove the condition.
2. Re-evaluate whether the candidate solution remains valid.
3. Re-evaluate whether its strategy remains competitive against conventional alternatives.
4. Mark the condition `essential` only if removal causes failure or material degradation.
5. Continue until no incidental context can be removed or `max_up_rounds` is reached.

## Full bidirectional method

Required control flow:

```text
specific problem
  -> downward context discovery
  -> candidate solution
  -> upward context removal
  -> validation
  -> if validation exposes missing context, return to downward loop
  -> otherwise stop
```

Hard cap total rounds/calls.

## Pilot benchmark

Create 6 initial tasks across at least 4 domains. Include exactly:

- 1 resource-emergence task
- 1 assumption-breaking task
- 1 constraint-changing task
- 1 cost-structure-changing task
- 1 negative-control task with irrelevant contextual differences
- 1 negative-control task where a conventional solution is already sufficient

Important benchmark requirements:

- Do not use the Alishan railway case as one of the six scored pilot tasks. It may appear only as a README example.
- Do not encode one exact natural-language answer as ground truth.
- Ground truth must be strategy-family / constraint / resource based.
- At least 3 tasks must have deterministic or rule-based downstream evaluators.
- The negative controls must penalize unnecessary complexity or reframing.

## Evaluation

Implement:

- set-based precision / recall / F1 for context differences
- constraint recall
- resource recall
- assumption-change recall
- false-context-difference rate
- essential-context precision / recall
- objective task success
- over-reframing rate
- calls, tokens, latency, approximate cost

For semantic matching, do not rely solely on the same LLM being evaluated. Support:

1. exact/normalized aliases defined by the benchmark
2. embedding or external judge as optional secondary metric
3. human adjudication export for ambiguous cases

Primary reported result should prefer deterministic scoring where available.

## Experimental protocol

Default pilot:

- methods: M0..M5 from `EXPERIMENT_SPEC.md`
- 6 tasks
- 5 independent runs per method/task
- fixed model across methods
- configurable temperature
- equal-call-budget experiment
- unrestricted experiment

Persist every run as JSONL so analysis can be rerun without another model call.

## Statistical analysis

For pilot reporting:

- per-method mean and standard deviation
- bootstrap 95% confidence intervals
- paired task-level differences where meaningful
- explicitly label the pilot as underpowered for definitive significance claims

Do not overclaim p-values from the 6-task pilot.

## Automatic Markdown report

Command:

```bash
python -m context_contrast_exp.cli report --results results/<run>.jsonl --out reports/<run>.md
```

The report must contain:

1. Executive summary
2. Research questions and hypotheses
3. Experiment configuration
4. Benchmark composition
5. Aggregate results table
6. Per-task results
7. Downward-loop ablation
8. Upward-loop ablation
9. Full vs single-pass comparison
10. Negative-control / over-reframing analysis
11. Efficiency analysis
12. Failure cases
13. Threats to validity
14. Go / Weak / No-Go decision
15. Raw artifact paths and reproduction command

The conclusion must follow the predefined criteria in `EXPERIMENT_SPEC.md`; it must not reinterpret weak results as success.

## CLI

Provide at least:

```bash
# validate benchmark
cc-exp validate-tasks tasks/pilot.jsonl

# run one method
cc-exp run --tasks tasks/pilot.jsonl --method direct --runs 5

# run all methods
cc-exp run-all --tasks tasks/pilot.jsonl --runs 5

# analyze existing output
cc-exp analyze --results results/<file>.jsonl

# generate report
cc-exp report --results results/<file>.jsonl --out reports/pilot_report.md
```

## Quality requirements

- Python 3.11+
- type hints
- Pydantic schemas
- deterministic unit tests for scoring and stopping logic
- no secrets committed
- `.env.example` only
- clear README reproduction instructions
- fail loudly on malformed model output
- retry model formatting errors separately from method loop iterations

## Deliverables

1. Working code
2. 6-task adversarial pilot benchmark
3. Tests
4. Reproduction instructions
5. Example dry-run result using a mock LLM
6. Automatically generated `reports/mock_pilot_report.md`

Do not fabricate real-model experimental results. The mock report must be explicitly labelled synthetic/mock.
