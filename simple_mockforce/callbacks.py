import json

from urllib.parse import urlparse

from simple_mockforce.utils import (
    parse_detail_url,
    parse_create_url,
)
from simple_mockforce.virtual import virtual_salesforce


def query_callback(request):
    records = virtual_salesforce.query(request.params["q"])

    body = {
        "totalSize": len(records),
        "done": True,
        "records": records,
    }
    return (200, {}, json.dumps(body))


def get_callback(request):
    url = request.url
    path = urlparse(url).path
    sobject, custom_id_field, record_id = parse_detail_url(path)

    object_ = virtual_salesforce.get(
        sobject, record_id, custom_id_field=custom_id_field
    )

    return (
        200,
        {},
        json.dumps({"attributes": {"type": sobject, "url": path}, **object_}),
    )


def create_callback(request):
    url = request.url
    path = urlparse(url).path
    body = json.loads(request.body)

    sobject = parse_create_url(path)

    id_ = virtual_salesforce.create(sobject, body)

    return (
        200,
        {},
        # yep, salesforce lowercases id on create's response
        json.dumps({"id": id_, "success": True, "errors": []}),
    )


def update_callback(request):
    url = request.url
    path = urlparse(url).path
    body = json.loads(request.body)

    sobject, upsert_key, record_id = parse_detail_url(path)

    virtual_salesforce.update(sobject, record_id, body, upsert_key=upsert_key)

    return (
        204,
        {},
        json.dumps({}),
    )


def delete_callback(request):
    url = request.url
    path = urlparse(url).path

    sobject, _, record_id = parse_detail_url(path)
    virtual_salesforce.delete(sobject, record_id)

    return (
        204,
        {},
        json.dumps({}),
    )