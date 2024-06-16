import dataclasses
from typing import List, Tuple, Callable, Any

from tabulate import tabulate


@dataclasses.dataclass(frozen=True)
class Dataset:
    """A definition of a Dataset."""

    id: str
    """The name / id of the dataset"""

    description: str
    """Description of the dataset for a data science practitioner."""

    rows: List[Tuple[Any, Any]]
    """List of training examples. Typically (Prompt,EvaluationData)"""

    # Agent_id, prompt_id, result, expected_result_data
    evaluate: Callable[[str, str, Any, Any], Any]
    """Evaluates an output against the expected output."""

    @property
    def _table(self) -> List[List[str]]:
        """Return a table representation of the dataset."""
        return [
            ["Id", self.id],
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

