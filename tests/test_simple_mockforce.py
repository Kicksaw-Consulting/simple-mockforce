from simple_mockforce import mock_salesforce


@mock_salesforce
def test_sf_mock():
    from simple_salesforce import Salesforce

    salesforce = Salesforce(
        username="hi", password="hello", security_token="123", domain="mock"
    )

    results = salesforce.query("SELECT Id, Name FROM Contact")
    records = results["records"]
    assert records