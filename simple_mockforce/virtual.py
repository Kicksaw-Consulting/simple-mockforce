# TODO: determine if provisioning should be implicit like it is now, or if it should be explicitly done
import datetime
import json
import os
import random
import string
from collections import defaultdict

from pathlib import Path

from python_soql_parser import parse

from simple_salesforce.exceptions import SalesforceResourceNotFound
from simple_mockforce.query_algorithms import (
    add_parent_object_attributes,
    filter_by_where_clause,
    sort_by_order_by_clause,
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
        self.provision()

        # temporary support for related object field names that don't
        # match the name of the related object, e.g., we can do Account__r,
        # but need this for when Company__r corresponds to an Account object
        path_to_relations_root = os.getenv("MOCKFORCE_RELATIONS_ROOT", ".")
        path_to_relations_json = Path(path_to_relations_root) / "relations.json"
        try:
            with open(path_to_relations_json) as file:
                relations_file = json.load(file)
            self.relations_file = relations_file
        except FileNotFoundError:
            self.relations_file = {}

    def provision(self):
        """
        Starts a virtual Salesforce instance from scratch. Useful to prevent test pollution
        """
        self.data = defaultdict(list)
        self.jobs = dict()
        self.batches = dict()
        self.batch_data = dict()

    # SOQL

    def query(self, soql: str, include_deleted: bool = False):
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

        all_fields = parse_results["fields"].asList()
        fields = list()
        parent_fields = list()

        for field in all_fields:
            if "." in field:
                parent_fields.append(field)
            else:
                fields.append(field)

        where = parse_results["where"].asList()

        limit = parse_results["limit"].asList()

        offset = parse_results["offset"].asList()

        # TODO: why do we need to check?
        order_by = (
            parse_results["order_by"].asList() if "order_by" in parse_results else None
        )
        sobjects = self.get_sobjects(sobject, include_deleted=include_deleted)

        records = list()

        if order_by:
            sort_by_order_by_clause(sobjects, order_by)

        for sobject in sobjects:
            passes = filter_by_where_clause(sobject, where)
            if not passes:
                continue

            record = {field: sobject.get(field) for field in fields}

            if parent_fields:
                add_parent_object_attributes(sobject, record, parent_fields, self)

            records.append(record)

        if offset:
            offset: int = offset[0]
            records = records[offset:] if offset >= 0 else records

        if limit:
            limit: int = limit[0]
            records = records[:limit]

        return records

    # CRUD

    def get(self, sobject_name: str, record_id: str):
        for sobject in self.get_sobjects(sobject_name):
            if sobject["Id"] == record_id:
                return sobject
        raise AssertionError(f"Could not find {record_id} in {sobject_name}s")

    def get_by_custom_id(self, sobject_name: str, record_id: str, custom_id_field: str):
        for sobject in self.get_sobjects(sobject_name):
            if sobject.get(custom_id_field) == record_id:
                return sobject
        raise AssertionError(f"Could not find {record_id} in {sobject_name}s")

    def update(self, sobject_name: str, record_id: str, data: dict, url: str = None):
        self._check_for_salesforce_resource(url, sobject_name)
        sobjects = self.get_sobjects(sobject_name)
        original, index = find_object_and_index(
            sobjects,
            "Id",
            record_id,
        )
        assert index is not None, f"Could not find {record_id} in {sobject_name}s"
        normalized_sobject = self._normalize_relation_via_external_id_field(data)
        sobject = self._update_datetime_fields(normalized_sobject)
        self.data[sobject_name][index] = {
            **original,
            **sobject,
        }

    def upsert(self, sobject_name: str, record_id: str, sobject: dict, upsert_key: str):
        sobjects = self.get_sobjects(sobject_name)
        _, index = find_object_and_index(
            sobjects,
            upsert_key,
            record_id,
        )

        # if this is a single object upsert, SFDC doesn't let you push the upsert key's value
        # up with the JSON. To mimic the server behavior, we need to explicitly add it here
        # even if it's not in the payload
        sobject[upsert_key] = record_id

        if index is None:
            return self.create(sobject_name, sobject), True
        else:
            sfdc_id = sobjects[index]["Id"]
            self.update(sobject_name, sfdc_id, sobject)
            return sfdc_id, False

    def create(self, sobject_name: str, sobject: dict):
        normalized_sobject = self._normalize_relation_via_external_id_field(sobject)
        sobject = self._add_system_fields(normalized_sobject)
        self.data[sobject_name].append(sobject)
        return sobject["Id"]

    def delete(self, sobject_name: str, record_id: str, url: str = None):
        self._check_for_salesforce_resource(url, sobject_name)
        index = None
        sobjects = self.get_sobjects(sobject_name)
        for idx, object_ in enumerate(sobjects):
            if object_["Id"] == record_id:
                index = idx

        assert index is not None, f"Could not found {record_id} in {sobject_name}s"

        sobject = sobjects[index]
        self._mark_as_deleted(sobject)

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

    def get_sobjects(self, sobject_name: str, include_deleted: bool = False):
        """
        Returns the objects currently loaded into the virtual instance
        """
        sobjects = self.data[sobject_name]
        if include_deleted:
            return sobjects
        return [sobject for sobject in sobjects if not sobject["IsDeleted"]]

    def _normalize_relation_via_external_id_field(self, sobject: dict):
        """
        We need to relate an object which was pushed via an external key with a master-detail
        relationship to its related object in the virtual data

        I'm not proud of this method
        """
        normalized = dict()
        for key, value in sobject.items():
            if key.endswith("__r"):
                # We assume there's only one key in this dict
                for external_id_field, external_id in value.items():
                    relational_field_name = self._related_object_name_to_object_name(
                        key
                    )
                    # if the related object name can't be inferred from the field name
                    # check the manually specified mapping
                    if key in self.relations_file:
                        related_object_name = self.relations_file[key]
                    # o/w infer it automatically
                    else:
                        related_object_name = relational_field_name
                    # If this is a standard object, we have to pop-off the __c
                    # A little dirty for sure, especially since we overwrite relational_field_name
                    standard_object_name = related_object_name.replace("__c", "")
                    if (
                        related_object_name not in self.data
                        and standard_object_name in self.data
                    ):
                        related_object_name = standard_object_name
                        relational_field_name = standard_object_name
                    related_object = self.get_by_custom_id(
                        related_object_name, external_id, external_id_field
                    )
                    normalized[relational_field_name] = related_object["Id"]
            # this may be a standard, Salesforce relation, such as "Order": {"OrderId__c": order_id}, on OrderItem
            # BillingAddress is a built-in Salesforce field that comes back from the API as a dictionary
            elif type(value) == dict and key != "BillingAddress":
                # check if we're not using a real sobject name,
                # and instead need to refer to the relations.json file for cases
                # where an sobject name can't be derived from a look up's field name
                if key not in self.data:
                    related_object_name = self.relations_file[key]
                    lookup_field_prefix = key
                else:
                    related_object_name = key
                    lookup_field_prefix = key

                for external_id_field, external_id in value.items():
                    related_object = self.get_by_custom_id(
                        related_object_name, external_id, external_id_field
                    )
                    # and in the above case, the lookup field is OrderId
                    normalized[f"{lookup_field_prefix}Id"] = related_object["Id"]
            else:
                normalized[key] = value
        return normalized

    @staticmethod
    def _related_object_name_to_object_name(related_object_name: str):
        return related_object_name.replace("__r", "__c")

    def _add_system_fields(self, sobject: dict) -> dict:
        current_datetime = datetime.datetime.now().isoformat()
        user_sfdc_id = self._generate_sfdc_id()
        system_fields = {
            "Id": self._generate_sfdc_id(),
            "IsDeleted": False,
            "CreatedById": user_sfdc_id,
            "LastModifiedById": user_sfdc_id,
            "LastModifiedDate": current_datetime,
            "CreatedDate": current_datetime,
            "SystemModstamp": current_datetime,
        }
        return {
            **sobject,
            **system_fields,
        }

    @staticmethod
    def _update_datetime_fields(sobject: dict) -> dict:
        current_datetime = datetime.datetime.now().isoformat()
        return {
            **sobject,
            "SystemModstamp": current_datetime,
            "LastModifiedDate": current_datetime,
        }

    @staticmethod
    def _mark_as_deleted(sobject: dict):
        sobject["IsDeleted"] = True
        sobject["LastModifiedDate"] = datetime.datetime.now().isoformat()

    @staticmethod
    def _generate_sfdc_id():
        return "".join(random.choices(string.ascii_letters + string.digits, k=18))

    def _check_for_salesforce_resource(self, url: str, sobject_name: str):
        if sobject_name not in self.data:
            raise SalesforceResourceNotFound(
                url,
                404,
                sobject_name,
                [
                    {
                        "errorCode": "NOT_FOUND",
                        "message": "The requested resource does not exist",
                    }
                ],
            )


virtual_salesforce = VirtualSalesforce()
