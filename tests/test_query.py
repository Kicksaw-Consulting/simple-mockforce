from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce


from tests.utils import MOCK_CREDS


@mock_salesforce
def test_query_mock():
    salesforce = Salesforce(**MOCK_CREDS)

    results = salesforce.query("SELECT Id, Name FROM Contact LIMIT 1")
    records = results["records"]
    assert len(records) == 1
