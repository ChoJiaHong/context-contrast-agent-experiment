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
