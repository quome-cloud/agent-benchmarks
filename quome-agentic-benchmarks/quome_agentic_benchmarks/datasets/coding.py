import json

import requests

from quome_agentic_benchmarks.datasets.base import Dataset
from quome_agentic_benchmarks.utils.coding import safe_build_and_run_python_code, PythonCodeInput


def eval_prompt_to_api(agent_id, prompt_id, result, expected):
    print(f"Result {result}")

    app_prefix = f"{agent_id}_{prompt_id}"

    points = 0

    code_environ = PythonCodeInput(
        main=result['main'],
        requirements=result['requirements'],
        run_command='fastapi run main.py'
    )

    with safe_build_and_run_python_code(code_environ, app_prefix=app_prefix) as running_app:
        base_url = f"http://0.0.0.0:{running_app['host_port']}"

        try:
            resp = requests.get(f'{base_url}/docs')
            if resp.status_code == 200:
                points += 10

            api_docs = json.loads(requests.get(f"{base_url}/openapi.json").text)

            for route in expected['endpoints']:
                # TODO - check each route exists in api docs
                print(api_docs)
                if route in api_docs['paths']:
                    points += 5

                pass

            # TODO - Verify functionality of routes
        except:
            print("An Error occurred during evaluation")
            # TODO - Give partial credit?
            app_logs = running_app['container'].logs()

            has_exception = 'Error' in app_logs

            if has_exception:
                print("There was a runtime error")
                print(app_logs)

            pass
    print(f"{app_prefix} achieved {points} points!")
    return points


prompt_to_api_test = Dataset(
    "prompt_to_api_test",
    "Prompt to API evaluation dataset",
    [(
        {
            "name": "twitter",
            "prompt": "Create an API for a Twitter website",
        },
        {
            'endpoints': ["/tweets"], # Create, read, update, delete
        }
    )],
    evaluate=eval_prompt_to_api
)