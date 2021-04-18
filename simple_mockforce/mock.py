import json
import re
import httpretty


from python_soql_parser import parse

from simple_salesforce import Salesforce

from simple_mockforce.patch_constants import LOGIN_URL, SOAP_API_LOGIN_RESPONSE


class MockSalesforce(Salesforce):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        httpretty.enable(allow_net_connect=False)
        httpretty.register_uri(
            httpretty.POST,
            uri=re.compile(LOGIN_URL),
            body=SOAP_API_LOGIN_RESPONSE,
            content_type="text/xml",
        )
        super().__init__(
            *args,
            **kwargs,
        )
        # will store {'Contact': [{"Id": "123456789123456789", # ... }], # ... }
        # self.instance_mock_data = dict()
        self.instance_mock_data = {
            "contact": [{"id": "123", "name": "Bob"}, {"id": "124", "name": "John"}]
        }

    def query_all(self, query, include_deleted, **kwargs):
        """
        Unit tests should use a low volume of data. Simply calling query instead will suffice
        """
        return self.query(query, include_deleted=include_deleted, **kwargs)

    def query(self, query, include_deleted=False, **kwargs):
        parse_results = parse(query)
        sobject = parse_results["sobject"]
        fields = parse_results["fields"].asList()
        limit = parse_results["limit"]

        objects = self.instance_mock_data[sobject]

        # TODO: construct attributes
        records = [
            *map(lambda record: {field: record[field] for field in fields}, objects)
        ]

        if limit:
            records[: limit[0][1]]

        body = {
            "totalSize": len(records),
            "done": True,
            "records": records,
        }
        url = self.base_url + ("queryAll/" if include_deleted else "query/")

        httpretty.register_uri(
            httpretty.GET,
            uri=url,
            body=json.dumps(body),
            content_type="content/json",
        )

        return super().query(query, include_deleted=include_deleted, **kwargs)