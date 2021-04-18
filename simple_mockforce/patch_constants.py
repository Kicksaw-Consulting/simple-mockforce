SF_VERSION = "[0-9]*[.]0"
BASE_URL = "https?://([a-z0-9]+[.])*salesforce[.]com"
DESCRIBE_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/sobjects/Contact/describe"
# example of query string if we decide to use q=Select+FirstName+from+Contact+
QUERY_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/query/"
LOGIN_URL = f"{BASE_URL}/services/Soap/u/{SF_VERSION}"
SOAP_API_LOGIN_RESPONSE = f'<?xml version="1.0"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><loginResponse><result><serverUrl>https://mock.salesforce.com</serverUrl><sessionId></sessionId></result></loginResponse></soapenv:Body></soapenv:Envelope>'
