# foundations
SF_VERSION = "[0-9]*[.]0"
BASE_URL = "https?://([a-z0-9]+[.])*salesforce[.]com"


# CRUD and query stuff
QUERY_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/query/"
DETAIL_URL = (
    f"{BASE_URL}/services/data/v{SF_VERSION}/sobjects/[a-zA-Z0-9]*/[a-zA-Z0-9]*"
)
CREATE_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/sobjects/[a-zA-Z0-9]*/"
DESCRIBE_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/sobjects/Contact/describe"


# bulk stuff
JOB_URL = f"{BASE_URL}/services/async/{SF_VERSION}/job"
JOB_DETAIL_URL = f"{BASE_URL}/services/async/{SF_VERSION}/job/[a-zA-Z0-9]*"
BATCH_URL = f"{BASE_URL}/services/async/{SF_VERSION}/job/[a-zA-Z0-9]*/batch"
BATCH_DETAIL_URL = (
    f"{BASE_URL}/services/async/{SF_VERSION}/job/[a-zA-Z0-9]*/batch/[a-zA-Z0-9]*"
)
BATCH_RESULT_URL = (
    f"{BASE_URL}/services/async/{SF_VERSION}/job/[a-zA-Z0-9]*/batch/[a-zA-Z0-9]*/result"
)


# login stuff
LOGIN_URL = f"{BASE_URL}/services/Soap/u/{SF_VERSION}"
# bare minimum needed to make simple salesforce happy
SOAP_API_LOGIN_RESPONSE = f"""<?xml version="1.0"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <loginResponse>
      <result>
        <serverUrl>https://mock.salesforce.com</serverUrl>
        <sessionId></sessionId>
      </result>
    </loginResponse>
  </soapenv:Body>
</soapenv:Envelope>
"""
