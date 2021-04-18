from simple_salesforce import Salesforce


def run():
    salesforce = Salesforce(
        username="hi", password="hello", security_token="123", domain="mock"
    )
