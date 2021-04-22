from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce

from tests.utils import MOCK_CREDS


@mock_salesforce
def test_get_object_mock():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.Contact.get("123")

    assert result["id"] == "123"
    assert result["name"] == "Bob"


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

    result = salesforce.Contact.upsert(
        "customExtIdField__c/imacustomid123",
        {"Name": "George", "customExtIdField__c": "imacustomid123"},
    )

    assert result == 204


@mock_salesforce
def test_get_by_custom_id_mock():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.Contact.get_by_custom_id(
        "customExtIdField__c", "imacustomid123"
    )

    assert result["id"]
    assert result["customextidfield__c"] == "imacustomid123"
    assert result["name"] == "George"


@mock_salesforce
def test_delete_object_mock():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.Contact.delete("123")

    assert result == 204
