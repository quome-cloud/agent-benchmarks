from quome_agentic_benchmarks.tasks.coding import PROMPT_TO_API

task_lookup = {
    "prompt_to_api": PROMPT_TO_API,
}

valid_tasks = task_lookup.keys()


def get_tasks(task_names):
    return [task_lookup[name] for name in task_names if name in task_lookup]


