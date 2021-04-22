from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce

from tests.utils import MOCK_CREDS, to_dict


@mock_salesforce
def test_bulk_lifecycle():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.bulk.Account.insert([{"Name": "Test Account"}])
    return
    assert len(result) == 1
    assert result[0]["success"]

    sfdc_id = result[0]["id"]

    account = salesforce.Account.get(sfdc_id)

    assert account["Name"] == "Test Account"

    result = salesforce.bulk.Account.update(
        [{"Id": sfdc_id, "Name": "Test Account - updated"}]
    )

    account = salesforce.Account.get(sfdc_id)

    assert account["Name"] == "Test Account - updated"


@mock_salesforce
def test_bulk_lifecycle_upsert_key():
    salesforce = Salesforce(**MOCK_CREDS)

    custom_id_field = "External_ID__c"
    custom_id = "98765"

    failed = False
    try:
        salesforce.Account.get_by_custom_id(custom_id_field, custom_id)
    except AssertionError:
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

    fetched_by_custom_id.pop("attributes")
    fetched_by_sfdc_id.pop("attributes")

    assert to_dict(fetched_by_custom_id) == to_dict(fetched_by_sfdc_id)

    result = salesforce.bulk.Account.upsert(
        [{"Name": "Worst Account Ever", custom_id_field: custom_id}],
        custom_id_field,
    )

    fetched_by_sfdc_id = salesforce.Account.get(sfdc_id)
    fetched_by_custom_id = salesforce.Account.get_by_custom_id(
        custom_id_field, custom_id
    )

    fetched_by_custom_id.pop("attributes")
    fetched_by_sfdc_id.pop("attributes")

    fetched_by_custom_id["Name"] == "Worst Account Ever"
    fetched_by_sfdc_id["Name"] == "Worst Account Ever"

    assert to_dict(fetched_by_custom_id) == to_dict(fetched_by_sfdc_id)