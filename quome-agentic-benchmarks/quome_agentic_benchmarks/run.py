# https://langchain-ai.github.io/langchain-benchmarks/notebooks/tool_usage/benchmark_all_tasks.html
import importlib

from langchain_community.llms.ollama import Ollama


# from quome_agentic_benchmarks.agents import get_agents
from quome_agentic_benchmarks.tasks.base import run_task
from quome_agentic_benchmarks.utils.benchmark import load_modules, load_members

from tools import *


def run_benchmark(model_names, tool_names, task_names, agent_names):
    print(f"Running benchmark: {model_names=}, {task_names=}, {tool_names=}, {agent_names=}")
    tools = load_members(tool_names, 'quome_agentic_benchmarks.tools')
    coding_tasks = load_members(task_names, 'quome_agentic_benchmarks.tasks.coding')
    agents = load_modules(agent_names, 'quome_agentic_benchmarks.agents')

    for task in coding_tasks:
        print(f"Running Task: {task.name}")
        for a in agents:
            for model in model_names:
                agent_to_test = a.agent(
                    llm=model,
                    tools=tools
                )
                if not agent_to_test:
                    # Model not supported for agent
                    continue

                print(f"Evaluating agent {agent_to_test.name} with model {model}")

                agent_id = f"{model}-{agent_to_test.name}"

                run_task(agent_id, agent_to_test, task, tools)


if __name__ == "__main__":
    run_benchmark(["llama3", "gpt-3.5-turbo"], ["create_api_template"], ["prompt_to_api"], ["openai_coder_v1", "example_agent"])
