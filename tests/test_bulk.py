from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce

from tests.utils import MOCK_CREDS


@mock_salesforce
def test_bulk_insert():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.bulk.Contact.insert([{"Name": "Test"}])

    assert len(result) == 1
    assert result[0]["success"]


@mock_salesforce
def test_bulk_upsert():
    salesforce = Salesforce(**MOCK_CREDS)

    result = salesforce.bulk.Contact.upsert(
        [{"Name": "Test", "customExtIdField__c": "9999"}], "customExtIdField__c"
    )

    assert len(result) == 1
    assert result[0]["success"]