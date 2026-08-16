from .matching import matched_sets
from .objective import evaluate_strategy

def set_scores(predicted: list[str], expected: list[str], aliases: dict[str,list[str]]|None=None) -> dict[str,float]:
    p,e=matched_sets(predicted,expected,aliases); tp=len(p&e)
    precision=tp/len(p) if p else (1.0 if not e else 0.0); recall=tp/len(e) if e else 1.0
    return {"precision":precision,"recall":recall,"f1":2*precision*recall/(precision+recall) if precision+recall else 0.0}

def score_output(output, task):
    gt=task.ground_truth; aliases=gt.aliases
    differences=set_scores(output.relevant_context_differences,gt.relevant_context_differences,aliases)
    essential=set_scores(output.essential_context_conditions,gt.essential_context_conditions,aliases)
    cost=set_scores(output.cost_structure_changes,gt.changed_cost_structure,aliases)
    negative=task.task_type.startswith("negative-control")
    over=negative and (output.strategy_family not in gt.valid_strategy_families or len(output.relevant_context_differences)>len(gt.relevant_context_differences))
    objective=evaluate_strategy(output.strategy_family,task.objective_evaluator.model_dump())
    return {"context_precision":differences["precision"],"context_recall":differences["recall"],"context_f1":differences["f1"],"constraint_recall":set_scores(output.constraints,gt.changed_constraints,aliases)["recall"],"resource_recall":set_scores(output.resources,gt.available_resources,aliases)["recall"],"assumption_recall":set_scores(output.assumption_changes,gt.changed_assumptions,aliases)["recall"],"cost_structure_recall":cost["recall"],"false_context_difference_rate":1-differences["precision"],"essential_context_precision":essential["precision"],"essential_context_recall":essential["recall"],"incidental_context_removal_rate":essential["precision"],"objective_success":objective,"strategy_validity":output.strategy_family in gt.valid_strategy_families,"over_reframing":over}
