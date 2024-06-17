import json
import os

import requests
import pandas as pd

from quome_agentic_benchmarks.utils.coding import PythonCodeInput, safe_build_and_run_python_code, \
    build_and_run_docker_python, RunningProgram


def evaluate_running_app(running_app: RunningProgram, expected: dict):
    results = {'eval': 'prompt-to-api', 'points': 0, 'successful': [], 'failed': []}

    base_url = f"http://0.0.0.0:{running_app['host_port']}"
    try:
        resp = requests.get(f'{base_url}/docs')
        if resp.status_code == 200:
            results['points'] += 10
            results['successful'].append('ping')
        else:
            results['failed'].append('ping')

        api_docs = json.loads(requests.get(f"{base_url}/openapi.json").text)

        for route in expected['endpoints']:
            # TODO - check each route exists in api docs
            print(api_docs)
            subeval_name = f'path_exists-{route}'

            if any(route in path for path in api_docs['paths'].keys()):
                # Path "/api/tweets" will match /tweets
                results['points'] += 5
                results['successful'].append(subeval_name)
            else:
                results['failed'].append(subeval_name)

            # TODO, check create read update and delete methods...
            # 1. Check method / path exists
            # 2. Verify functionality (actually call the methods)
            # Actually call the POST /tweets endpoint, then the GET /tweets endpoint
            # JSON schema -> endpoint input -> Fake an input str: "abc" int: 42
            # Verify that new input was added to list.
            # Expect the API to have created a tweet

    except:
        print("An Error occurred during evaluation")
        # TODO - Give partial credit?
        app_logs = running_app['container'].logs()

        has_exception = 'Error' in app_logs

        if has_exception:
            print("There was a runtime error")
            print(app_logs)


    # TODO: Evaluate the code quality, this can be done by opening the files in the base_dir
    # Does it use a database? (Yes = 20 points)
    # Linters, code security checks, etc.

    print(f"Achieved {results['points']} points! {results}")

    with open(os.path.join(running_app['base_dir'], "evaluation_results.json"), "w") as f:
        f.write(json.dumps(results))

    return results


def eval_prompt_to_api(agent_id, prompt_id, result, expected):
    print(f"Result {result}")

    app_prefix = f"{agent_id}_{prompt_id}".lower()


    code_environ = PythonCodeInput(
        main=result['main'],
        requirements=result['requirements'],
        run_command='fastapi run main.py'
    )

    with safe_build_and_run_python_code(code_environ, app_prefix=app_prefix) as running_app:
        eval_results = evaluate_running_app(running_app, expected)

    return eval_results


def eval_prompt_to_api_from_dir(dir, expected):
    with build_and_run_docker_python(dir, "test", run_command="python main.py") as running_app:
        base_url = f"http://0.0.0.0:{running_app['host_port']}"
        evaluate_running_app(running_app, dir)
