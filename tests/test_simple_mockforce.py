import json

from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce


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


@mock_salesforce
def test_query_mock():
    salesforce = Salesforce(**MOCK_CREDS)

    results = salesforce.query("SELECT Id, Name FROM Contact LIMIT 1")
    records = results["records"]
    assert len(records) == 1


@mock_salesforce
def test_get_object_mock():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.Contact.get("123")

    assert dict(result) == {
        "id": "123",
        "name": "Bob",
        "attributes": {
            "type": "Contact",
            "url": "/services/data/v42.0/sobjects/Contact/123",
        },
    }


@mock_salesforce
def test_create_object_mock():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.Contact.create({"FirstName": "John", "LastName": "Doe"})

    assert result["id"]
    assert result["success"] == True
    assert result["errors"] == []


@mock_salesforce
def test_update_object_mock():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.Contact.update("123", {"LastName": "Smith"})

    assert result == 204


@mock_salesforce
def test_upsert_object_mock():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.Contact.upsert("customExtIdField__c/11999", {"Name": "George"})

    assert result == 204
