# Introduction

This library was inspired by [moto](https://github.com/spulec/moto) and mimics some of its design. Mainly,
no `simple-salesforce` code is patched; instead, the HTTP calls it makes are intercepted, and state is
stored in an in-memory, virtual Salesforce instance, which is just a globally instantiated class that
is created at the run-time of a test-suite.

# Installation

`pip install simple-mockforce`

or, with poetry

`poetry add simple-mockforce`

# Usage

To patch calls to the Salesforce API and instead interact with the "virtual"
Salesforce instance provided by this library, add the following:

```python
import os

from simple_mockforce import mock_salesforce

from simple_salesforce import Salesforce


@mock_salesforce
def test_api():
    salesforce = Salesforce(
        username=os.getenv["SFDC_USERNAME"],
        password=os.getenv["SFDC_PASSWORD"],
        security_token=os.getenv["SFDC_SECURITY_TOKEN"]
    )

    salesforce.Account.create({"Name": "Test Account"})
```

To reset state, you can call `create_new_virtual_instance`,
ensuring there's no pollution between tests

```python
from simple_mockforce.virtual import virtual_salesforce


@mock_salesforce
def test_api_again():
    # This will wipe away the account created in the above step
    virtual_salesforce.create_new_virtual_instance()
```

And that's about it!

# Caveats

## Missing endpoints

The following features are currently not supported:

- the describe API
- bulk queries
- SOSL searches

## Queries

SOQL is only partially supported as of now. Please refer to the README
for [python-soql-parser](https://github.com/Kicksaw-Consulting/python-soql-parser#notable-unsupported-features)
to see what's not yet implemented.

You should only expect this library to be able to mock the most basic of queries.
While there are plans to, mocking query calls which traverse object relationships
or that use SOQL-specific where-clause tokens are not yet supported.

## Error handling

Error handling is only mocked to a degree, and for some calls it isn't at all.
This is because the virtual Salesforce instance does not yet enforce any of
the server-side validation when working with a real API.

This means that the virtual instance is much more permissive and loose than a
real Salesforce instance would be.

There are plans to read the XML consumed by the meta API in order to enforce
more rigidity inside the virtual instance, but this is not yet implemented.

## All HTTP traffic is blocked

When using `@mock_salesforce`, do note that the `requests` library is being
patched with `responses`, so any calls you make to any other APIs will fail
unless you patch them yourself, or patch the code which invokes.
