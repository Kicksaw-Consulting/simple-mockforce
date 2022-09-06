from typing import Dict
import json

MOCK_CREDS = {
    "username": "hi",
    "password": "hello",
    "security_token": "123",
    "domain": "mock",
}

MOCK_CREDS_USING_PRIVATE_KEY = {
    "username": "hi",
                "privatekey": """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCx+jeTYRH4eS2iCBw/5BklAIUx3H8sZXvZ4d5HBBYLTJ8Z1Ura
RHBATBxRNBuPH3U43d0o2aykg2n8VkbdzHYX+BaKrltB1DMx/KLa38gE1XIIlJBh
+e75AspHzojGROAA8G7uzKvcndL2iiLMsJ3Hbg28c1J3ZbGjeoxnYlPcwQIDAQAB
AoGBAJKyvwpgsZJQN7fd3YMgPUWNlzwRFlX+1EY0caWxjYYEwwNlFsywKqIk2hZo
z+p5sIKOBVQ9j5sOotaWOtVpSVB6OBOQP7F8LI21QBm0qIyOhLwsEHTg/D3YHPU9
RInjp1NXel5G679GaeAn3sYypCO8hvEKF/hclblsriAZnbP9AkEA3xVvqF1TJWAR
6mpLVTx2t8QipIZn20b2DpWTevSST/2zoY/jw3DJWEo/IXqmCv1KJ9Cp+9zmo2M7
OSdPHEO0swJBAMw8+a2Asujb9Z/NOcPeJY192aZymhDtN4+KF2Lh53BHajU4VBLC
y/KjMOHHRaq/jVxAyiS6rFevqs3pGk2gqrsCQDV2U64Lv5NjdKezFZ61wNXFgW/g
bh9U4D8ahZ+f4TieWmBLtY/vBbHNCVgipoxXq1/jV/luNS/O5jCKRSFG8JUCQHce
DQT7bd1QBIbKPCmXk9FdGCby6hZ7NA98m70pQkGC9VfK3YX/pNGECkt0XJaEl965
TuxzD3co1na3wIaL8WcCQQCAOHE0Ji5IjpTp1WSIvL/RT3vTuA4gDIsTRAIt92pz
YZNQnrTiTHnNB8xT5jG3Svz0INueT4RpTJIFl/+wB1kV
-----END RSA PRIVATE KEY-----""",
                "consumer_key": 123,
                "domain": "mock",
}

STANDARD_FIELDS_WITHOUT_USER = ["Id", "IsDeleted", "LastModifiedDate", "CreatedDate", "SystemModstamp"]
USER_STANDARD_FIELDS = ["LastModifiedById", "CreatedById"]


def to_dict(input_ordered_dict):
    """
    Useful for getting rid of OrderedDicts
    """
    return json.loads(json.dumps(input_ordered_dict))


def filter_user_fields(salesforce_object: Dict[str, str]) -> Dict[str, str]:
    return {key: value for key, value in salesforce_object.items() if key not in USER_STANDARD_FIELDS}