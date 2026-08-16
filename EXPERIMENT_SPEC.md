# Experiment Specification

## Research object

Evaluate whether **Context-Contrast-Driven Problem Formulation** improves LLM/agent problem solving beyond direct answering and generic reframing.

The method treats context differences as relevant only when they change at least one of:

- constraints
- resources
- assumptions
- cost structure

The core method has two loops:

### Downward loop
Increase contextual specificity and search for structural context differences that change problem–solution fit.

### Upward loop
Remove incidental context conditions and test which conditions are actually essential for solution validity.

## Methods to compare

### M0 — Direct
`Specific Problem -> Solution`

### M1 — Generic Reframing
`Specific Problem -> Reframe -> Solution`

### M2 — Single-Pass Context Contrast
`Specific -> General Class -> General Solutions -> Context Difference -> Constraint/Resource -> Adapted Solution`

### M3 — Downward Loop Only
Repeated contextual specialization and contrast until no meaningful new difference is found or budget is reached.

### M4 — Upward Loop Only
Start from a candidate solution and repeatedly remove context conditions, revalidating solution applicability.

### M5 — Full Bidirectional Loop
Downward discovery + candidate solution + upward counterfactual context removal + validation + repeat if needed.

## Pilot benchmark

Start with 6 adversarial tasks, then scale to 30 if signal exists.

Task types:

1. Resource-emergence
2. Assumption-breaking
3. Constraint-changing
4. Cost-structure-changing
5. Negative control: contextual differences exist but should not alter the solution
6. Negative control: obvious conventional solution is already sufficient

## Required task schema

Each task should contain:

```json
{
  "id": "task_001",
  "domain": "...",
  "specific_problem": "...",
  "general_problem_class": "...",
  "context_facts": ["..."],
  "ground_truth": {
    "relevant_context_differences": ["..."],
    "changed_constraints": ["..."],
    "available_resources": ["..."],
    "changed_assumptions": ["..."],
    "changed_cost_structure": ["..."],
    "valid_strategy_families": ["..."],
    "essential_context_conditions": ["..."]
  },
  "objective_evaluator": {
    "type": "rules|numeric|human",
    "spec": {}
  }
}
```

Do not make a single hand-authored target phrase the only correct answer. Score strategy families and objective feasibility.

## Primary metrics

### Problem-formulation metrics

- Relevant Context Difference Precision / Recall / F1
- Constraint Recall
- Resource Recall
- Assumption-change Recall
- False Context Difference Rate

### Solution metrics

- Strategy validity
- Constraint satisfaction
- Objective task success
- Over-engineering / over-reframing rate

### Upward-loop metrics

- Essential Context Precision / Recall
- Incidental Context Removal Rate
- Applicability boundary accuracy

### Efficiency metrics

- Model calls
- Input/output tokens
- Wall-clock latency
- Approximate API cost

## Core hypotheses

### H1
Context-contrast methods discover more relevant constraints/resources than direct solving.

### H2
Any improvement in formulation translates into higher downstream task success.

### H3
Full bidirectional looping outperforms single-pass context contrast on tasks where later solution validation exposes missing context.

### H4
On negative-control tasks, the method does not substantially increase over-reframing or needless complexity.

### H5
The upward loop improves essential-context identification rather than merely producing post-hoc abstractions.

## Ablation logic

Key comparisons:

- M5 vs M2: Does looping matter?
- M5 vs M3: Does the upward loop add value?
- M5 vs M4: Does downward discovery add value?
- M2 vs M1: Is explicit context contrast better than generic reframing?
- M1 vs M0: Is generic reframing itself useful?

## Fairness controls

Use the same:

- base model
- temperature
- tool access
- task information
- random-seed policy

Run both:

1. Equal-token / equal-call budget comparison
2. Unrestricted-method comparison

## Stopping rules

Downward loop stops when:

- no new difference changes constraint/resource/assumption/cost structure, or
- marginal formulation gain is below threshold, or
- max loop budget is reached.

Upward loop stops when:

- removing another context condition makes the solution invalid or noncompetitive, or
- no additional incidental condition can be removed, or
- max loop budget is reached.

## Go / Weak / No-Go criteria

### Go
Continue to a 30-task benchmark if all are broadly true:

- M5 or M2 improves objective downstream success, not just answer richness
- improvement exceeds generic reframing on at least part of the benchmark
- negative-control over-reframing remains bounded
- at least one loop shows measurable ablation value

### Weak
If formulation metrics improve but objective task success does not.

### No-Go
Stop or redesign if:

- M0 ≈ M1 ≈ M2 ≈ M5 on objective success
- M1 ≈ M5 across tasks
- M5 mostly wins by consuming far more tokens/calls
- negative-control tasks show systematic unnecessary reframing
- upward-loop outputs cannot be validated independently of LLM judgment
