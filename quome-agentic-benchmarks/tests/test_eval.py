from quome_agentic_benchmarks.eval.rest_api import eval_prompt_to_api_from_dir

app_dir = '/Users/cjoverbay/code/qudb/agent-benchmarks/quome-agentic-benchmarks/quome_agentic_benchmarks/generated_apps/2024-06-26/llama3-example_agent_twitter/llama3-example_agent_twitter-08_05_10'

expected = {
    'schemas': [
        {
            'name': "User",
            'properties': ['username']
        },
        {
            'name': "Tweet",
            'properties': ['content', 'reply']
        }
    ],
    'endpoints': ["users", "followers", "following", "like", "likes", "login", "tweets"],  # Create, read, update, delete
}
if __name__ == '__main__':
    result = eval_prompt_to_api_from_dir(app_dir, expected, run_command="python main.py")
