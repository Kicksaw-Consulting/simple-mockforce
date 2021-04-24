# TODO: determine if provisioning should be implicit like it is now, or if it should be explicitly done
import random
import string

from python_soql_parser import parse

from simple_salesforce.exceptions import SalesforceResourceNotFound

from simple_mockforce.query import (
    filter_by_where_clause,
)
from simple_mockforce.utils import find_object_and_index

from logging import getLogger

logger = getLogger(__name__)


class VirtualSalesforce:
    """
    A global, in-memory store for all the written data when calling with @mock_salesforce

    As of now, all objects are assumed to exist (and provisioned if they don't already).
    This class does not yet mimic any of the validation you'd see with Salesforce server-side
    """

    def __init__(self):
        self.create_new_virtual_instance()
        self.data["Account"] = []

    def create_new_virtual_instance(self):
        """
        Starts a virtual Salesforce instance from scratch. Useful to prevent test pollution
        """
        self.data = dict()
        self.jobs = dict()
        self.batches = dict()
        self.batch_data = dict()

    # SOQL

    def query(self, soql: str):
        logger.warning(
            "Mocking 'query' is not yet fully supported. You should watch your tests closely if you're using this feature."
        )
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
        where = parse_results["where"].asList()

        limit = parse_results["limit"].asList()
        sobjects = self.get_sobjects(sobject)

        records = list()

        for sobject in sobjects:
            passes = filter_by_where_clause(sobject, where)
            if not passes:
                continue

            record = {field: sobject.get(field) for field in fields}
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
        raise AssertionError(f"Could not find {record_id} in {sobject_name}s")

    def get_by_custom_id(self, sobject_name: str, record_id: str, custom_id_field: str):
        for sobject in self.data[sobject_name]:
            if sobject.get(custom_id_field) == record_id:
                return sobject
        raise AssertionError(f"Could not find {record_id} in {sobject_name}s")

    def update(self, sobject_name: str, record_id: str, data: dict):
        original, index = find_object_and_index(
            self.data[sobject_name],
            "Id",
            record_id,
        )
        assert index is not None, f"Could not find {record_id} in {sobject_name}s"
        sobject = self._normalize_relation_via_external_id_field(data)
        self.data[sobject_name][index] = {
            **original,
            **sobject,
        }

    def upsert(self, sobject_name: str, record_id: str, sobject: dict, upsert_key: str):
        self._provision_sobject(sobject_name)
        _, index = find_object_and_index(
            self.data[sobject_name],
            upsert_key,
            record_id,
        )

        if index is None:
            return self.create(sobject_name, sobject)
        else:
            sfdc_id = self.data[sobject_name][index]["Id"]
            self.update(sobject_name, sfdc_id, sobject)
            return sfdc_id

    def create(self, sobject_name: str, sobject: dict):
        id_ = self._generate_sfdc_id()
        sobject["Id"] = id_
        sobject = self._normalize_relation_via_external_id_field(sobject)

        self._provision_sobject(sobject_name)
        self.data[sobject_name].append(sobject)
        return id_

    def delete(self, sobject_name: str, record_id: str):
        index = None
        for idx, object_ in enumerate(self.data[sobject_name]):
            if object_["Id"] == record_id:
                index = idx

        assert index is not None, f"Could not found {record_id} in {sobject_name}s"

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

    def _normalize_relation_via_external_id_field(self, sobject: dict):
        """
        We need to relate an object which was pushed via an external key with a master-detail
        relationship to its related object in the virtual data
        """
        normalized = dict()
        for key, value in sobject.items():
            if key.endswith("__r"):
                # We assume there's only one key in this dict
                for external_id_field, external_id in value.items():
                    related_object_name = key.replace("__r", "__c")
                    related_object = self.get_by_custom_id(
                        related_object_name, external_id, external_id_field
                    )
                    normalized[related_object_name] = related_object["Id"]
            else:
                normalized[key] = value
        return normalized

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


virtual_salesforce = VirtualSalesforce()