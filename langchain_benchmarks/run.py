# https://langchain-ai.github.io/langchain-benchmarks/notebooks/tool_usage/benchmark_all_tasks.html
import datetime

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langsmith.client import Client
from langchain_core.prompts import ChatPromptTemplate

from langchain_benchmarks.tool_usage.tasks.multiverse_math import MULTIVERSE_MATH
from tool_usage.agents import StandardAgentFactory
from langchain_benchmarks.rate_limiting import RateLimiter
from langchain.schema.output_parser import StrOutputParser


def run_benchmark():
    llama3 = ChatOllama(model="llama3")
    # using LangChain Expressive Language chain syntax
    # learn more about the LCEL on
    # /docs/concepts/#langchain-expression-language-lcel
    prompt = ChatPromptTemplate.from_template(
        "You are an expert python Fast API programmer, please design a fast API: {prompt}")
    fastApiProgrammerLlama3 = prompt | llama3 | StrOutputParser()

    # Create prompts for the agents
    # Using two prompts because some chat models do not support SystemMessage.
    without_system_message_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "{instructions}\n{question}",
            ),  # Populated from task.instructions automatically
            MessagesPlaceholder("agent_scratchpad"),  # Workspace for the agent
        ]
    )

    with_system_message_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{instructions}"),
            ("human", "{question}"),  # Populated from task.instructions automatically
            MessagesPlaceholder("agent_scratchpad"),  # Workspace for the agent
        ]
    )

    experiment_uuid = "sky25"
    tests = [
        (
            "llama3",
            llama3,
        ),
        (
            "fastApiProgrammerLlama3",
            fastApiProgrammerLlama3
        )
    ]

    client = Client()  # Launch langsmith client for cloning datasets
    today = datetime.date.today().isoformat()
    task = MULTIVERSE_MATH

    for model_name, model in tests:
        prompt = with_system_message_prompt
        rate_limiter = RateLimiter(requests_per_second=1)
        print()
        print(f"Benchmarking {task.name} with model: {model_name}")
        eval_config = task.get_eval_config()

        agent_factory = StandardAgentFactory(
            task, model, prompt, rate_limiter=rate_limiter
        )

        client.run_on_dataset(
            dataset_name=dataset_name,
            llm_or_chain_factory=agent_factory,
            evaluation=eval_config,
            verbose=False,
            project_name=f"{model_name}-{task.name}-{today}-{experiment_uuid}",
            concurrency_level=5,
            project_metadata={
                "model": model_name,
                "id": experiment_uuid,
                "task": task.name,
                "date": today
            },
        )


if __name__ == "__main__":
    run_benchmark()
