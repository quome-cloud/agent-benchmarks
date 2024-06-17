import json

import requests

from quome_agentic_benchmarks.datasets.base import Dataset
from quome_agentic_benchmarks.eval.rest_api import eval_prompt_to_api


prompt_to_api_test = Dataset(
    "prompt_to_api_test",
    "Prompt to API evaluation dataset",
    [
        # (
        #     {
        #         "name": "twitter",
        #         "prompt": "Create an API for a Twitter website",
        #     },
        #     {
        #         'endpoints': ["/tweets"],  # Create, read, update, delete
        #     }
        # ),
        (
            {
                "name": "dna",
                "prompt": "Create an API to run DNA and RNA sequencing pipelines. Use Parabricks if possible.",
            },
            {
                'endpoints': ["/pipelines", "/dna", "/rna"],  # Create, read, update, delete
            }
        )
    ],
    evaluate=eval_prompt_to_api
)