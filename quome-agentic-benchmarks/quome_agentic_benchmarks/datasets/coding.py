import json

import requests

from quome_agentic_benchmarks.datasets.base import Dataset
from quome_agentic_benchmarks.eval.frontend import eval_prompt_to_frontend
from quome_agentic_benchmarks.eval.prd import eval_prompt_to_prd
from quome_agentic_benchmarks.eval.rest_api import eval_prompt_to_api


prompt_to_api_test = Dataset(
    "prompt_to_api_test",
    "Prompt to API evaluation dataset",
    [
        (
            {
                "name": "twitter",
                "prompt": "Create an app like Twitter",
            },
            {
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
                'endpoints': ["users", "followers", "following", "like", "likes", "login", "tweets"], # Create, read, update, delete
            }
        ),
        (
            {
                "name": "dna",
                "prompt": "Create an app that handles DNA and RNA sequencing pipelines. Use Parabricks if possible.",
            },
            {
                'schemas': [
                    {
                        'name': "Job",
                        'properties': ['status']
                    },
                ],
                'endpoints': ["/pipelines", "/dna", "/rna"],  # Create, read, update, delete
            }
        )
    ],
    evaluate=eval_prompt_to_api
)

prompt_to_prd_test = Dataset(
    "prompt_to_prd_test",
    "Prompt to PRD evaluation dataset",
    [
        (
            {
                "name": "twitter",
                "prompt": "Create an app like Twitter",
            },
            {
                "terms": ["tweet", "user", "content", "follow", "profile"]
            }
        ),
        (
            {
                "name": "dna",
                "prompt": "Create an app that handles DNA and RNA sequencing pipelines. Use Parabricks if possible.",
            },
            {
                "terms": ["dna", "rna", "pipeline", "job", "jobs", "exome", "genome", "sequencing"]
            }
        )
    ],
    evaluate=eval_prompt_to_prd
)


prompt_to_frontend_test = Dataset(
    "prompt_to_frontend_test",
    "Prompt to Frontend evaluation dataset",
    [
        (
            {
                "name": "twitter",
                "prompt": "Create an app like Twitter",
            },
            {
                "components": ["post", "search", "following", "profile", "messages"]
            }
        ),
        (
            {
                "name": "dna",
                "prompt": "Create an app that handles DNA and RNA sequencing pipelines. Use Parabricks if possible.",
            },
            {
                "components": ["upload", "create", "run", "job", "jobs", "dna", "rna", "data"]
            }
        )
    ],
    evaluate=eval_prompt_to_frontend
)