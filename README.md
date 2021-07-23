# Introduction

This library was inspired by [moto](https://github.com/spulec/moto) and mimics some of its design. Mainly,
no `simple-salesforce` code is patched; instead, the HTTP calls it makes are intercepted, and state is
stored in an in-memory, virtual Salesforce organization, which is just a globally instantiated class that
is created at the run-time of a test-suite.

# Installation

`pip install simple-mockforce`

or, with poetry

`poetry add simple-mockforce`

# Usage

To patch calls to the Salesforce API and instead interact with the "virtual"
Salesforce organization provided by this library, add the following:

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

    response = salesforce.Account.create({"Name": "Test Account"})

    account_id = response["id"]

    account = salesforce.Account.get(account_id)

    assert account["Name"] == "Test Account"
```

To reset state, you can pass `fresh=True`,
ensuring there's no pollution between tests

```python
from simple_mockforce.virtual import virtual_salesforce


# This will wipe away the account created in the above step
@mock_salesforce(fresh=True)
def test_api_again():
    pass
```

And that's about it!

# Caveats

## Case sensitivity

Unlike a real Salesforce organization, the virtual organization will not handle case-insensitive
dependent code for you. You must remain consistent with your casing of object and field
names in all aspects of the code.

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

Notable mentions:

- be explicit with direction in `ORDER BY` clauses, i.e., always supply `DESC` or `ASC`
- attributes of parent objects can be specified in the `select` clause (but not in the `where` clause)

## Error handling

Error handling is only mocked to a degree, and for some calls it isn't at all.
This is because the virtual Salesforce organization does not yet enforce any of
the server-side validation when working with a real API.

This means that the virtual organization is much more permissive and loose than a
real Salesforce organization would be.

There are plans to read the XML consumed by the meta API in order to enforce
more rigidity inside the virtual organization, but this is not yet implemented.

## All HTTP traffic is blocked

When using `@mock_salesforce`, do note that the `requests` library is being
patched with `responses`, so any calls you make to any other APIs will fail
unless you patch them yourself, or patch the code which invokes said calls.

## Relations

Relations are the weakest part of this library, and some features are just
plain not supported yet.

If you have a relational field that points to an object whose name cannot be
inferred from the field name (e.g., from `Account__r` it can be inferred
that this is pointing to an `Account` object), you can create a file called
`relations.json` that translates a relational field name to your intended
Salesforce object's name. See `relations.json` in the test folder for an
example.

To specify the location of `relations.json`, set an environment variable
called `MOCKFORCE_RELATIONS_ROOT` which points to the parent folder of
`relations.json`. Note, this defaults to the current directory `.`.
