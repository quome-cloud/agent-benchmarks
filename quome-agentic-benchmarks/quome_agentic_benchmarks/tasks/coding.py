from quome_agentic_benchmarks.agents.prompts.coding import prompt_to_api_task_prompt, prompt_to_prd_task_prompt, prompt_to_frontend_task_prompt
from quome_agentic_benchmarks.tasks.base import BaseTask

prompt_to_api = BaseTask(
    name="prompt_to_api",
    description="From a prompt, generate a working API",
    dataset_id="prompt_to_api_v1",
    task_prompt=prompt_to_api_task_prompt
)

prompt_to_prd = BaseTask(
    name="prompt_to_prd",
    description="From a prompt, generate a product requirements docs",
    dataset_id="prompt_to_prd_v1",
    task_prompt=prompt_to_prd_task_prompt
)

prompt_to_frontend = BaseTask(
    name="prompt_to_frontend",
    description="From a prompt, generate a frontend for an app",
    dataset_id="prompt_to_frontend_v1",
    task_prompt=prompt_to_frontend_task_prompt
)