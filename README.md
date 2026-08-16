# Context-Contrast Agent Experiment

Pilot experiment for evaluating **Context-Contrast-Driven Problem Formulation** in LLM/agent reasoning.

The repository is intentionally designed to **falsify**, not merely confirm, the proposed method.

## Core comparison

- Direct solving
- Generic problem reframing
- Single-pass context contrast
- Downward-loop only
- Upward-loop only
- Full bidirectional context-contrast loop

## Primary questions

1. Does explicit context contrast improve discovery of relevant constraints/resources?
2. Does that improvement translate to downstream task success?
3. Are the downward and upward loops individually necessary?
4. Does the method over-reframe negative-control problems?
5. Is the full method better than generic reframing under comparable inference budgets?

See `EXPERIMENT_SPEC.md` for the experimental design and `CODEX_TASK.md` for the implementation task intended for Codex.

## Installation

Requires Python 3.11+.

    python -m pip install -e '.[dev]'

Copy config.example.yaml for real experiments and set OPENAI_API_KEY only in the environment. The default mock provider is deterministic and synthetic.

## Reproduction

    cc-exp validate-tasks tasks/pilot.jsonl
    cc-exp run --tasks tasks/pilot.jsonl --method direct --runs 5
    cc-exp run-all --tasks tasks/pilot.jsonl --runs 5 --out results/pilot.jsonl
    cc-exp analyze --results results/pilot.jsonl
    python -m context_contrast_exp.cli report --results results/pilot.jsonl --out reports/pilot_report.md
    cc-exp export-adjudication --results results/pilot.jsonl --tasks tasks/pilot.jsonl --out reports/adjudication.jsonl

Every successful call is persisted with raw and validated output, seed, tokens, latency, model, method, task, run, action, and call identifiers; run records also contain aggregate cost. Formatting retries are distinct from loop iterations. The deterministic mock uses task-text fixture rules—not benchmark ground truth—to exercise infrastructure, and its results are **not model evidence**.

Evaluated methods receive only the task ID, domain, specific problem, and context facts. Ground-truth sets, aliases, evaluator rules, task-type labels, and the benchmark's reference problem class remain inside the scoring harness and are never included in model prompts.

## Benchmark and scoring

The six-task adversarial pilot spans public health, software operations, manufacturing, energy, logistics, and administration. Ground truth uses sets, aliases, strategy families, and rule/numeric evaluators rather than a single target sentence. Negative controls penalize invented context and needless strategy changes. Deterministic normalized aliases are primary; exported JSONL supports optional external semantic judging and human adjudication without rerunning a model.

The report uses bootstrap intervals, descriptive standard deviations in analysis utilities, and predefined Go/Weak/No-Go logic. Six tasks are explicitly underpowered. Set `budget_mode: equal_calls` to apply `equal_call_budget` as the common maximum opportunity for every method. Set `budget_mode: unrestricted` to use the method loop limits subject to the safety cap `max_total_calls`.

The Alishan railway can motivate the intuition informally, but is intentionally absent from scored tasks.
