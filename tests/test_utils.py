from simple_mockforce.utils import (
    parse_detail_url,
    parse_create_url,
    find_object_and_index,
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


def test_find_object_and_index():
    object_, index = find_object_and_index([{"id": "123"}], "id", "123")
    assert object_ == {"id": "123"}
    assert index == 0