from simple_mockforce.mock import MockSalesforce


def test_sf_mock(monkeypatch):
    salesforce = MockSalesforce(
        username="hi", password="hello", security_token="123", domain="mock"
    )

    result = salesforce.query("SELECT Id FROM Contact")
    assert result == None