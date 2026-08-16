# Context-Contrast Pilot Report
> **SYNTHETIC MOCK — NOT EMPIRICAL EVIDENCE**
## Executive summary
This underpowered six-task pilot cannot support definitive significance claims. Mock values validate the pipeline only.

## Research questions and hypotheses
Tests H1–H5 from EXPERIMENT_SPEC.md: formulation discovery, downstream success, loop value, bounded over-reframing, and independently useful upward removal.

## Experiment configuration
- Model: mock-deterministic-v1
- Records: 36
- Mock: True

## Benchmark composition
assumption-breaking: 6, constraint-changing: 6, cost-structure-changing: 6, negative-control-conventional: 6, negative-control-irrelevant: 6, resource-emergence: 6

## Aggregate results table
| Method | Objective mean | 95% bootstrap CI | Context F1 | Calls | Tokens |
|---|---:|---:|---:|---:|---:|
| direct | 1.000 | [1.000, 1.000] | 0.333 | 1.0 | 20.0 |
| generic_reframe | 1.000 | [1.000, 1.000] | 0.333 | 1.0 | 20.0 |
| context_contrast_single | 1.000 | [1.000, 1.000] | 1.000 | 1.0 | 20.0 |
| downward_loop | 1.000 | [1.000, 1.000] | 1.000 | 1.0 | 20.0 |
| upward_loop | 1.000 | [1.000, 1.000] | 1.000 | 1.0 | 20.0 |
| bidirectional_loop | 1.000 | [1.000, 1.000] | 1.000 | 1.0 | 20.0 |

## Per-task results
- **assumption_001:** direct=1, generic_reframe=1, context_contrast_single=1, downward_loop=1, upward_loop=1, bidirectional_loop=1
- **constraint_001:** direct=1, generic_reframe=1, context_contrast_single=1, downward_loop=1, upward_loop=1, bidirectional_loop=1
- **cost_001:** direct=1, generic_reframe=1, context_contrast_single=1, downward_loop=1, upward_loop=1, bidirectional_loop=1
- **negative_conventional_001:** direct=1, generic_reframe=1, context_contrast_single=1, downward_loop=1, upward_loop=1, bidirectional_loop=1
- **negative_irrelevant_001:** direct=1, generic_reframe=1, context_contrast_single=1, downward_loop=1, upward_loop=1, bidirectional_loop=1
- **resource_001:** direct=1, generic_reframe=1, context_contrast_single=1, downward_loop=1, upward_loop=1, bidirectional_loop=1

## Downward-loop ablation
Compare bidirectional_loop with upward_loop, and downward_loop with single pass. Mock output is not an ablation result.

## Upward-loop ablation
Compare bidirectional_loop with downward_loop; essential-context precision/recall are independently reported.

## Full vs single-pass comparison
Compare objective success under equal budgets; richer text alone is not success.

## Negative-control / over-reframing analysis
Mean over-reframing: 0.000.

## Efficiency analysis
Total calls: 36; total tokens: 720; approximate cost: 0.000000.

## Failure cases
Review records with objective success false and adjudicate semantic mismatches.

## Threats to validity
Six hand-built tasks are underpowered; alias coverage, model dependence, mock leakage, and evaluator validity limit inference.

## Go / Weak / No-Go decision
Mock run: **No decision**. For real runs apply the predefined criteria without reinterpretation.

## Raw artifact paths and reproduction command
- Results: results/mock_pilot.jsonl
- Reproduce: python -m context_contrast_exp.cli report --results results/mock_pilot.jsonl --out reports/mock_pilot_report.md
