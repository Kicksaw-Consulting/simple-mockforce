from typing import Dict
import json

MOCK_CREDS = {
    "username": "hi",
    "password": "hello",
    "security_token": "123",
    "domain": "mock",
}

STANDARD_FIELDS_WITHOUT_USER = ["Id", "IsDeleted", "LastModifiedDate", "CreatedDate", "SystemModstamp"]
USER_STANDARD_FIELDS = ["LastModifiedById", "CreatedById"]


def to_dict(input_ordered_dict):
    """
    Useful for getting rid of OrderedDicts
    """
    return json.loads(json.dumps(input_ordered_dict))


def filter_user_fields(salesforce_object: Dict[str, str]) -> Dict[str, str]:
    return {key: value for key, value in salesforce_object.items() if key not in USER_STANDARD_FIELDS}