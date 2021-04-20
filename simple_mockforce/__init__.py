import json
import re

import responses

from simple_mockforce.mock import MockSalesforce as Salesforce
from simple_mockforce.patch_constants import (
    LOGIN_URL,
    SOAP_API_LOGIN_RESPONSE,
    BASE_URL,
    QUERY_URL,
)


def mock_salesforce(func):
    @responses.activate
    def wrapper(*args, **kwargs):
        responses.add(
            responses.POST,
            re.compile(LOGIN_URL),
            body=SOAP_API_LOGIN_RESPONSE,
            content_type="text/xml",
        )

        def request_callback(request):
            resp_body = {}
            headers = {}
            return (200, headers, json.dumps(resp_body))

        responses.add_callback(
            responses.GET,
            re.compile(QUERY_URL),
            callback=request_callback,
            content_type="content/json",
        )
        func(*args, **kwargs)

    return wrapper