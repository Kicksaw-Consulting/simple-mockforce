from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce


MOCK_CREDS = {
    "username": "hi",
    "password": "hello",
    "security_token": "123",
    "domain": "mock",
}


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

    result = salesforce.Contact.create(
        {"Id": "12345", "FirstName": "John", "LastName": "Doe"}
    )

    return

    assert dict(result) == {
        "id": "12345",
        "firstname": "John",
        "lastname": "Doe",
        "attributes": {
            "type": "Contact",
            "url": "/services/data/v42.0/sobjects/Contact/12345",
        },
    }