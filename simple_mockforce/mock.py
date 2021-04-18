import re

from functools import reduce, partial

from unittest.mock import patch

from simple_salesforce import Salesforce, SalesforceMalformedRequest


def MockSalesforceLogin(*args, **kwagrs):
    return "mock_session_id", "mock_sf_instance"


class MockSalesforce(Salesforce):
    raise NotImplementedError

    @patch("simple_salesforce.api.SalesforceLogin", MockSalesforceLogin)
    def __init__(
        self,
        *args,
        **kwagrs,
    ):
        super().__init__(
            *args,
            **kwagrs,
        )
        # will store {'Contact': [{"Id": "123456789123456789", # ... }], # ... }
        # self.instance_mock_data = dict()
        self.instance_mock_data = {
            "Contact": [{"Id": "123", "Name": "Bob"}, {"Id": "124", "Name": "John"}]
        }

    def query(self, query, include_deleted=False, **kwargs):
        try:
            components = re.split("SELECT | FROM |,", query)
            components.pop(0)  # remove empty string element at beginning
            object_name = components.pop(-1)
            fields = [*map(lambda component: component.strip(), components)]
            objects = self.instance_mock_data[object_name]
            return [
                *map(lambda record: {field: record[field] for field in fields}, objects)
            ]
        except:
            raise SalesforceMalformedRequest
