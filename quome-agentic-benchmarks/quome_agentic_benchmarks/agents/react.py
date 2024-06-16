
from langchain.agents import create_react_agent
from langchain_core.runnables import Runnable

from .prompts.base import react_prompt


def agent(llm, tools) -> Runnable:
    if llm is None:
        from langchain_community.llms import Ollama
        llm = Ollama(model="llama3")

    if tools is None:
        from ..tools import TavilySearchResults
        tools = [TavilySearchResults(max_results=1)]

    # Construct the ReAct agent
    return create_react_agent(llm, tools, react_prompt)
