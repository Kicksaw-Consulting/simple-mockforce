import json
import uuid

from urllib.parse import urlparse

from python_soql_parser import parse

from simple_mockforce.utils import (
    parse_detail_url,
    parse_create_url,
    find_object_and_index,
)
from simple_mockforce.virtual import virtual_salesforce


def query_callback(request):
    parse_results = parse(request.params["q"])
    sobject = parse_results["sobject"]
    fields = parse_results["fields"].asList()
    limit = parse_results["limit"].asList()
    objects = virtual_salesforce.get_sobjects(sobject)
    # TODO: construct attributes
    records = [*map(lambda record: {field: record[field] for field in fields}, objects)]
    if limit:
        limit: int = limit[0]
        records = records[:limit]

    body = {
        "totalSize": len(records),
        "done": True,
        "records": records,
    }
    return (200, {}, json.dumps(body))


def get_callback(request):
    url = request.url
    path = urlparse(url).path
    sobject, _, record_id = parse_detail_url(path)

    objects = virtual_salesforce.get_sobjects(sobject)

    narrowed = [*filter(lambda object_: object_["id"] == record_id, objects)][0]

    return (
        200,
        {},
        json.dumps({"attributes": {"type": sobject, "url": path}, **narrowed}),
    )


def create_callback(request):
    url = request.url
    path = urlparse(url).path
    body = json.loads(request.body)

    sobject = parse_create_url(path)

    normalized = {key.lower(): value for key, value in body.items()}

    id_ = str(uuid.uuid4())

    normalized["id"] = id_

    virtual_salesforce.create(sobject, normalized)

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

    normalized = {key.lower(): value for key, value in body.items()}

    normalized_object_name = sobject.lower()

    objects = virtual_salesforce.get_sobjects(sobject)

    try:
        original, index = find_object_and_index(
            objects, "id" if not upsert_key else upsert_key, record_id
        )
        virtual_salesforce.data[normalized_object_name][index] = {
            **original,
            **normalized,
        }
    except KeyError:
        id_ = str(uuid.uuid4())
        normalized["id"] = id_
        if upsert_key:
            normalized[upsert_key] = record_id
        virtual_salesforce.data[normalized_object_name].append(normalized)

    return (
        204,
        {},
        json.dumps({}),
    )


def delete_callback(request):
    url = request.url
    path = urlparse(url).path

    sobject, _, record_id = parse_detail_url(path)

    objects = virtual_salesforce.get_sobjects(sobject)

    index = None
    for idx, object_ in enumerate(objects):
        if object_["id"] == record_id:
            index = idx

    objects.pop(index)

    return (
        204,
        {},
        json.dumps({}),
    )