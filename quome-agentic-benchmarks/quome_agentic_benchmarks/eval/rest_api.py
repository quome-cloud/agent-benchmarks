import json
import os

import requests
import pandas as pd

from quome_agentic_benchmarks.utils.coding import RunningProgram, build_and_run_docker, CodeInput, AllowedDockerFiles, safe_build_and_run_code


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

        if 'schemas' in expected:
            for schema in expected['schemas']:
                subeval_name = f'schema_exists-{schema['name']}'
                schemas = api_docs['components']['schemas']
                if schema['name'] in schemas:
                    results['points'] += 5
                    results['successful'].append(subeval_name)
                    if 'properties' in schema:
                        props = schemas[schema['name']]['properties']
                        for p in schema['properties']:
                            if p in props:
                                props_eval_name = f'schema-{schema['name']}-has_prop-{p}'
                                results['points'] += 5
                                results['successful'].append(props_eval_name)

        for route in expected['endpoints']:
            # TODO - check each route exists in api docs
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

            # TODO: Eval with a "Judge" eval model (GPT40)
            # https://huggingface.co/learn/cookbook/en/llm_judge
            # Look up good Judge prompts...

    except:
        print("An Error occurred during evaluation")
        # TODO - Give partial credit?
        app_logs = running_app['container'].logs().decode("utf-8")

        has_exception = 'Error' in app_logs

        if has_exception:
            print("There was a runtime error")
            print(app_logs)


    # TODO: Evaluate the code quality, this can be done by opening the files in the base_dir
    # Does it use a database? (Yes = 20 points)
    # Linters, code security checks, etc.
    # Does it have all the imports and packages that it needs?
    # Does it actually do things? Rather than just fake doing things?

    print(f"Achieved {results['points']} points! {results}")

    with open(os.path.join(running_app['base_dir'], "evaluation_results.json"), "w") as f:
        f.write(json.dumps(results))

    return results


def eval_prompt_to_api(agent_id, prompt_id, code_result: CodeInput, expected):
    print(f"Result {code_result}")

    app_prefix = f"{agent_id}_{prompt_id}".lower()

    with safe_build_and_run_code(code_result, app_prefix=app_prefix) as running_app:
        eval_results = evaluate_running_app(running_app, expected)

    return eval_results


def eval_prompt_to_api_from_dir(dir, expected, run_command="fastapi run main.py", tag=None):
    tag = dir.split("/")[-1]

    with build_and_run_docker(dir, tag=tag, run_command=run_command) as running_app:
        base_url = f"http://0.0.0.0:{running_app['host_port']}"
        evaluate_running_app(running_app, expected)


def fake_post_body(content, schemas):
    obj = {}

def test_crud_endpoints(open_api_spec):
    paths = open_api_spec['paths']
    schemas = open_api_spec['components']['schemas']
    base_url = f"http://0.0.0.0:8000"

    for path, methods in paths.items():
        # Restful conventions - Ending in s implies this endpoint is something like
        # /tweets or /likes
        endpoint = f'{base_url}/path'
        if path[-1] == 's' and 'post' in methods and 'get' in methods:
            # Get all items
            items = requests.get(f'{base_url}/path').json()
            # Post an item
            fake_item = fake_post_body(
                methods['post']['requestBody']['content'],
                schemas
            )

            # Get all items again. Expect new item to be added

        for method, endpoint_info in methods.items():
            #
            # if method == 'post':
            resp = requests.request(method, f'{base_url}/path')
