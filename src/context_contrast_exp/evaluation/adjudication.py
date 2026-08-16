import json
from pathlib import Path

from .matching import matched_sets
from ..runner import load_tasks


FIELD_MAP = {
    "relevant_context_differences": "relevant_context_differences",
    "constraints": "changed_constraints",
    "resources": "available_resources",
    "assumption_changes": "changed_assumptions",
    "cost_structure_changes": "changed_cost_structure",
    "essential_context_conditions": "essential_context_conditions",
}


def export_ambiguous_cases(results_path: str, tasks_path: str, out: str) -> int:
    """Export unmatched set items for blinded human or external adjudication."""
    tasks = {task.id: task for task in load_tasks(tasks_path)}
    records = [json.loads(line) for line in Path(results_path).read_text().splitlines() if line.strip()]
    cases: list[dict] = []
    for record in records:
        task = tasks[record["task_id"]]
        aliases = task.ground_truth.aliases
        for output_field, truth_field in FIELD_MAP.items():
            predicted = record["output"].get(output_field, [])
            expected = getattr(task.ground_truth, truth_field)
            normalized_predicted, normalized_expected = matched_sets(predicted, expected, aliases)
            if normalized_predicted == normalized_expected:
                continue
            cases.append({
                "case_id": f"{record['task_id']}:{record['method']}:{record['run_id']}:{output_field}",
                "task_id": record["task_id"],
                "method": record["method"],
                "run_id": record["run_id"],
                "field": output_field,
                "predicted": predicted,
                "expected_alias_set": expected,
                "adjudication": None,
                "notes": "",
            })
    destination = Path(out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(json.dumps(case, ensure_ascii=False) + "\n" for case in cases))
    return len(cases)
