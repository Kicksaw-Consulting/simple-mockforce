import re
from simple_mockforce.callbacks import get_callback, query_callback

import responses

from simple_mockforce.constants import (
    LOGIN_URL,
    SOAP_API_LOGIN_RESPONSE,
    GET_URL,
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
        responses.add_callback(
            responses.GET,
            re.compile(QUERY_URL),
            callback=query_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.GET,
            re.compile(QUERY_URL),
            callback=query_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.GET,
            re.compile(GET_URL),
            callback=get_callback,
            content_type="content/json",
        )
        func(*args, **kwargs)

    return wrapper