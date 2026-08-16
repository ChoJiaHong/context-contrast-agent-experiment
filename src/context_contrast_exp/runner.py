import json
from pathlib import Path
from pydantic import ValidationError
from .config import ExperimentConfig
from .evaluation.metrics import score_output
from .llm import MockLLMClient, OpenAIClient
from .methods import METHODS
from .schemas import RunRecord, Task

def load_tasks(path: str) -> list[Task]:
    tasks=[]; seen=set()
    for line_no,line in enumerate(Path(path).read_text().splitlines(),1):
        if not line.strip(): continue
        task=Task.model_validate_json(line)
        if task.id in seen: raise ValueError(f"duplicate task id at line {line_no}: {task.id}")
        seen.add(task.id); tasks.append(task)
    return tasks

def run(tasks: list[Task], methods: list[str], runs: int, config: ExperimentConfig, out: str) -> list[RunRecord]:
    unknown=set(methods)-set(METHODS)
    if unknown: raise ValueError(f"unknown methods: {sorted(unknown)}")
    client=MockLLMClient() if config.provider=="mock" else OpenAIClient(config.model,config.temperature)
    records=[]; path=Path(out); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w") as fh:
      for task in tasks:
       for method in methods:
        system=Path(f"prompts/{method}.md").read_text()
        for run_id in range(runs):
          seed=run_id; payload=json.dumps({"task":task.model_dump(),"method":method})
          last_error=None
          for attempt in range(config.format_retries+1):
            try: response=client.generate(system=system,user=payload,seed=seed); break
            except (ValidationError,json.JSONDecodeError) as exc: last_error=exc
          else: raise ValueError(f"malformed output after formatting retries: {last_error}")
          cost=(response.input_tokens*config.approximate_input_cost_per_million+response.output_tokens*config.approximate_output_cost_per_million)/1_000_000
          record=RunRecord(task_id=task.id,domain=task.domain,task_type=task.task_type,method=method,run_id=run_id,seed=seed,model=client.model,output=response.parsed,raw_responses=[response.raw_response],calls=1,input_tokens=response.input_tokens,output_tokens=response.output_tokens,latency_seconds=response.latency_seconds,approximate_cost=cost,metrics=score_output(response.parsed,task),configuration=config.model_dump(),is_mock=config.provider=="mock")
          records.append(record); fh.write(record.model_dump_json()+"\n"); fh.flush()
    return records
