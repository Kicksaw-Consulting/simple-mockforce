import re

import responses

from simple_mockforce.callbacks import (
    bulk_callback,
    bulk_detail_callback,
    bulk_result_callback,
    create_callback,
    delete_callback,
    get_callback,
    job_callback,
    job_detail_callback,
    query_callback,
    update_callback,
)
from simple_mockforce.constants import (
    BATCH_DETAIL_URL,
    BATCH_RESULT_URL,
    CREATE_URL,
    JOB_DETAIL_URL,
    LOGIN_URL,
    SOAP_API_LOGIN_RESPONSE,
    DETAIL_URL,
    QUERY_URL,
    JOB_URL,
    BATCH_URL,
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
            re.compile(DETAIL_URL),
            callback=get_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.POST,
            re.compile(CREATE_URL),
            callback=create_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.PATCH,
            re.compile(DETAIL_URL),
            callback=update_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.DELETE,
            re.compile(DETAIL_URL),
            callback=delete_callback,
            content_type="content/json",
        )
        # bulk calls
        responses.add_callback(
            responses.GET,
            re.compile(BATCH_RESULT_URL),
            callback=bulk_result_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.GET,
            re.compile(BATCH_DETAIL_URL),
            callback=bulk_detail_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.POST,
            re.compile(BATCH_URL),
            callback=bulk_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.POST,
            re.compile(JOB_DETAIL_URL),
            callback=job_detail_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.POST,
            re.compile(JOB_URL),
            callback=job_callback,
            content_type="content/json",
        )
        func(*args, **kwargs)

    return wrapper