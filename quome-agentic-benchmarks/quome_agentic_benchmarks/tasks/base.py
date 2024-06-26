import dataclasses
import string
from datetime import datetime
from typing import List, TypedDict

from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from tabulate import tabulate

from quome_agentic_benchmarks.datasets import get_dataset
from quome_agentic_benchmarks.datasets.base import Dataset
from quome_agentic_benchmarks.utils.benchmark import get_benchmark_output_dir, EvaluationMetadata


class TaskData(TypedDict):
    task: str  # Specifies the task the model should perform.
    task_output: dict[str, str]  # File name -> File contents. Will want a nicer interface later.


@dataclasses.dataclass(frozen=True)
class BaseTask:
    """A definition of a task."""

    name: str
    """The name of the environment."""

    dataset_id: str
    """The ID of the langsmith public dataset.

    This dataset contains expected inputs/outputs for the environment, and
    can be used to evaluate the performance of a model/agent etc.
    """

    description: str
    """Description of the task for a data science practitioner.

    This can contain information about the task, the dataset, the tools available
    etc.
    """

    task_prompt: str
    """A wrapper around the user prompt that provides a task prompt."""

    @property
    def dataset(self) -> Dataset:
        return get_dataset(self.dataset_id)

    @property
    def _table(self) -> List[List[str]]:
        """Return a table representation of the environment."""
        return [
            ["Name", self.name],
            ["Type", self.type],
            ["Dataset ID", self.dataset_id],
            ["Description", self.description],
        ]

    def _repr_html_(self) -> str:
        """Return an HTML representation of the environment."""
        return tabulate(
            self._table,
            tablefmt="unsafehtml",
        )

    @property
    def type(self) -> str:
        """Return the type of the task."""
        return self.__class__.__name__


def run_task(agent_id: str, agent_runnable: Runnable, task: BaseTask, tools, benchmark_start: datetime):
    task_prompt = string.Template(task.task_prompt)
    task_id = task.name

    for task_row, expected in task.dataset.rows:
        prompt = task_row['prompt']
        task_row_id = task_row['name']
        # executor = AgentExecutor(agent=agent_runnable, tools=tools)
        instruction_prompt = task_prompt.substitute(prompt=prompt)
        thread_config = {"configurable": {"thread_id": "1"}}  # Thread needed for checkpointing
        # See Runnable methods for other methods - Stream, Astream, astream_log, batch, etc.
        # TODO - Possible to do batch here. Particularly useful when using model services like Open AI.

        eval_metadata = EvaluationMetadata(
            agent_id, task_id, task_row_id, benchmark_start
        )

        eval_metadata.start()
        # Start the task
        chunks = []
        for chunk in agent_runnable.stream({"task": instruction_prompt}, thread_config):
            print(chunk)
            chunks.append(chunk)  # Careful with model streaming outputs here, could be a lot of chunks...
        # End the task, get the task_output from final dict
        eval_metadata.end()
        task_output = list(chunks[-1].values())[-1]['task_output']

        eval_metadata.log_agent_call_chain(chunks)

        # resp: TaskData = agent_runnable.invoke({"task": instruction_prompt}, thread_config)
        # task_output = final_output['task_output']
        eval_results = task.dataset.evaluate(eval_metadata, task_output, expected)
