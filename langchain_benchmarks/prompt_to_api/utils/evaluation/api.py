import requests


def ping(url):
    return requests.get(url).status_code == 200


def has_docs(url):
    return ping(os.path.join(url, "/docs"))


def evaluate_api(url, expected):
    points = 0

    if ping(url):
        points += 10

    if has_docs(url):
        points += 5

    for method, path in expected["endpoints"]:
        # Check endpoint here
        pass


    # Security bench mark
    # - Vulns CVN (critical vulns) - Dependency versions that are being used
    # What security scores are available?
    # - CVSS - Common Vulnerability Scoring System

    # Our main strategy - Is to solve the security issue once, and make it easy for developers,
    # to use our secure code instead of writing their own.
    # - Sidecar (Connect API to Database)
    # ---  Add observability / logging (data accessed by person at XYZ time)
    # ---  Get login for database Auth
    # ---  Access control - Make sure this user can only data they are supposed to edit / see

