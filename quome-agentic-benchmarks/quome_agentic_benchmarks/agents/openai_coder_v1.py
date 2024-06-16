
from typing import TypedDict, List

from langchain_core.messages import SystemMessage, HumanMessage

from langchain_experimental.llms.ollama_functions import OllamaFunctions
#from ._temp_langchain_overrides.ollama_functions import OllamaFunctions

from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama

from quome_agentic_benchmarks.tasks.base import TaskData
from quome_agentic_benchmarks.tools import get_tools
from quome_agentic_benchmarks.utils.coding import extract_code_from_llm_output, PythonCodeInput

memory = SqliteSaver.from_conn_string(":memory:")

# model = ChatOllama(model="llama3")  # Doesn't work with structured output... See OllamaFunctions instead
# model = OllamaFunctions(model="llama3", format="json", temperature=0)  # Temp 0 = less creative, more deterministic


class AgentState(TaskData):
    # task: str # Inherited from TaskInput
    # task_output: dict[str, str] # Inherited from TaskInput
    # task_output: PythonCodeInput

    # Agent state
    plan: str
    draft: str
    critique: str
    content: List[str]
    # Settings
    revision_number: int
    max_revisions: int


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
REFLECTION_PROMPT = """You are a senior software engineer with expertise in Python and Fast API. \
You are conducting code review for junior software engineer. \
Please provide a list of actionable critiques and recommendations for the MR \
Check edge cases and check functionality of the code"""

RESEARCH_PLAN_PROMPT = """You are a technical product manager charged with providing information that can \
be used by the developer to build the following fast API. Create a list of search queries that would help \
find relevant product and technical information when building the API. \
Only generate 3 queries max."""

RESEARCH_CRITIQUE_PROMPT = """You are a technical product manager charged with providing information that can \
be used by the senior developers to critique and code review the following Python code / fast API (as outlined below). \
Generate a list of search queries that will gather any relevant information. Only generate 3 queries max."""

from langchain_core.pydantic_v1 import BaseModel

class Queries(BaseModel):
    queries: List[str]


def agent(llm, tools) -> Runnable:
    #model = OllamaFunctions(model="llama3")

    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    if tools:
        model.bind_tools(tools)

    def input_node(state: TaskData):
        return {
            "task": state['task'],
            # Set initial state for agent
            "max_revisions": 2,
            "revision_number": 1
        }

    def plan_node(state: AgentState):
        messages = [
            SystemMessage(content=PLAN_PROMPT),
            HumanMessage(content=state['task'])
        ]
        response = model.invoke(messages)
        return {"plan": response.content}

    def research_plan_node(state: AgentState):
        queries = model.with_structured_output(Queries).invoke([
            SystemMessage(content=RESEARCH_PLAN_PROMPT),
            HumanMessage(content=state['task'])
        ])
        content = state['content'] or []
        # TODO - Implement search feature for research
        # Could use API search docs, could also simply use google search or duck duck go? Custom?
        # Tavily seems interesting here, but payed service. The question -> Answer search seems useful

        # for q in queries.queries:
        #     response = tavily.search(query=q, max_results=2)
        #     for r in response['results']:
        #         content.append(r['content'])
        return {"content": content}

    def generation_node(state: AgentState):
        content = "\n\n".join(state['content'] or [])
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
            "draft": response.content,
            "revision_number": state.get("revision_number", 1) + 1
        }

    def finalize_code_node(state: AgentState):
        main_py = extract_code_from_llm_output("main.py", state["draft"])
        requirements_txt = extract_code_from_llm_output("requirements.txt", state["draft"])
        task_output = PythonCodeInput(
            main=main_py,
            requirements=requirements_txt,
        )

        return {
            "task_output": task_output
        }

    def reflection_node(state: AgentState):
        messages = [
            SystemMessage(content=REFLECTION_PROMPT),
            HumanMessage(content=state['draft'])
        ]
        response = model.invoke(messages)
        return {"critique": response.content}

    def research_critique_node(state: AgentState):
        queries = model.with_structured_output(Queries).invoke([
            SystemMessage(content=RESEARCH_CRITIQUE_PROMPT),
            HumanMessage(content=state['critique'])
        ])
        content = state['content'] or []
        # for q in queries.queries:
        #     response = tavily.search(query=q, max_results=2)
        #     for r in response['results']:
        #         content.append(r['content'])
        return {"content": content}

    def should_continue(state):
        if state["revision_number"] > state["max_revisions"]:
            return "finalize_code"
        return "reflect"

    builder = StateGraph(AgentState)
    builder.add_node("input", input_node)
    builder.add_node("planner", plan_node)
    builder.add_node("generate", generation_node)
    builder.add_node("reflect", reflection_node)
    builder.add_node("research_plan", research_plan_node)
    builder.add_node("research_critique", research_critique_node)
    builder.add_node("finalize_code", finalize_code_node)

    builder.set_entry_point("input")

    builder.add_conditional_edges(
        "generate",
        should_continue,
        {"reflect": "reflect", "finalize_code": "finalize_code"}
    )

    builder.add_edge("input", "planner")
    builder.add_edge("planner", "research_plan")
    builder.add_edge("research_plan", "generate")

    builder.add_edge("reflect", "research_critique")
    builder.add_edge("research_critique", "generate")
    builder.add_edge("finalize_code", END)

    graph = builder.compile(checkpointer=memory)

    return graph


if __name__ == "__main__":
    # Example
    tools = get_tools(["search_fast_api_docs"])
    graph = agent(None, tools)
    thread = {"configurable": {"thread_id": "1"}}
    for s in graph.stream({
        'task': "Write an API for a Twitter clone. It should include Tweets, Users, and Follows."
    }, thread):
        print(s)
