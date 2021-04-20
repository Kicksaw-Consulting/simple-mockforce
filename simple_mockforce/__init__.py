from simple_mockforce.mock import MockSalesforce as Salesforce


def mock_salesforce(func):
    def wrapper(*args, **kwargs):
        import sys

        sys.modules["simple_salesforce"] = __import__(__name__)
        func(*args, **kwargs)
        del sys.modules["simple_salesforce"]

    return wrapper