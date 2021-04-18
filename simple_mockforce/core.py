def mock_salesforce(func):
    def wrapper(*args, **kwargs):
        import sys

        sys.modules["simple_salesforce"] = __import__("simple_mockforce")
        func(*args, **kwargs)
        del sys.modules["simple_salesforce"]

    return wrapper