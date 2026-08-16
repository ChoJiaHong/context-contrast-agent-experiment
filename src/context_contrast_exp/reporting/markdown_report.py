import json
from collections import defaultdict
from pathlib import Path
from ..evaluation.statistics import paired_task_differences, summarize

def generate_report(results_path: str, out: str) -> None:
    records=[json.loads(x) for x in Path(results_path).read_text().splitlines() if x.strip()]
    if not records: raise ValueError("results file is empty")
    grouped=defaultdict(list)
    for r in records: grouped[r["method"]].append(r)
    mock=all(r.get("is_mock",False) for r in records)
    lines=["# Context-Contrast Pilot Report","> **"+("SYNTHETIC MOCK — NOT EMPIRICAL EVIDENCE" if mock else "REAL PROVIDER RUN")+"**","## Executive summary","This underpowered six-task pilot cannot support definitive significance claims. Mock values validate the pipeline only." if mock else "Results are exploratory; inspect objective success and negative controls before proceeding.","","## Research questions and hypotheses","Tests H1–H5 from EXPERIMENT_SPEC.md: formulation discovery, downstream success, loop value, bounded over-reframing, and independently useful upward removal.","","## Experiment configuration",f"- Model: {records[0]['model']}\n- Records: {len(records)}\n- Mock: {mock}","","## Benchmark composition"]
    counts=defaultdict(int)
    for r in records: counts[r["task_type"]]+=1
    lines += [", ".join(f"{k}: {v}" for k,v in sorted(counts.items())),"","## Aggregate results table","| Method | Objective mean ± SD | 95% bootstrap CI | Context F1 | Calls | Tokens |","|---|---:|---:|---:|---:|---:|"]
    for method, rs in grouped.items():
        obj=summarize([float(x["metrics"]["objective_success"]) for x in rs]); f1=summarize([x["metrics"]["context_f1"] for x in rs])
        lines.append(f"| {method} | {obj['mean']:.3f} ± {obj['sd']:.3f} | [{obj['ci_low']:.3f}, {obj['ci_high']:.3f}] | {f1['mean']:.3f} | {sum(x['calls'] for x in rs)/len(rs):.1f} | {sum(x['input_tokens']+x['output_tokens'] for x in rs)/len(rs):.1f} |")
    lines += ["","## Per-task results"]
    for task in sorted({r["task_id"] for r in records}):
        rows=[r for r in records if r["task_id"]==task]; lines.append(f"- **{task}:** "+", ".join(f"{r['method']}={int(r['metrics']['objective_success'])}" for r in rows))
    negative=[r for r in records if r["task_type"].startswith("negative")]
    def comparison(left: str, right: str) -> str:
        values=paired_task_differences(records,left,right,"objective_success")
        stats=summarize(values) if values else None
        return "No paired tasks available." if not stats else f"Paired task-level objective difference ({left} − {right}): {stats['mean']:.3f} (95% bootstrap CI [{stats['ci_low']:.3f}, {stats['ci_high']:.3f}]; n={len(values)} tasks)."
    sections=[("Downward-loop ablation",comparison("bidirectional_loop","upward_loop")),("Upward-loop ablation",comparison("bidirectional_loop","downward_loop")),("Full vs single-pass comparison",comparison("bidirectional_loop","context_contrast_single")),("Negative-control / over-reframing analysis",f"Mean over-reframing: {sum(float(r['metrics']['over_reframing']) for r in negative)/max(1,len(negative)):.3f}."),("Efficiency analysis",f"Total calls: {sum(r['calls'] for r in records)}; total tokens: {sum(r['input_tokens']+r['output_tokens'] for r in records)}; approximate cost: {sum(r['approximate_cost'] for r in records):.6f}."),("Failure cases","Review records with objective success false and adjudicate semantic mismatches."),("Threats to validity","Six hand-built tasks are underpowered; alias coverage, model dependence, mock leakage, and evaluator validity limit inference."),("Go / Weak / No-Go decision","Mock run: **No decision**. For real runs apply the predefined criteria without reinterpretation."),("Raw artifact paths and reproduction command",f"- Results: {results_path}\n- Reproduce: python -m context_contrast_exp.cli report --results {results_path} --out {out}")]
    for title,body in sections: lines += ["",f"## {title}",body]
    Path(out).parent.mkdir(parents=True,exist_ok=True); Path(out).write_text("\n".join(lines)+"\n")
