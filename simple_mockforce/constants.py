# foundations
SF_VERSION = "[0-9]*[.]0"
BASE_URL = "https?://([a-z0-9]+[.])*salesforce[.]com"
SOBJECT = "[a-zA-Z0-9_]+"
SFDC_ID = "[a-zA-Z0-9]+"


# CRUD and query stuff
QUERY_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/query/"
QUERY_ALL_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/queryAll/"
DETAIL_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/sobjects/{SOBJECT}/{SFDC_ID}"
CREATE_URL = f"{BASE_URL}/services/data/v{SF_VERSION}/sobjects/{SOBJECT}/"


# bulk stuff
JOB_URL = f"{BASE_URL}/services/async/{SF_VERSION}/job"
JOB_DETAIL_URL = f"{BASE_URL}/services/async/{SF_VERSION}/job/{SFDC_ID}"
BATCH_URL = f"{BASE_URL}/services/async/{SF_VERSION}/job/{SFDC_ID}/batch"
BATCH_DETAIL_URL = (
    f"{BASE_URL}/services/async/{SF_VERSION}/job/{SFDC_ID}/batch/{SFDC_ID}"
)
BATCH_RESULT_URL = (
    f"{BASE_URL}/services/async/{SF_VERSION}/job/{SFDC_ID}/batch/{SFDC_ID}/result"
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

OAUTH_URL = f"{BASE_URL}/services/oauth2/token"
OAUTH_RESPONSE = """
{
  "access_token":"FAKE_ACCESS_TOKEN",
  "token_type":"Bearer",
  "expires_in":3600,
  "refresh_token":"FAKE_REFRESH_TOKEN",
  "scope":"create",
  "instance_url":"https://mock.salesforce.com"
}
"""
