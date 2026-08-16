from context_contrast_exp.methods.downward_loop import should_stop as downward
from context_contrast_exp.methods.upward_loop import should_stop as upward

def test_downward_patience_and_cap():
    assert downward([{"meaningful_new_difference":False}],1,3)==(True,"patience_exhausted")
    assert downward([{"meaningful_new_difference":True}]*3,2,3)==(True,"max_down_rounds")

def test_upward_stopping():
    assert upward([{"incidental_removed":False}],3)==(True,"no_incidental_context")
    assert upward([{"incidental_removed":True}],3)==(False,"")

class FakeOutput:
    def __init__(self, *, differences=None, constraints=None, essential=None):
        self.relevant_context_differences = differences or []
        self.constraints = constraints or []
        self.resources = []
        self.assumption_changes = []
        self.cost_structure_changes = []
        self.essential_context_conditions = essential or []
        self.reasoning_trace = []
        self.stop_reason = ""
    def model_copy(self, *, update):
        self.__dict__.update(update)
        return self
    def model_dump(self):
        return dict(self.__dict__)

class FakeResponse:
    def __init__(self, output):
        self.parsed = output

class FakeTask:
    context_facts = ["incidental", "essential"]
    def model_dump(self):
        return {"id": "fake"}

def test_downward_execute_exposes_each_round():
    from context_contrast_exp.methods.downward_loop import execute
    def generate(_action, _data):
        return FakeResponse(FakeOutput(differences=["new"], constraints=["changed"]))
    output, responses = execute(FakeTask(), generate, max_rounds=4, patience=1)
    assert len(responses) == 2
    assert output.stop_reason == "patience_exhausted"
    assert output.reasoning_trace[0]["meaningful_new_difference"] is True
    assert output.reasoning_trace[1]["meaningful_new_difference"] is False

def test_upward_execute_uses_counterfactual_conditions():
    from context_contrast_exp.methods.upward_loop import execute
    calls = []
    def generate(action, data):
        calls.append((action, data))
        essential = [data["removed_condition"]] if action == "counterfactual_removal_test" and data["removed_condition"] == "essential" else []
        return FakeResponse(FakeOutput(essential=essential))
    output, _ = execute(FakeTask(), generate, max_rounds=3)
    assert [data["removed_condition"] for action, data in calls if action == "counterfactual_removal_test"] == ["incidental", "essential"]
    assert output.stop_reason == "no_incidental_context"
