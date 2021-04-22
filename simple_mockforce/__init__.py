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
from simple_mockforce.utils import terminate_regex


def mock_salesforce(func):
    @responses.activate
    def wrapper(*args, **kwargs):
        responses.add(
            responses.POST,
            terminate_regex(LOGIN_URL),
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
            terminate_regex(CREATE_URL),
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
            terminate_regex(DETAIL_URL),
            callback=delete_callback,
            content_type="content/json",
        )
        # bulk calls
        responses.add_callback(
            responses.GET,
            terminate_regex(BATCH_RESULT_URL),
            callback=bulk_result_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.GET,
            terminate_regex(BATCH_DETAIL_URL),
            callback=bulk_detail_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.POST,
            terminate_regex(BATCH_URL),
            callback=bulk_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.POST,
            terminate_regex(JOB_DETAIL_URL),
            callback=job_detail_callback,
            content_type="content/json",
        )
        responses.add_callback(
            responses.POST,
            terminate_regex(JOB_URL),
            callback=job_callback,
            content_type="content/json",
        )
        func(*args, **kwargs)

    return wrapper