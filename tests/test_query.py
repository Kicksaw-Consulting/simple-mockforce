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

    response = salesforce.Lead.create({"Name": "Jim Bean"})
    response = salesforce.Lead.create({"Name": "Corey Taylor"})
    sfdc_id = response["id"]

    results = salesforce.query(f"SELECT Id, Name FROM Lead WHERE Id = 'hi'")
    records = results["records"]
    assert len(records) == 0

    results = salesforce.query(f"SELECT Id, Name FROM Lead WHERE Id = '{sfdc_id}'")
    records = results["records"]
    assert len(records) == 1
    assert records[0]["id"] == sfdc_id
