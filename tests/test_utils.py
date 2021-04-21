from simple_mockforce.utils import parse_detail_url, parse_create_url


def test_parse_detail_url():
    sobject, record_id = parse_detail_url(
        "https://mock.salesforce.com/services/data/v42.0/sobjects/Contact/123"
    )

    assert sobject == "Contact"
    assert record_id == "123"


def test_parse_create_url():
    sobject = parse_create_url(
        "https://mock.salesforce.com/services/data/v42.0/sobjects/Contact/"
    )

    assert sobject == "Contact"