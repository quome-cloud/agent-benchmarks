# https://langchain-ai.github.io/langchain-benchmarks/notebooks/tool_usage/benchmark_all_tasks.html
from langchain_community.llms.ollama import Ollama


from quome_agentic_benchmarks.agents import get_agents
from quome_agentic_benchmarks.tasks import get_tasks
from quome_agentic_benchmarks.tasks.base import run_task
from quome_agentic_benchmarks.tasks.coding import PROMPT_TO_API
from quome_agentic_benchmarks.tools import get_tools


def run_benchmark(model_names, tool_names, task_names, agent_names):
    print(f"Running benchmark: {model_names=}, {task_names=}, {tool_names=}, {agent_names=}")
    tools = get_tools(tool_names)
    tasks = get_tasks(task_names)
    agents = get_agents(agent_names)

    for task in tasks:
        print(f"Running Task: {task.name}")
        for agent_factory in agents:
            for model in model_names:
                agent_to_test = agent_factory(
                    llm=Ollama(model=model),
                    tools=tools
                )
                print(f"Evaluating agent {agent_to_test.name} on model {model}")

                agent_id = f"{model}-{agent_to_test.name}"

                run_task(agent_id, agent_to_test, task, tools)


if __name__ == "__main__":
    run_benchmark(["llama3"], ["create_api_template"], ["prompt_to_api"], ["openai_coder_v1"])
