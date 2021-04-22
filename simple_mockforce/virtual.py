# TODO: determine if provisioning should be implicit like it is now, or if it should be explicitly done
import random
import string

from python_soql_parser import parse
from simple_mockforce.utils import (
    find_object_and_index,
)


class VirtualSalesforce:
    """
    A global, in-memory store for all the written data when calling with @mock_salesforce

    As of now, all objects are assumed to exist (and provisioned if they don't already).
    This class does not yet mimic any of the validation you'd see with Salesforce server-side
    """

    def __init__(self):
        # will store {'contact': [{"Id": "123456789123456789", # ... }], # ... }
        # this is the mega-dictionary that stores it all
        # self.data = dict()
        self.data = {
            "Contact": [
                {"Id": "123", "Name": "Bob"},
                {"Id": "124", "Name": "John", "customExtIdField__c": "9999"},
            ]
        }

        self.jobs = dict()
        self.batches = dict()
        self.batch_data = dict()

    def reset(self):
        """
        Clears stored data. Useful to prevent test pollution
        """
        self.data = dict()
        self.jobs = dict()
        self.batches = dict()
        self.batch_data = dict()

    # SOQL

    def query(self, soql: str):
        parse_results = parse(soql)
        parsed_sobject = parse_results["sobject"]

        sobject = None
        for sobject_name in self.data.keys():
            if sobject_name.lower() == parsed_sobject.lower():
                sobject = sobject_name

        # TODO: throw some Salesforce error about the object not existing?
        assert (
            sobject
        ), f"{parsed_sobject} not present in the virtual Salesforce objects"

        fields = parse_results["fields"].asList()
        limit = parse_results["limit"].asList()
        sobjects = self.get_sobjects(sobject)

        records = list()
        # TODO: do this in a more algorithm efficient way
        for sobject in sobjects:
            normalized_sobject = {key.lower(): value for key, value in sobject.items()}
            record = {field: normalized_sobject.get(field) for field in fields}
            records.append(record)

        if limit:
            limit: int = limit[0]
            records = records[:limit]

        return records

    # CRUD

    def get(self, sobject_name: str, record_id: str):
        for sobject in self.data[sobject_name]:
            if sobject["Id"] == record_id:
                return sobject
        # TODO: somehow mock the error we'd get from Salesforce instead?
        raise AssertionError(f"Could not find {record_id} in {sobject_name}s")

    def get_by_custom_id(self, sobject_name: str, record_id: str, custom_id_field: str):
        for sobject in self.data[sobject_name]:
            if sobject.get(custom_id_field) == record_id:
                return sobject
        # TODO: ditto
        raise AssertionError(f"Could not find {record_id} in {sobject_name}s")

    def update(self, sobject_name: str, record_id: str, data: dict):
        original, index = find_object_and_index(
            self.data[sobject_name],
            "Id",
            record_id,
        )
        self.data[sobject_name][index] = {
            **original,
            **data,
        }

    def upsert(self, sobject_name: str, record_id: str, sobject: dict, upsert_key: str):
        _, index = find_object_and_index(
            self.data[sobject_name],
            upsert_key,
            record_id,
        )
        if not index:
            return self.create(sobject_name, sobject)
        else:
            return self.data[sobject_name][0]["Id"]

    def create(self, sobject_name: str, sobject: dict):
        id_ = self._generate_sfdc_id()
        sobject["Id"] = id_
        self._provision_sobject(sobject_name)
        self.data[sobject_name].append(sobject)
        return id_

    def delete(self, sobject_name: str, record_id: str):
        index = None
        for idx, object_ in enumerate(self.data[sobject_name]):
            if object_["Id"] == record_id:
                index = idx

        self.data[sobject_name].pop(index)

    # bulk stuff

    def create_job(self, job: dict):
        job_id = self._generate_sfdc_id()
        job = {**job, "id": job_id}
        self.jobs[job_id] = job
        return job

    def create_batch(self, job_id: str, data: dict, operation: str):
        batch_id = self._generate_sfdc_id()
        batch = {
            "id": batch_id,
            "jobId": job_id,
        }
        self.batches[batch_id] = batch
        self.batch_data[batch_id] = data
        return batch

    # utils

    def get_sobjects(self, sobject_name: str):
        """
        Returns the objects currently loaded into the virtual instance
        """
        self._provision_sobject(sobject_name)
        return self.data[sobject_name]

    def _provision_sobject(self, sobject_name: str):
        """
        Provisions a virtual Salesfoce object

        Use the word "provision" instead of "create" as to not confuse with creating an instance of an object
        """
        if sobject_name not in self.data:
            self.data[sobject_name] = []

    @staticmethod
    def _generate_sfdc_id():
        return "".join(random.choices(string.ascii_letters + string.digits, k=18))

    @staticmethod
    def _get_pk_name(external_id_field: str = None):
        if external_id_field:
            return external_id_field
        return "Id"


virtual_salesforce = VirtualSalesforce()