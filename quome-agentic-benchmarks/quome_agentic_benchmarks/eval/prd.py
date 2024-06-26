

def eval_prompt_to_prd(agent_id, prompt_id, result, expected):
    print(f"Result {result}")

    app_prefix = f"{agent_id}_{prompt_id}".lower()

    # Simple evaluation.
    # Count how many words that were expected are in the result
    points = sum(term in result for term in expected['terms'])

    # May want to explore the LLM judge paradigm
    # https://huggingface.co/learn/cookbook/en/llm_judge

    return points