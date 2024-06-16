from . import react, openai_coder_v1

agent_lookup = {
    "react": react.agent,
    "openai_coder_v1": openai_coder_v1.agent
}

all_agents = agent_lookup.keys()


def get_agents(agent_names):
    return [agent_lookup[agent_name] for agent_name in agent_names if agent_name in agent_lookup]

