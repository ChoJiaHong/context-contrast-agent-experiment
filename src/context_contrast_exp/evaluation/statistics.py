import random, statistics

def summarize(values: list[float], seed: int=42, samples: int=2000) -> dict[str,float]:
    if not values: return {"mean":0.0,"sd":0.0,"ci_low":0.0,"ci_high":0.0}
    rng=random.Random(seed); means=sorted(statistics.mean(rng.choices(values,k=len(values))) for _ in range(samples))
    return {"mean":statistics.mean(values),"sd":statistics.stdev(values) if len(values)>1 else 0.0,"ci_low":means[int(.025*samples)],"ci_high":means[min(samples-1,int(.975*samples))]}


def paired_task_differences(records: list[dict], left: str, right: str, metric: str) -> list[float]:
    """Pair method means within tasks, never unrelated independent runs."""
    task_values: dict[str, dict[str, list[float]]] = {}
    for record in records:
        if record["method"] not in {left, right}:
            continue
        task_values.setdefault(record["task_id"], {}).setdefault(record["method"], []).append(float(record["metrics"][metric]))
    differences=[]
    for methods in task_values.values():
        if left in methods and right in methods:
            differences.append(statistics.mean(methods[left])-statistics.mean(methods[right]))
    return differences
