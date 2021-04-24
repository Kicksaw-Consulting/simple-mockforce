from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceResourceNotFound

from simple_mockforce import mock_salesforce
from tests.utils import MOCK_CREDS


@mock_salesforce
def test_bulk_lifecycle():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.bulk.Account.insert(
        [{"Name": "Test Account"}, {"Name": "Test Account 2"}]
    )

    assert len(result) == 2
    assert result[0]["success"]
    assert result[1]["success"]

    sfdc_id = result[0]["id"]
    sfdc_id2 = result[1]["id"]

    account = salesforce.Account.get(sfdc_id)
    account2 = salesforce.Account.get(sfdc_id2)

    assert account["Name"] == "Test Account"
    assert account2["Name"] == "Test Account 2"

    result = salesforce.bulk.Account.update(
        [{"Id": sfdc_id, "Name": "Test Account - updated"}]
    )

    account = salesforce.Account.get(sfdc_id)
    account2 = salesforce.Account.get(sfdc_id2)

    assert account["Name"] == "Test Account - updated"
    assert account2["Name"] == "Test Account 2"


@mock_salesforce
def test_bulk_lifecycle_upsert_key():
    salesforce = Salesforce(**MOCK_CREDS)

    custom_id_field = "External_ID__c"
    custom_id = "98765"

    failed = False
    try:
        salesforce.Account.get_by_custom_id(custom_id_field, custom_id)
    except SalesforceResourceNotFound:
        failed = True

    assert failed

    result = salesforce.bulk.Account.upsert(
        [{"Name": "Best Account Ever", custom_id_field: custom_id}],
        custom_id_field,
    )

    assert len(result) == 1
    assert result[0]["success"]

    sfdc_id = result[0]["id"]

    fetched_by_sfdc_id = salesforce.Account.get(sfdc_id)
    fetched_by_custom_id = salesforce.Account.get_by_custom_id(
        custom_id_field, custom_id
    )

    assert fetched_by_custom_id["Id"] == fetched_by_sfdc_id["Id"]
    assert fetched_by_custom_id["Name"] == "Best Account Ever"
    assert fetched_by_sfdc_id["Name"] == "Best Account Ever"

    result = salesforce.bulk.Account.upsert(
        [{"Name": "Worst Account Ever", custom_id_field: custom_id}],
        custom_id_field,
    )

    fetched_by_sfdc_id = salesforce.Account.get(sfdc_id)
    fetched_by_custom_id = salesforce.Account.get_by_custom_id(
        custom_id_field, custom_id
    )

    assert fetched_by_custom_id["Id"] == fetched_by_sfdc_id["Id"]
    assert fetched_by_custom_id["Name"] == "Worst Account Ever"
    assert fetched_by_sfdc_id["Name"] == "Worst Account Ever"


@mock_salesforce
def test_bulk_upsert_with_relation():
    salesforce = Salesforce(**MOCK_CREDS)

    custom_contact_id_field = "ExternalId__c"
    custom_contact_id = "1-2-3"

    response = salesforce.Contact.create(
        {"Name": "Test Name", custom_contact_id_field: custom_contact_id}
    )

    contact_id = response["id"]

    custom_message_id_field = "MessageId__c"
    custom_message_id = "10001"
    custom_message_id2 = "10002"

    results = salesforce.bulk.MessageAttempt__c.upsert(
        [
            {
                "Name": "Message 1",
                custom_message_id_field: custom_message_id,
                "Contact__r": {custom_contact_id_field: custom_contact_id},
            },
            {
                "Name": "Message 2",
                custom_message_id_field: custom_message_id2,
                "Contact__r": {custom_contact_id_field: custom_contact_id},
            },
        ],
        custom_message_id_field,
    )

    assert len(results) == 2

    message1_id = results[0]["id"]

    message1 = salesforce.MessageAttempt__c.get(message1_id)

    assert message1["Name"] == "Message 1"
    assert message1["Contact"] == contact_id
    assert message1[custom_message_id_field] == custom_message_id

    message1 = salesforce.MessageAttempt__c.get_by_custom_id(
        custom_message_id_field, custom_message_id2
    )

    assert message1["Name"] == "Message 2"
    assert message1["Contact"] == contact_id
    assert message1[custom_message_id_field] == custom_message_id2