from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce

from tests.utils import MOCK_CREDS


@mock_salesforce
def test_basic_query():
    """
    WARNING: this test is polluted
    """
    salesforce = Salesforce(**MOCK_CREDS)

    results = salesforce.query("SELECT Id, Name FROM Contact LIMIT 1")
    records = results["records"]
    assert len(records) == 1


@mock_salesforce
def test_where_query():
    salesforce = Salesforce(**MOCK_CREDS)

    response = salesforce.Lead.create(
        {"Name": "Jim Bean", "Title": "CDO", "Human_Score__c": 5}
    )
    sfdc_id = response["id"]
    response = salesforce.Lead.create({"Name": "Corey Taylor", "Title": "Singer"})

    results = salesforce.query(f"SELECT Id, Name FROM Lead WHERE Id = 'nothing'")
    records = results["records"]
    assert len(records) == 0

    results = salesforce.query(f"SELECT Id, Name FROM Lead WHERE Id = '{sfdc_id}'")
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["id"] == sfdc_id
    assert record["name"] == "Jim Bean"

    results = salesforce.query(f"SELECT Id, Name FROM Lead WHERE Human_Score__c = 5")
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["id"] == sfdc_id

    results = salesforce.query(
        f"SELECT Id, Name FROM Lead WHERE Human_Score__c < 4 OR Name = 'Jim Bean'"
    )
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["id"] == sfdc_id

    results = salesforce.query(
        f"SELECT Id, Name FROM Lead WHERE (Human_Score__c < 4 OR Name = 'Jim Bean') AND Title = 'CDO'"
    )
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["id"] == sfdc_id

    results = salesforce.query(f"SELECT Id, Name FROM Lead WHERE Human_Score__c >= 6")
    records = results["records"]
    assert len(records) == 0
