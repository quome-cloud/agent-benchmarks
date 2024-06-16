from quome_agentic_benchmarks.datasets.coding import prompt_to_api_test

dataset_lookup = {
    "prompt_to_api_v1": prompt_to_api_test,
}

valid_datasets = dataset_lookup.keys()


def get_dataset(dataset_name):
    return dataset_lookup[dataset_name]

