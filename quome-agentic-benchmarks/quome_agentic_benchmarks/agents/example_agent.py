
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_experimental.llms.ollama_functions import OllamaFunctions
# from langchain_fireworks import ChatFireworks
# from langchain_openai import ChatOpenAI

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import StateGraph

from quome_agentic_benchmarks.tasks.base import TaskData
from quome_agentic_benchmarks.tools import create_api_template
from quome_agentic_benchmarks.utils.coding import extract_code_from_llm_output, CodeInput, \
    AllowedDockerFiles

_SUPPORTED_MODELS = {"llama3", "codellama"}

PLAN_PROMPT = """You are an expert backend coder tasked with creating a working fast API in Python\
Write a development plan including the endpoints needed to accomplish the user's request. \
Use restful API conventions, include the HTTP method, \
the path, and specify each object type and its schema including data types.
"""

CODER_PROMPT = """You are an expert backend coder tasked with creating a working fast API in Python \
Write the best API code possible for the user's request and the initial API outline. \
If the user provides critique, respond with a revised version of your previous attempts. \
Please include 2 files:
- requirements.txt
- main.py

Utilize all the information below as needed: 

------

{content}"""

# TODO: Once we get credits, setup custom model evaluation agents via AWS, Google
# TODO: Running hyperparameter tuning jobs in the cloud


class AgentState(TaskData):
    # task: str # Inherited from TaskInput
    # task_output: dict[str, str] # Inherited from TaskInput
    # task_output: PythonCodeInput

    # Agent state
    plan: str
    code: str


def agent(llm, tools):
    if llm not in _SUPPORTED_MODELS:
        print(f"{llm} is not supported for openai_coder_v1")
        return None

    #model = OllamaFunctions(model=llm, format="json", temperature=0)
    model = ChatOllama(model=llm, temperature=0)

    # TODO - Figure out tool use...
    # if tools:
    #     model.bind_tools(
    #         tools
    #     )

    def input_node(state: TaskData):
        return {
            "task": state['task']
        }

    def plan_node(state: AgentState):
        messages = [
            SystemMessage(content=PLAN_PROMPT),
            HumanMessage(content=state['task'])
        ]
        # If you need to get a single promt from a list of message prompts, can use:
        # prompt = ChatPromptTemplate.from_messages(messages)

        response = model.invoke(messages)
        return {"plan": response.content}

    def coder_node(state: AgentState):
        content = "\n\n".join(state['code'] or [])
        user_message = HumanMessage(
            content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")
        messages = [
            SystemMessage(
                content=CODER_PROMPT.format(content=content)
            ),
            user_message
        ]
        response = model.invoke(messages)
        return {
            "code": response.content
        }

    def finalize_code_node(state: AgentState):
        main_py = extract_code_from_llm_output("main.py", state["code"])
        requirements_txt = extract_code_from_llm_output("requirements.txt", state["code"])
        task_output = CodeInput(
            files={
                "main.py": main_py,
                "requirements.txt": requirements_txt
            },
            dockerfile=AllowedDockerFiles.python,
            run_command="fastapi run main.py"
        )

        return {
            "task_output": task_output
        }

    builder = StateGraph(AgentState)
    builder.add_node("input", input_node)
    builder.add_node("planner", plan_node)
    builder.add_node("coder", coder_node)
    builder.add_node("finalize_code", finalize_code_node)

    builder.add_edge("input", "planner")
    builder.add_edge("planner", "coder")
    builder.add_edge("coder", "finalize_code")
    builder.add_edge("finalize_code", END)

    builder.set_entry_point("input")

    graph = builder.compile()
    graph.name = "example_agent"

    return graph


# https://github.com/langchain-ai/langgraph/blob/main/examples/storm/storm.ipynb
if __name__ == '__main__':
    a = agent("llama3", [create_api_template])
    resp = a.invoke({"task": "Create an API for a calendar"})
    print(resp)

