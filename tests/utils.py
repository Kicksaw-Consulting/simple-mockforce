import json

MOCK_CREDS = {
    "username": "hi",
    "password": "hello",
    "security_token": "123",
    "domain": "mock",
}


def to_dict(input_ordered_dict):
    """
    Useful for getting rid of OrderedDicts
    """
    return json.loads(json.dumps(input_ordered_dict))