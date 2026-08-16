import json
from pathlib import Path
from pydantic import ValidationError
from .config import ExperimentConfig
from .evaluation.metrics import score_output
from .llm import MockLLMClient, OpenAIClient
from .methods import METHODS, get_executor
from .schemas import CallRecord, RunRecord, Task

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
    call_cap=config.effective_call_cap
    records=[]; path=Path(out); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w") as fh:
      for task in tasks:
       for method in methods:
        system=Path(f"prompts/{method}.md").read_text()
        for run_id in range(runs):
          seed=run_id
          call_actions: list[str] = []
          def generate(action: str, data: dict):
            payload=json.dumps({"method":method,"action":action,**data})
            last_error=None
            for _attempt in range(config.format_retries+1):
              try:
                response=client.generate(system=system,user=payload,seed=seed)
                call_actions.append(action)
                return response
              except (ValidationError,json.JSONDecodeError) as exc: last_error=exc
            raise ValueError(f"malformed output after formatting retries: {last_error}")
          output,responses=get_executor(method)(task,generate,max_rounds=min(config.max_down_rounds,call_cap),max_up_rounds=min(config.max_up_rounds,max(0,call_cap-1)),patience=config.patience,max_total_calls=call_cap)
          input_tokens=sum(r.input_tokens for r in responses); output_tokens=sum(r.output_tokens for r in responses)
          cost=(input_tokens*config.approximate_input_cost_per_million+output_tokens*config.approximate_output_cost_per_million)/1_000_000
          call_records=[CallRecord(call_index=index,action=action,model=client.model,method=method,task_id=task.id,run_id=run_id,input_tokens=response.input_tokens,output_tokens=response.output_tokens,latency_seconds=response.latency_seconds,raw_response=response.raw_response,parsed=response.parsed) for index,(action,response) in enumerate(zip(call_actions,responses,strict=True),1)]
          record=RunRecord(task_id=task.id,domain=task.domain,task_type=task.task_type,method=method,run_id=run_id,seed=seed,model=client.model,output=output,raw_responses=[r.raw_response for r in responses],call_records=call_records,calls=len(responses),input_tokens=input_tokens,output_tokens=output_tokens,latency_seconds=sum(r.latency_seconds for r in responses),approximate_cost=cost,metrics=score_output(output,task),configuration=config.model_dump(),is_mock=config.provider=="mock")
          records.append(record); fh.write(record.model_dump_json()+"\n"); fh.flush()
    return records
