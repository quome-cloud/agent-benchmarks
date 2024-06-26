import requests

from quome_agentic_benchmarks.utils.coding import CodeInput, \
    safe_build_and_run_code, AllowedDockerFiles


def eval_prompt_to_frontend(agent_id, prompt_id, result: CodeInput, expected):
    print(f"Result {result}")

    app_prefix = f"{agent_id}_{prompt_id}".lower()

    code_environ = CodeInput(
        files=result['files'],
        dockerfile=AllowedDockerFiles.static_web,
        port=3000
    )

    with safe_build_and_run_code(code_environ, app_prefix=app_prefix) as running_app:
        eval_results = requests.get(f'{running_app.port}')

    return eval_results
