from unittest.mock import patch
from simple_mockforce.mock import MockSalesforce


def mock_salesforce(func):
    @patch("simple_salesforce.Salesforce", MockSalesforce)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    return wrapper