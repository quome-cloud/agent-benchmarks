# Quome-agentic-benchmarks

Our internal company library for running LLM benchmarks.

### Current goal:
*Build an agent that reliably generates working APIs from a short prompt*

# Setup



## Pre-requisites
1. Install Ollama
   - https://ollama.com/download
2. Install Huggingface CLI (I used homebrew on mac)
   -  `brew install huggingface-cli`
   - https://huggingface.co/docs/huggingface_hub/main/en/guides/cli
3. Install pipx
   - `brew install pipx`
   - https://pipx.pypa.io/stable/installation/
4. Use pipx to install poetry
   - https://python-poetry.org/docs/

## Pip - Make sure you are using Python 3.12
1. `pip install -r requirements.txt`

## Poetry (A bit problematic for some) Running the prompt-to-api benchmark
1. Change directory to the same directory as this Readme.md 
2. In terminal, run `poetry install`
3. Create an environment file `.env`
   - Copy `cp .env.example .env`
   - Then edit the file to add your `OPENAI_API_KEY` (Ask Jenia, or Collin for one)
   - `.env` is a hidden file, but should be visible in your code editor
     - On a Mac hidden files can be seen in Finder with `Command + Shift + .`
     - In the terminal hidden files can be seen with `ls -a`
4. In a terminal window, change directory into `quome-agentic-benchmarks/quome_agentic_benchmarks`
5. Run the benchmark `python run.py`
   - You can specify which models, tools, benchmarks, and agents you test at bottom of file
   - `run_benchmark(["llama3"], ["create_api_template"], ["prompt_to_api"], ["openai_coder_v1"])`


## Creating your own agents
1. Open `quome_agentic_benchmarks/agents/example_agent_with_tool_use`
2. Create a copy
3. Code away!


## Creating your own tools
Tools are just python functions that the agents can call.
1. Open `quome_agentic_benchmarks/tools.py`
2. See examples there. Just write a function, annotate with `@tool`, provide a doc string
3. https://python.langchain.com/v0.1/docs/modules/tools/custom_tools/


## Tips
### Running any huggingface model on Ollama
- https://otmaneboughaba.com/posts/local-llm-ollama-huggingface/
