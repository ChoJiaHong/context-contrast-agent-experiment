from context_contrast_exp.evaluation.metrics import set_scores

def test_empty_sets_are_perfect():
    assert set_scores([],[])=={"precision":1.0,"recall":1.0,"f1":1.0}

def test_alias_and_false_positive():
    result=set_scores(["reefer","paint"],["cold storage"],{"cold storage":["reefer"]})
    assert result["precision"]==0.5 and result["recall"]==1
