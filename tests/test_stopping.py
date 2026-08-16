from context_contrast_exp.methods.downward_loop import should_stop as downward
from context_contrast_exp.methods.upward_loop import should_stop as upward

def test_downward_patience_and_cap():
    assert downward([{"meaningful_new_difference":False}],1,3)==(True,"patience_exhausted")
    assert downward([{"meaningful_new_difference":True}]*3,2,3)==(True,"max_down_rounds")

def test_upward_stopping():
    assert upward([{"incidental_removed":False}],3)==(True,"no_incidental_context")
    assert upward([{"incidental_removed":True}],3)==(False,"")
