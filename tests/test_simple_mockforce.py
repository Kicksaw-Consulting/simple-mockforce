from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce


@mock_salesforce
def test_sf_mock():
    salesforce = Salesforce(
        username="hi", password="hello", security_token="123", domain="mock"
    )
