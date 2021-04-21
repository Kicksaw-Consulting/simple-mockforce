import json

from urllib.parse import urlparse

from simple_mockforce.utils import (
    parse_batch_detail_url,
    parse_batch_result_url,
    parse_detail_url,
    parse_create_url,
    parse_job_batch_url,
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


def job_callback(request):
    """
    Note, this will be called again when simple salesforce calls close job,
    but it's basically a no-op as far as we're concerned at that point
    """
    body = json.loads(request.body)
    print("first")

    sobject = body.get("object")

    job = virtual_salesforce.create_job(sobject)

    return (
        201,
        {},
        json.dumps(job),
    )


def job_detail_callback(request):
    print("fifth")
    return (
        201,
        {},
        json.dumps({}),
    )


def bulk_callback(request):
    url = request.url
    path = urlparse(url).path
    body = json.loads(request.body)

    print("second")

    job_id = parse_job_batch_url(path)
    sobject_name = virtual_salesforce.jobs[job_id]["object"]

    created_ids = list()
    for sobject in body:
        id_ = virtual_salesforce.create(sobject_name, sobject)
        created_ids.append(id_)

    fake_response = {
        "id": "idontmatter",
        "jobId": job_id,
    }

    return (
        201,
        {},
        json.dumps(fake_response),
    )


def bulk_detail_callback(request):
    url = request.url
    path = urlparse(url).path

    job_id, batch_id = parse_batch_detail_url(path)

    fake_response = {
        "id": batch_id,
        "jobId": job_id,
        "state": "Completed",
    }

    print("third")

    return (
        201,
        {},
        json.dumps(fake_response),
    )


def bulk_result_callback(request):
    url = request.url
    path = urlparse(url).path

    print("fourth")

    job_id, batch_id = parse_batch_result_url(path)

    fake_response = {
        "id": batch_id,
        "jobId": job_id,
        "state": "Completed",
    }

    return (
        201,
        {},
        json.dumps(fake_response),
    )