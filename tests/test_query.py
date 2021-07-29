import datetime

import pytest

from python_soql_parser.tokens import TODAY, TOMORROW, YESTERDAY

from simple_mockforce import mock_salesforce
from simple_salesforce import Salesforce

from tests.utils import MOCK_CREDS

import simple_mockforce.query_algorithms.where as where_module


@mock_salesforce(fresh=True)
def test_basic_query():
    salesforce = Salesforce(**MOCK_CREDS)

    salesforce.Contact.create({"Name": "Ozzy Osbourne"})

    results = salesforce.query("SELECT Id, Name FROM Contact LIMIT 1")
    records = results["records"]

    assert len(records) == 1
    record = records[0]
    assert record["Id"]
    assert record["Name"] == "Ozzy Osbourne"


@mock_salesforce(fresh=True)
def test_where_basic_query():
    salesforce = Salesforce(**MOCK_CREDS)

    response = salesforce.Lead.create({"Name": "Jim Bean", "Title": "CDO"})
    sfdc_id = response["id"]
    response = salesforce.Lead.create({"Name": "Corey Taylor", "Title": "Singer"})

    results = salesforce.query(f"SELECT Id, Name FROM Lead WHERE Id = 'nothing'")
    records = results["records"]
    assert len(records) == 0

    results = salesforce.query(f"SELECT Id, Name FROM Lead WHERE Name = null")
    records = results["records"]
    assert len(records) == 0

    results = salesforce.query(
        f"SELECT Id, Name, Title FROM Lead WHERE Id = '{sfdc_id}'"
    )
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["Id"] == sfdc_id
    assert record["Name"] == "Jim Bean"
    assert record["Title"] == "CDO"


@mock_salesforce(fresh=True)
def test_where_bool_query():
    salesforce = Salesforce(**MOCK_CREDS)

    response = salesforce.Opportunity.create({"Name": "Opp 1", "IsDeleted": True})
    deleted_opp_id = response["id"]
    response = salesforce.Opportunity.create({"Name": "Opp 2", "IsDeleted": False})
    active_opp_id = response["id"]

    results = salesforce.query(
        f"SELECT Id, Name, IsDeleted FROM Opportunity WHERE IsDeleted = true"
    )
    records = results["records"]
    assert len(records) == 1
    deleted_record = records[0]
    assert deleted_record["Name"] == "Opp 1"
    assert deleted_record["Id"] == deleted_opp_id
    assert deleted_record["IsDeleted"]

    results = salesforce.query(
        f"SELECT Id, Name, IsDeleted FROM Opportunity WHERE IsDeleted = false"
    )
    records = results["records"]
    assert len(records) == 1
    active_record = records[0]
    assert active_record["Name"] == "Opp 2"
    assert active_record["Id"] == active_opp_id
    assert not active_record["IsDeleted"]

    results = salesforce.query(f"SELECT Id FROM Opportunity")
    records = results["records"]
    assert len(records) == 2


@pytest.mark.parametrize(
    "operator,number,expected",
    [
        # <
        ("<", 100, 0),
        ("<", 120, 1),
        # <=
        ("<=", 100, 1),
        ("<=", 5, 0),
        # >
        (">", 101, 0),
        (">", 4, 1),
        # >=
        (">=", 100, 1),
        (">=", 999, 0),
    ],
)
@mock_salesforce(fresh=True)
def test_where_comparison_query(operator, number, expected):
    salesforce = Salesforce(**MOCK_CREDS)

    response = salesforce.bulk.Lead.insert(
        [
            {
                "Name": "Kurt Cobain",
                "Title": "Nirvana Guitarist",
                "Human_Score__c": 100,
            },
            {"Name": "Paris Hilton", "Title": "no one knows"},
        ]
    )
    sfdc_id = response[0]["id"]

    results = salesforce.query(
        f"SELECT Id, Name, Human_Score__c FROM Lead WHERE Human_Score__c {operator} {number}"
    )
    records = results["records"]
    assert len(records) == expected

    if expected > 0:
        record = records[0]
        assert record["Id"] == sfdc_id
        assert record["Name"] == "Kurt Cobain"
        assert record["Human_Score__c"] == 100


@mock_salesforce(fresh=True)
def test_where_complex_query():
    salesforce = Salesforce(**MOCK_CREDS)

    response = salesforce.SomeFamousPerson__c.create(
        {"Name": "Quentin Tarantino", "Title": "Director"}
    )
    tarantino_id = response["id"]
    response = salesforce.SomeFamousPerson__c.create(
        {"Name": "Steven Spielberg", "Title": "Director"}
    )
    spielberg_id = response["id"]
    response = salesforce.SomeFamousPerson__c.create(
        {"Name": "Amy Adams", "Title": "Actor"}
    )
    adams_id = response["id"]

    results = salesforce.query(
        f"SELECT Id, Name FROM SomeFamousPerson__c WHERE Name = 'Quentin Tarantino' OR Name = 'Amy Adams'"
    )
    records = results["records"]
    assert len(records) == 2
    record = records[0]
    assert record["Id"] == tarantino_id
    record = records[1]
    assert record["Id"] == adams_id

    results = salesforce.query(
        f"SELECT Id, Name FROM SomeFamousPerson__c WHERE (Title = 'Director' OR Name = 'Amy Adams') AND Id != null"
    )
    records = results["records"]
    assert len(records) == 3
    record = records[0]
    assert record["Id"] == tarantino_id
    record = records[1]
    assert record["Id"] == spielberg_id
    record = records[2]
    assert record["Id"] == adams_id

    results = salesforce.query(
        f"SELECT Id, Name FROM SomeFamousPerson__c WHERE (Title = 'Actor' OR Title = 'Director') AND Name = null"
    )
    records = results["records"]
    assert len(records) == 0

    results = salesforce.query(
        f"SELECT Id, Name FROM SomeFamousPerson__c WHERE (Title = 'Actor' OR Title = 'Director') AND (Name != null AND Name = 'Quentin Tarantino')"
    )
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["Id"] == tarantino_id


@mock_salesforce(fresh=True)
def test_order_by_query():
    salesforce = Salesforce(**MOCK_CREDS)

    salesforce.bulk.Account.insert(
        [
            {"Name": "Google", "AlexaRanking__c": 1},
            {"Name": "YouTube", "AlexaRanking__c": 2},
            {"Name": "Facebook", "AlexaRanking__c": 7},
        ]
    )

    results = salesforce.query("SELECT Name FROM Account ORDER BY Name ASC")
    records = results["records"]

    record1 = records[0]
    record2 = records[1]
    record3 = records[2]

    assert record1["Name"] == "Facebook"
    assert record2["Name"] == "Google"
    assert record3["Name"] == "YouTube"

    results = salesforce.query("SELECT Name FROM Account ORDER BY Name DESC")
    records = results["records"]

    record1 = records[0]
    record2 = records[1]
    record3 = records[2]

    assert record3["Name"] == "Facebook"
    assert record2["Name"] == "Google"
    assert record1["Name"] == "YouTube"

    # not possible, but let's pretend
    salesforce.Account.create(
        {"Name": "Google dupe", "AlexaRanking__c": 1},
    )

    results = salesforce.query(
        "SELECT Name FROM Account ORDER BY AlexaRanking__c ASC, Name DESC"
    )
    records = results["records"]

    record1 = records[0]
    record2 = records[1]
    record3 = records[2]
    record4 = records[3]

    assert record1["Name"] == "Google dupe"
    assert record2["Name"] == "Google"
    assert record3["Name"] == "YouTube"
    assert record4["Name"] == "Facebook"


@mock_salesforce(fresh=True)
def test_query_with_parent_object_attribute():
    salesforce = Salesforce(**MOCK_CREDS)

    response = salesforce.Account.create({"Name": "Google", "Website": "google.com"})
    account_id = response["id"]

    response = salesforce.Contact.create(
        {
            "FirstName": "Sundar",
            "LastName": "Pichai",
            "Account": account_id,
            "Title": "CEO",
        }
    )
    contact_id = response["id"]

    results = salesforce.query(
        "SELECT Id, Title, FirstName, LastName, Account.Name FROM Contact"
    )
    records = results["records"]

    assert len(records) == 1
    record = records[0]
    assert record["Id"] == contact_id
    assert record["FirstName"] == "Sundar"
    assert record["LastName"] == "Pichai"
    assert record["Title"] == "CEO"
    assert record["Account"]["Name"] == "Google"


@mock_salesforce(fresh=True)
def test_query_with_custom_parent_object_attribute():
    salesforce = Salesforce(**MOCK_CREDS)

    response = salesforce.CustomObj__c.create({"Name": "I'm Custom"})
    custom_object_id = response["id"]

    response = salesforce.Lead.create(
        {
            "Name": "Super Lead",
            "CustomObj__c": custom_object_id,
        }
    )
    lead_id = response["id"]

    results = salesforce.query("SELECT Id, Name, CustomObj__r.Name FROM Lead")
    records = results["records"]

    assert len(records) == 1
    record = records[0]
    assert record["Id"] == lead_id
    assert record["Name"] == "Super Lead"
    assert record["CustomObj__r"]["Name"] == "I'm Custom"


class JamesDOB:
    def today(*args, **kwargs):
        return datetime.datetime(1963, 8, 3)


class DayBeforeLarsDOB:
    def today(*args, **kwargs):
        return datetime.datetime(1963, 12, 25)


class DayAfterLarsDOB:
    def today(*args, **kwargs):
        return datetime.datetime(1963, 12, 27)


@mock_salesforce(fresh=True)
def test_where_query_with_dates(monkeypatch):
    salesforce = Salesforce(**MOCK_CREDS)

    monkeypatch.setattr(where_module, "date", JamesDOB)

    salesforce.bulk.Lead.insert(
        [
            {
                "Name": "James Hetfield",
                "Title": "Metallica's Frontman",
                "DOB__c": "1963-08-03",
            },
            {
                "Name": "Lars Ulrich",
                "Title": "Metallica's Drummer",
                "DOB__c": "1963-12-26",
            },
            {
                "Name": "Kirk Hammet",
                "Title": "Metallica's Lead Guitarist",
                "DOB__c": None,
            },
            {
                "Name": "Robert Trujillo",
                "Title": "Metallica's Bassist",
                "DOB__c": "1964-10-23",
            },
        ]
    )

    results = salesforce.query(f"SELECT Name FROM Lead WHERE DOB__c = {TODAY}")
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["Name"] == "James Hetfield"

    monkeypatch.setattr(where_module, "date", DayBeforeLarsDOB)

    results = salesforce.query(f"SELECT Name FROM Lead WHERE DOB__c = {TOMORROW}")
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["Name"] == "Lars Ulrich"

    monkeypatch.setattr(where_module, "date", DayAfterLarsDOB)

    results = salesforce.query(f"SELECT Name FROM Lead WHERE DOB__c = {YESTERDAY}")
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["Name"] == "Lars Ulrich"

    results = salesforce.query(f"SELECT Name FROM Lead WHERE DOB__c > {YESTERDAY}")
    records = results["records"]
    assert len(records) == 1
    record = records[0]
    assert record["Name"] == "Robert Trujillo"
