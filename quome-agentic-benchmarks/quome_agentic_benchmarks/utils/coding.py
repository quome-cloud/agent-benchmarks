
import contextlib
import itertools
import json
import os
import re
from asyncio import sleep

import requests

from datetime import date, datetime
from docker.models.containers import Container
from pathlib import Path
from typing import TypedDict, NotRequired

_example_llm_code_output = "requirements.txt\n```fastapi==0.1.2\npandas==1.2.3```Some explanation\nsome_other_file.py\n```abc\nabc\nabc\n```"
_example_llm_code_output_2 = "main.py\n```python\nprint('hello world')```"

# Regex matches code blocks denoted by three backticks ```
# Also matches ```python and ```bash
backtick_code_regex = '```(?:[\\w]*\n)?'


def extract_code_from_llm_output(file_name, llm_output):
    """
    Extracts a single code block (file) from llm output. Relies on three backticks ``` for code blocks
    >>> extract_code_from_llm_output("requirements.txt", _example_llm_code_output)
    'fastapi==0.1.2\\npandas==1.2.3'

    >>> extract_code_from_llm_output("main.py", _example_llm_code_output_2)
    "print('hello world')"
    """

    llm_output.find(file_name)
    code_block = re.split(backtick_code_regex, llm_output[llm_output.find(file_name):])[1]

    return code_block


class PythonCodeInput(TypedDict):
    main: str
    requirements: str
    run_command: NotRequired[str]


DEFAULT_PYTHON_DOCKERFILE = """FROM python:alpine
WORKDIR /opt/app
COPY requirements.txt requirements.txt
COPY main.py main.py
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
"""

README_TEMPLATE = """# {app_name}
```
docker bu
```
"""


class RunningProgram(TypedDict):
    container: Container
    host_port: int
    build_logs: str
    base_dir: str


def write_code_to_dir(code: PythonCodeInput, app_prefix: str, unique_app_id: str) -> str:
    # Write files to temporary directory - Find out how to get base directory of package
    generated_apps_dir = os.path.join(os.getcwd(), "generated_apps", str(date.today()), app_prefix)
    base_dir = os.path.join(generated_apps_dir, unique_app_id)
    Path(base_dir).mkdir(parents=True, exist_ok=True)

    print(f"Creating new code directory {base_dir}")

    with open(os.path.join(base_dir, "main.py"), "w") as f:
        f.write(code["main"])

    with open(os.path.join(base_dir, "requirements.txt"), "w") as f:
        f.write(code["requirements"])

    with open(os.path.join(base_dir, "Dockerfile"), "w") as f:
        f.write(DEFAULT_PYTHON_DOCKERFILE)

    return base_dir


@contextlib.contextmanager
def safe_build_and_run_python_code(code: PythonCodeInput, app_prefix="apps") -> RunningProgram:
    """Use this function with Python's "with" keyword
    with safe_build_and_run_python_code(...) as running_app:
       running_app['port']
    """
    lapp_prefix = app_prefix.lower()

    hours_minutes_seconds = datetime.now().strftime('%H_%M_%S')
    unique_app_id = f"{lapp_prefix}-{hours_minutes_seconds}"

    base_dir = write_code_to_dir(code, lapp_prefix, unique_app_id)

    # Delegated generator...
    # https://stackoverflow.com/questions/11197186/how-to-yield-results-from-a-nested-generator-function
    yield from build_and_run_docker_python(base_dir, unique_app_id, run_command=code.get('run_command', None))


def build_and_run_docker_python(base_dir, tag, run_command="python main.py"):
    import docker
    # TODO - May want to hash the input and use as key so we don't create duplicate apps for same code

    client = docker.from_env()
    ports_in_use = set(itertools.chain.from_iterable(map(lambda c: (int(v[0]['HostPort']) for v in c.ports.values() if v), client.containers.list())))
    available_host_port = next(port for port in range(8000, 9000) if port not in ports_in_use)
    # Build docker image.
    # https://docker-py.readthedocs.io/en/stable/images.html#docker.models.images.ImageCollection.build
    # https://docker-py.readthedocs.io/en/stable/images.html#docker.models.images.Image
    image, _build_logs = client.images.build(path=base_dir, tag=tag.lower())

    # Run the app image in a docker container
    # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    container = client.containers.run(
        image,
        command=run_command,  # May need to be careful here... Check with Ryan
        ports={'8000/tcp': available_host_port},
        detach=True,
        name=tag.lower(),
    )

    # Wait til container starts
    wait_seconds = 30
    retry_seconds = 1
    elapsed_time = 0
    while container.status not in ('running', 'exited') and elapsed_time < wait_seconds:
        container.reload()
        sleep(retry_seconds)
        elapsed_time += retry_seconds
        continue

    try:
        running_program = RunningProgram(
            container=container,
            host_port=available_host_port,
            build_logs=''.join([r.get('stream', '') for r in _build_logs]),
            base_dir=base_dir
        )
        yield running_program

    finally:
        # Cleanup
        container.stop()
        container.wait()
        container.remove()
        image.remove(force=True)


FASTAPI_HELLOWORLD = """from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def root():
    return {"message": "Hello World"}
"""
FASTAPI_REQUIREMENTS = "fastapi==0.111.0"

if __name__ == "__main__":
    # For running some tests.
    import doctest
    doctest.testmod()

    # Run API example
    with safe_build_and_run_python_code({
        "main": FASTAPI_HELLOWORLD,
        "requirements": FASTAPI_REQUIREMENTS,
        "run_command": "fastapi run main.py"
    }) as running_app:
        print(running_app['host_port'])
        resp = requests.get(f"http://0.0.0.0:{running_app['host_port']}")
        api_docs = json.loads(requests.get(f"http://0.0.0.0:{running_app['host_port']}/openapi.json").text)
        print(running_app['container'])
        print(running_app['container'].logs())


    # Run output logs only (no running program)
    with safe_build_and_run_python_code({
        "main": "import pandas as pd\nimport numpy as np\ns = pd.Series([1, 3, 5, np.nan, 6, 8])\nprint(s)",
        "requirements": "pandas\nnumpy"
    }) as program:
        print(program['container'])
        print(program['container'].logs())
        print(program['build_logs'])





