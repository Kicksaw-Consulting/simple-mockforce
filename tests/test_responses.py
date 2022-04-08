import responses

from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce

from tests.utils import MOCK_CREDS


@responses.activate
@mock_salesforce
def test_responses_activated_before():
    """
    Verify we can activate a user-defined `responses` on top of our Mockforce mocks
    """
    Salesforce(**MOCK_CREDS)


@mock_salesforce
@responses.activate
def test_responses_activated_after():
    """
    Verify we can activate a user-defined `responses` at the bottom of our Mockforce mocks
    """
    Salesforce(**MOCK_CREDS)
