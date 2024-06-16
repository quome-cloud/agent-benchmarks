from quome_agentic_benchmarks.agents.prompts.coding import prompt_to_api_task_prompt
from quome_agentic_benchmarks.tasks.base import BaseTask

PROMPT_TO_API = BaseTask(
    name="prompt_to_api",
    description="From a prompt, generate a working API",
    dataset_id="prompt_to_api_v1",
    task_prompt=prompt_to_api_task_prompt
)