
import contextlib
import itertools
import json
import os
import re
import uuid
from asyncio import sleep
from docker.errors import APIError
from enum import Enum

import requests

from datetime import date, datetime
from docker.models.containers import Container
from pathlib import Path
from typing import TypedDict, NotRequired, Optional

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
    code_blocks = re.split(backtick_code_regex, llm_output[llm_output.find(file_name):])

    if len(code_blocks) < 2:
        print(f"No code blocks found for {file_name}")
        return ""

    return code_blocks[1]


DEFAULT_PYTHON_DOCKERFILE = """FROM python:alpine
WORKDIR /opt/app
COPY requirements.txt requirements.txt
COPY main.py main.py
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
"""

# For hosting basic HTML, Javascript, CSS websites
DEFAULT_STATIC_HOSTING_DOCKERFILE = """
FROM busybox:1.35

# Create a non-root user to own the files and run our server
RUN adduser -D static
USER static
WORKDIR /home/static

# Copy the static website
# Use the .dockerignore file to control what ends up inside the image!
COPY . .

# Run BusyBox httpd
CMD ["busybox", "httpd", "-f", "-v", "-p", "3000"]
"""


class AllowedDockerFiles(Enum):
    python = DEFAULT_PYTHON_DOCKERFILE
    static_web = DEFAULT_STATIC_HOSTING_DOCKERFILE


class CodeInput(TypedDict):
    files: dict[str, str]  # Path -> Content
    dockerfile: AllowedDockerFiles
    build_command: NotRequired[str]
    run_command: NotRequired[str]
    port: NotRequired[int]


class RunningProgram(TypedDict):
    container: Container
    host_port: int
    build_logs: str
    base_dir: str
    runtime_error: Optional[str]


DISALLOWED_PATHS = {"Dockerfile"}


def write_code_to_dir(code: CodeInput, output_dir: Optional[str] = None) -> str:
    """
        Writes all files to temporary directory within generated_apps
        This function is likely a large security risk.
        Writing Dockerfiles is possible here. Useful, but definitely carries risks.
    """
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "generated", "apps", str(date.today()))

    base_dir = output_dir
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    print(f"Creating new code directory {base_dir}")

    for path, content in code["files"].items():
        # Careful about relative paths here. Don't want to dig where we shouldn't on local file system.
        file_path = os.path.join(base_dir, path)
        if not file_path.startswith(base_dir) or ".." in path:
            raise ValueError("Relative paths not allowed")

        if path in DISALLOWED_PATHS:
            raise ValueError(f"Writing custom {path} is not allowed")

        # Could try and only expose writing to files through docker...
        with open(file_path, "w") as f:
            f.write(content)

    # Write Dockerfile
    dockerfile_path = os.path.join(base_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(code['dockerfile'].value)

    return base_dir


def safe_build_and_run_code(code: CodeInput, app_id=None, output_dir=None):
    """Use this function with Python's "with" keyword
    with safe_build_and_run_code(...) as running_app:
       running_app['port']
    """
    if app_id is None:
        app_id = str(uuid.uuid4())  # For docker images.

    code_dir = os.path.join(output_dir, 'app')
    write_code_to_dir(code, output_dir=code_dir)

    # Delegated generator...
    # https://stackoverflow.com/questions/11197186/how-to-yield-results-from-a-nested-generator-function
    return build_and_run_docker(
        code_dir,
        app_id,
        run_command=code.get('run_command', None),
        expose_port=code.get('port', 8000)
    )


@contextlib.contextmanager
def build_and_run_docker(base_dir, tag, run_command="python main.py", expose_port=8000):
    import docker

    if tag is None:
        tag = str(uuid.uuid4())

    client = docker.from_env()
    port_mapping = {}
    ports_in_use = set(itertools.chain.from_iterable(map(lambda c: (int(v[0]['HostPort']) for v in c.ports.values() if v), client.containers.list())))
    available_host_port = next(port for port in range(expose_port, expose_port+100) if port not in ports_in_use)
    # Build docker image.
    # https://docker-py.readthedocs.io/en/stable/images.html#docker.models.images.ImageCollection.build
    # https://docker-py.readthedocs.io/en/stable/images.html#docker.models.images.Image
    port_mapping[f'{expose_port}/tcp'] = available_host_port

    image, _build_logs = client.images.build(path=base_dir, tag=tag.lower())

    # Run the app image in a docker container
    # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    runtime_error = None
    container = None
    try:
        container = client.containers.run(
            image,
            command=run_command,  # May need to be careful here... Check with Ryan
            ports=port_mapping,
            detach=True,
            name=tag.lower(),
        )
    except APIError as e:
        runtime_error = e

    # Wait til container starts
    wait_seconds = 30
    retry_seconds = 1
    elapsed_time = 0
    while not runtime_error and container.status not in ('running', 'exited') and elapsed_time < wait_seconds:
        container.reload()
        sleep(retry_seconds)
        elapsed_time += retry_seconds
        continue

    try:
        running_program = RunningProgram(
            container=container,
            host_port=available_host_port,
            build_logs=''.join([r.get('stream', '') for r in _build_logs]),
            base_dir=base_dir,
            runtime_error=runtime_error
        )
        yield running_program

    finally:
        # Cleanup
        with open(os.path.join(base_dir, "build.log"), "w") as f:
            f.write(running_program['build_logs'])
        with open(os.path.join(base_dir, "application.log"), "w") as f:
            f.write(container.logs().decode('utf-8'))
        if runtime_error:
            with open(os.path.join(base_dir, "error.log"), "w") as f:
                f.write(str(runtime_error))
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
    with safe_build_and_run_code(CodeInput(
        files={
            "main.py": FASTAPI_HELLOWORLD,
            "requirements.txt": FASTAPI_REQUIREMENTS
        },
        dockerfile=AllowedDockerFiles.python,
        run_command="fastapi run main.py"
    )) as running_app:
        print(running_app['host_port'])
        resp = requests.get(f"http://0.0.0.0:{running_app['host_port']}")
        api_docs = json.loads(requests.get(f"http://0.0.0.0:{running_app['host_port']}/openapi.json").text)
        print(running_app['container'])
        print(running_app['container'].logs())


    # Run output logs only (no running program)
    with safe_build_and_run_code(CodeInput(
            files={
                    "main.py": "import pandas as pd\nimport numpy as np\ns = pd.Series([1, 3, 5, np.nan, 6, 8])\nprint(s)",
                    "requirements.txt": "pandas\nnumpy"
                },
            dockerfile=AllowedDockerFiles.python,
            run_command="python main.py"
    )) as program:
        print(program['container'])
        print(program['container'].logs())
        print(program['build_logs'])


    # Example of static web hosting
    with safe_build_and_run_code(CodeInput(
            files={
                    "index.html": """
<!doctype html>
<html>
  <head>
    <title>Hello world!</title>
  </head>
  <body>
    <p>This is an example paragraph.</p>
  </body>
</html>
"""
            },
            dockerfile=AllowedDockerFiles.static_web,
            port=3000
    )) as running_app:
        print(running_app['host_port'])
        response = requests.get(f"http://0.0.0.0:{running_app['host_port']}")
        print(response.content)
