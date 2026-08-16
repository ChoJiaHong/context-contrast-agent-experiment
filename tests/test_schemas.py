from context_contrast_exp.runner import load_tasks

def test_pilot_shape():
    tasks=load_tasks("tasks/pilot.jsonl")
    assert len(tasks)==6
    assert len({t.domain for t in tasks})>=4
    assert sum(t.objective_evaluator.type!="human" for t in tasks)>=3
