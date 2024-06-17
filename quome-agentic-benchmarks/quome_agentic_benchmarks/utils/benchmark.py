import importlib


def load_modules(module_names, package, relative_package=''):
    return [importlib.import_module(f'{relative_package}.{module}', package) for module in module_names]


def load_members(attribute_names, module):
    module = importlib.import_module(module)
    return [getattr(module, attribute) for attribute in attribute_names]

