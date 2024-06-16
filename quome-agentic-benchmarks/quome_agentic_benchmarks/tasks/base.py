import dataclasses
import string
from typing import List, TypedDict

from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from tabulate import tabulate

from quome_agentic_benchmarks.datasets import get_dataset
from quome_agentic_benchmarks.datasets.base import Dataset


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


def run_task(agent_id: str, agent_runnable: Runnable, task: BaseTask, tools):
    task_prompt = string.Template(task.task_prompt)

    for task_row, expected in task.dataset.rows:
        prompt = task_row['prompt']
        prompt_id = task_row['name']
        # executor = AgentExecutor(agent=agent_runnable, tools=tools)
        instruction_prompt = task_prompt.substitute(prompt=prompt)
        thread_config = {"configurable": {"thread_id": "1"}}  # Thread needed for checkpointing.
        # Look at other methods (besides invoke) - Stream, Astream
        resp: TaskData = agent_runnable.invoke({"task": instruction_prompt}, thread_config)
        task_output = resp['task_output']
        eval_results = task.dataset.evaluate(agent_id, prompt_id, task_output, expected)
