import argparse, json
from datetime import datetime, timezone
from pathlib import Path
from .config import ExperimentConfig
from .methods import METHODS
from .reporting import generate_report
from .runner import load_tasks, run

def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="cc-exp"); sub=p.add_subparsers(dest="command",required=True)
    v=sub.add_parser("validate-tasks"); v.add_argument("tasks")
    for name in ("run","run-all"):
        s=sub.add_parser(name); s.add_argument("--tasks",required=True); s.add_argument("--runs",type=int,default=5); s.add_argument("--config"); s.add_argument("--out")
        if name=="run": s.add_argument("--method",required=True,choices=METHODS)
    a=sub.add_parser("analyze"); a.add_argument("--results",required=True)
    r=sub.add_parser("report"); r.add_argument("--results",required=True); r.add_argument("--out",required=True)
    return p

def main(argv: list[str]|None=None) -> int:
    args=parser().parse_args(argv)
    if args.command=="validate-tasks":
        tasks=load_tasks(args.tasks); types={t.task_type for t in tasks}; domains={t.domain for t in tasks}
        required={"resource-emergence","assumption-breaking","constraint-changing","cost-structure-changing","negative-control-irrelevant","negative-control-conventional"}
        if len(tasks)!=6 or types!=required or len(domains)<4: raise ValueError("pilot must contain six required task types across at least four domains")
        print(f"valid: {len(tasks)} tasks, {len(domains)} domains"); return 0
    if args.command in {"run","run-all"}:
        config=ExperimentConfig.load(args.config); stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); out=args.out or f"results/{stamp}.jsonl"
        methods=[args.method] if args.command=="run" else list(METHODS); records=run(load_tasks(args.tasks),methods,args.runs,config,out)
        print(f"wrote {len(records)} records to {out}"); return 0
    if args.command=="analyze":
        rows=[json.loads(x) for x in Path(args.results).read_text().splitlines() if x.strip()]
        for method in sorted({x["method"] for x in rows}):
            subset=[x for x in rows if x["method"]==method]; print(f"{method}: objective_success={sum(x['metrics']['objective_success'] for x in subset)/len(subset):.3f}")
        return 0
    generate_report(args.results,args.out); print(f"wrote {args.out}"); return 0

if __name__=="__main__": raise SystemExit(main())
