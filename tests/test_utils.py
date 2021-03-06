from simple_mockforce.utils import (
    parse_detail_url,
    parse_create_url,
    parse_job_batch_url,
    parse_batch_result_url,
    find_object_and_index,
    parse_batch_detail_url,
)


def test_parse_detail_url():
    sobject, _, record_id = parse_detail_url(
        "/services/data/v42.0/sobjects/Contact/123"
    )

    assert sobject == "Contact"
    assert record_id == "123"


def test_parse_detail_url_with_upsert_key():
    sobject, upsert_key, record_id = parse_detail_url(
        "/services/data/v42.0/sobjects/Contact/customExtIdField__c/123"
    )

    assert sobject == "Contact"
    assert upsert_key == "customExtIdField__c"
    assert record_id == "123"


def test_parse_create_url():
    sobject = parse_create_url("/services/data/v42.0/sobjects/Contact/")

    assert sobject == "Contact"


def test_parse_job_batch_url():
    job_id = parse_job_batch_url("/services/async/42.0/job/123456/batch")

    assert job_id == "123456"


def test_parse_batch_detail_url():
    job_id, batch_id = parse_batch_detail_url(
        "/services/async/42.0/job/123456/batch/123"
    )

    assert job_id == "123456"
    assert batch_id == "123"


def test_parse_batch_result_url():
    job_id, batch_id = parse_batch_result_url(
        "/services/async/42.0/job/123456/batch/123/result"
    )

    assert job_id == "123456"
    assert batch_id == "123"


def test_find_object_and_index():
    object_, index = find_object_and_index([{"Id": "123"}], "Id", "123")
    assert object_ == {"Id": "123"}
    assert index == 0
