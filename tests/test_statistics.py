from context_contrast_exp.evaluation.statistics import paired_task_differences, summarize

def test_summary_is_deterministic_and_has_sd():
    assert summarize([0.0, 1.0], seed=7, samples=100) == summarize([0.0, 1.0], seed=7, samples=100)
    assert summarize([0.0, 1.0], samples=100)["sd"] > 0

def test_paired_differences_average_runs_within_task():
    rows = [
        {"task_id":"a","method":"full","metrics":{"score":1}},
        {"task_id":"a","method":"full","metrics":{"score":0}},
        {"task_id":"a","method":"single","metrics":{"score":0}},
        {"task_id":"b","method":"full","metrics":{"score":1}},
        {"task_id":"b","method":"single","metrics":{"score":1}},
    ]
    assert paired_task_differences(rows,"full","single","score") == [0.5, 0.0]

def test_paired_differences_skip_unadjudicated_values():
    rows = [
        {"task_id":"a","method":"full","metrics":{"score":None}},
        {"task_id":"a","method":"single","metrics":{"score":0}},
    ]
    assert paired_task_differences(rows,"full","single","score") == []
