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

def test_optional_secondary_matcher_does_not_replace_primary():
    from context_contrast_exp.evaluation.matching import secondary_matches
    class Matcher:
        def similarity(self, predicted, expected):
            return 0.9 if predicted[0] == expected[0] else 0.1
    assert secondary_matches(["cold locker"], ["chilled capacity"], Matcher()) == [("cold locker", "chilled capacity", 0.9)]
    assert set_scores(["cold locker"], ["chilled capacity"])["f1"] == 0.0
