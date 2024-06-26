import importlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class EvaluationMetadata:
    agent_id: str
    task_id: str
    task_row: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def start(self):
        self.start_time = datetime.now(timezone.utc)

    def end(self):
        self.end_time = datetime.now(timezone.utc)

    @property
    def output_dir(self) -> str:
        directory = os.path.join(
            "benchmark_results",
            str(self.start_time.strftime("%Y%m%d-%H%M%S")),
            self.task_id,
            self.agent_id,
            self.task_row
        )
        # Make dir if not exists.
        Path(directory).mkdir(parents=True, exist_ok=True)
        return directory

    def log_agent_call_chain(self, chunks: List[Dict[str, Any]]):
        # TODO: Can support streaming logs? Then we can ensure progress is logged.
        # TODO: Support retrying failed runs? Note, checkpoints are available in langgraph.
        print(chunks)
        with open(os.path.join(self.output_dir, 'agent.log'), 'w') as log_file:
            # Only works for JSON-serializable data...
            # TODO: Fix to support generic python agent state.
            log_data = [next(iter(chunk.items())) for chunk in chunks]
            try:
                json.dump(log_data, log_file)
            except TypeError:
                # Not JSON serializable, write as string
                log_file.write(str(log_data))


def get_benchmark_output_dir(agent_id, task_name, task_row_name, eval_end_date):
    return os.path.join("benchmark_results")


def load_modules(module_names, package, relative_package=''):
    return [importlib.import_module(f'{relative_package}.{module}', package) for module in module_names]


def load_members(attribute_names, module):
    module = importlib.import_module(module)
    return [getattr(module, attribute) for attribute in attribute_names]

