from context_contrast_exp.evaluation.metrics import set_scores
from context_contrast_exp.evaluation.objective import evaluate_strategy

def test_empty_sets_are_perfect():
    assert set_scores([],[])=={"precision":1.0,"recall":1.0,"f1":1.0}

def test_alias_and_false_positive():
    result=set_scores(["reefer","paint"],["cold storage"],{"cold storage":["reefer"]})
    assert result["precision"]==0.5 and result["recall"]==1

def test_objective_rules_are_benchmark_owned():
    evaluator={"type":"rules","spec":{"allowed_strategy_families":["simple"]}}
    assert evaluate_strategy("simple",evaluator) is True
    assert evaluate_strategy("ornate",evaluator) is False
    assert evaluate_strategy("anything",{"type":"human","spec":{}}) is None
