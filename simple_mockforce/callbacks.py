import json

from python_soql_parser import parse

from simple_mockforce.state import virtual_salesforce


def query_callback(request):
    headers = {}
    parse_results = parse(request.params["q"])
    sobject = parse_results["sobject"]
    fields = parse_results["fields"].asList()
    limit = parse_results["limit"].asList()
    objects = virtual_salesforce.data[sobject]
    # TODO: construct attributes
    records = [*map(lambda record: {field: record[field] for field in fields}, objects)]
    if limit:
        records = records[: limit[0]]

    body = {
        "totalSize": len(records),
        "done": True,
        "records": records,
    }
    return (200, headers, json.dumps(body))