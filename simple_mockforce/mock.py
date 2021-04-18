import re

import httpretty

from functools import reduce, partial

from simple_salesforce import Salesforce, SalesforceMalformedRequest


SF_VERSION = "[0-9]*[.]0"
BASE_URL = "https?://([a-z0-9]+[.])*salesforce[.]com"
DESCRIBE_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/sobjects/Contact/describe"
# example of query string if we decide to use q=Select+FirstName+from+Contact+
QUERY_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/query/"
LOGIN_URL = f"{BASE_URL}/services/Soap/u/{SF_VERSION}"
SOAP_API_LOGIN_RESPONSE = f'<?xml version="1.0"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><loginResponse><result><serverUrl>{BASE_URL}</serverUrl><sessionId></sessionId></result></loginResponse></soapenv:Body></soapenv:Envelope>'


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
