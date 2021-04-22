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
        # will store {'contact': [{"id": "123456789123456789", # ... }], # ... }
        # this is the mega-dictionary that stores it all
        # self.data = dict()
        self.data = {
            "contact": [
                {"id": "123", "name": "Bob"},
                {"id": "124", "name": "John", "customextidfield__c": "9999"},
            ]
        }

        self.jobs = {}
        self.batches = {}
        self.batch_data = {}

    # SOQL

    def query(self, soql: str):
        parse_results = parse(soql)
        sobject = parse_results["sobject"]
        fields = parse_results["fields"].asList()
        limit = parse_results["limit"].asList()
        objects = self.get_sobjects(sobject)
        # TODO: construct attributes
        records = [
            *map(lambda record: {field: record.get(field) for field in fields}, objects)
        ]
        if limit:
            limit: int = limit[0]
            records = records[:limit]

        return records

    # CRUD

    def get(self, sobject_name: str, record_id: str):
        sobject_name = sobject_name.lower()
        for sobject in self.data[sobject_name]:
            if sobject["id"] == record_id:
                return sobject
        # TODO: somehow mock the error we'd get from Salesforce instead?
        raise AssertionError(f"Could not find {record_id} in {sobject_name}s")

    def get_by_custom_id(self, sobject_name: str, record_id: str, custom_id_field: str):
        sobject_name = sobject_name.lower()
        custom_id_field = custom_id_field.lower()
        print(self.data)
        print(custom_id_field, record_id)
        for sobject in self.data[sobject_name]:
            if sobject.get(custom_id_field) == record_id:
                return sobject
        # TODO: ditto
        raise AssertionError(f"Could not find {record_id} in {sobject_name}s")

    def update(self, sobject_name: str, record_id: str, data: dict):
        sobject_name = sobject_name.lower()
        data = self._normalize_data(data)
        original, index = find_object_and_index(
            self.data[sobject_name],
            "id",
            record_id,
        )
        self.data[sobject_name][index] = {
            **original,
            **data,
        }

    def upsert(self, sobject_name: str, record_id: str, sobject: dict, upsert_key):
        sobject_name = sobject_name.lower()
        sobject = self._normalize_data(sobject)
        _, index = find_object_and_index(
            self.data[sobject_name],
            upsert_key,
            record_id,
        )
        if not index:
            self.create(sobject_name, sobject)

    def create(self, sobject_name: str, sobject: dict):
        sobject = self._normalize_data(sobject)
        sobject_name = sobject_name.lower()
        id_ = self._generate_sfdc_id()
        sobject["id"] = id_
        self._provision_sobject(sobject_name)
        self.data[sobject_name].append(sobject)
        return id_

    def delete(self, sobject_name: str, record_id: str):
        sobject_name = sobject_name.lower()

        index = None
        for idx, object_ in enumerate(self.data[sobject_name]):
            if object_["id"] == record_id:
                index = idx

        self.data[sobject_name].pop(index)

    # bulk stuff

    def create_job(self, job: dict):
        job_id = self._generate_sfdc_id()
        job = {**job, "id": job_id}
        self.jobs[job_id] = job
        return job

    def create_batch(self, job_id, data, operation):
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
        sobject_name = sobject_name.lower()
        self._provision_sobject(sobject_name)
        return self.data[sobject_name]

    def _provision_sobject(self, sobject_name: str):
        """
        Provisions a virtual Salesfoce object

        Use the word "provision" instead of "create" as to not confuse with creating an instance of an object
        """
        sobject_name = sobject_name.lower()
        if sobject_name not in self.data:
            self.data[sobject_name] = []

    @staticmethod
    def _generate_sfdc_id():
        return "".join(random.choices(string.ascii_letters + string.digits, k=18))

    @staticmethod
    def _normalize_data(data: dict):
        return {key.lower(): value for key, value in data.items()}

    @staticmethod
    def _get_pk_name(external_id_field: str = None):
        if external_id_field:
            return external_id_field
        return "id"


virtual_salesforce = VirtualSalesforce()