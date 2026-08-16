from context_contrast_exp.config import ExperimentConfig
from context_contrast_exp.runner import load_tasks, run

def test_runner_persists_per_call_metadata(tmp_path):
    task = load_tasks("tasks/pilot.jsonl")[:1]
    destination = tmp_path / "run.jsonl"
    records = run(task, ["downward_loop"], 1, ExperimentConfig(), str(destination))
    assert len(records) == 1
    record = records[0]
    assert record.calls == 2
    assert len(record.call_records) == record.calls
    assert [call.call_index for call in record.call_records] == [1, 2]
    assert all(call.task_id == task[0].id for call in record.call_records)
    assert all(call.action == "downward_discovery_round" for call in record.call_records)
    assert destination.read_text().count("\n") == 1

def test_equal_and_unrestricted_call_caps_are_distinct():
    assert ExperimentConfig(budget_mode="equal_calls", equal_call_budget=2, max_total_calls=8).effective_call_cap == 2
    assert ExperimentConfig(budget_mode="unrestricted", equal_call_budget=2, max_total_calls=8).effective_call_cap == 8
