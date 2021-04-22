from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce

from tests.utils import MOCK_CREDS


@mock_salesforce
def test_crud_lifecycle():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.Contact.create({"FirstName": "John", "LastName": "Doe"})

    record_id = result["id"]

    assert record_id
    assert result["success"] == True
    assert result["errors"] == []

    result = salesforce.Contact.get(record_id)

    assert result["Id"] == record_id
    assert result["FirstName"] == "John"
    assert result["LastName"] == "Doe"

    result = salesforce.Contact.update(record_id, {"LastName": "Smith"})

    assert result == 204

    result = salesforce.Contact.get(record_id)

    assert result["Id"] == record_id
    assert result["FirstName"] == "John"
    assert result["LastName"] == "Smith"

    result = salesforce.Contact.delete(record_id)

    assert result == 204

    failed = False
    try:
        result = salesforce.Contact.get(record_id)
    except AssertionError:
        failed = True

    assert failed


@mock_salesforce
def test_crud_lifecycle_with_custom_id():
    salesforce = Salesforce(**MOCK_CREDS)

    custom_id = "imacustomid123"
    custom_id_field = "customExtIdField__c"

    result = salesforce.Contact.upsert(
        f"{custom_id_field}/{custom_id}",
        {"LastName": "Doe", f"{custom_id_field}": f"{custom_id}"},
    )

    assert result == 204

    result = salesforce.Contact.get_by_custom_id(custom_id_field, custom_id)

    assert result["Id"]
    assert result[custom_id_field] == custom_id
    assert result["LastName"] == "Doe"

    result = salesforce.Contact.upsert(
        f"{custom_id_field}/{custom_id}",
        {"LastName": "Smith", f"{custom_id_field}": f"{custom_id}"},
    )

    result = salesforce.Contact.get_by_custom_id(custom_id_field, custom_id)

    assert result["Id"]
    assert result[custom_id_field] == custom_id
    assert result["LastName"] == "Smith"