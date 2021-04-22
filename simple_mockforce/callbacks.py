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

    if not upsert_key:
        virtual_salesforce.update(sobject, record_id, body)
    else:
        virtual_salesforce.upsert(sobject, record_id, body, upsert_key=upsert_key)

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

    job = virtual_salesforce.create_job(body)

    return (
        201,
        {},
        json.dumps(job),
    )


def bulk_callback(request):
    url = request.url
    path = urlparse(url).path
    body = json.loads(request.body)

    job_id = parse_job_batch_url(path)
    job = virtual_salesforce.jobs[job_id]
    operation = job["operation"]

    batch = virtual_salesforce.create_batch(job_id, body, operation)

    return (
        201,
        {},
        json.dumps(batch),
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

    return (
        201,
        {},
        json.dumps(fake_response),
    )


def bulk_result_callback(request):
    url = request.url
    path = urlparse(url).path

    job_id, batch_id = parse_batch_result_url(path)

    job = virtual_salesforce.jobs[job_id]
    sobject_name = job["object"]
    data = virtual_salesforce.batch_data[batch_id]

    created_ids = list()
    for sobject in data:
        id_ = virtual_salesforce.create(sobject_name, sobject)
        created_ids.append(id_)

    fake_response = [
        {
            "success": True,
            "created": True,
            "id": id_,
            "errors": [],
        }
        for id_ in created_ids
    ]

    return (
        201,
        {},
        json.dumps(fake_response),
    )


def job_detail_callback(request):
    """
    This is a no-op as far as we're concerned
    """
    return (
        201,
        {},
        json.dumps({}),
    )