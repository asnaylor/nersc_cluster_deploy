import json
from pathlib import Path

def load_secrets():
    with open(str(Path.home()) + '/.sf_api_secrets') as json_file:
        secrets = json.load(json_file)

    return secrets['client_id'], secrets['private_key']

def user_account():
    with open(str(Path.home()) + '/.sf_api_secrets') as json_file:
        secrets = json.load(json_file)

    return secrets['account']
