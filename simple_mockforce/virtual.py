# TODO: determine if provisioning should be implicit like it is now, or if it should be explicitly done
import uuid
from simple_mockforce.utils import (
    find_object_and_index,
)


class VirtualSalesforceInstance:
    """
    A global, in-memory store for all the written data when calling with @mock_salesforce

    As of now, all objects are assumed to exist (and provisioned if they don't already).
    This class also does not yet mimic any of the validation you'd see with Salesforce server-side
    """

    def __init__(self):
        # will store {'contact': [{"id": "123456789123456789", # ... }], # ... }
        # this is the mega-dictionary that stores it all
        # self.data = dict()
        self.data = {
            "contact": [{"id": "123", "name": "Bob"}, {"id": "124", "name": "John"}]
        }

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
    def _normalize_data(data: dict):
        return {key.lower(): value for key, value in data.items()}

    def get(self, sobject_name: str, record_id: str):
        sobject_name = sobject_name.lower()
        for sobject in self.data[sobject_name]:
            if sobject["id"] == record_id:
                return sobject
        raise AssertionError(f"Could not find {record_id} in {sobject_name}s")

    def update(self, sobject_name: str, record_id: str, data: dict, upsert_key=None):
        sobject_name = sobject_name.lower()
        data = self._normalize_data(data)
        try:
            original, index = find_object_and_index(
                self.data[sobject_name],
                "id" if not upsert_key else upsert_key,
                record_id,
            )
            self.data[sobject_name][index] = {
                **original,
                **data,
            }
        except KeyError:
            id_ = str(uuid.uuid4())
            data["id"] = id_
            if upsert_key:
                data[upsert_key] = record_id
            self.data[sobject_name].append(data)

    def create(self, sobject_name: str, sobject: dict):
        sobject_name = sobject_name.lower()
        self._provision_sobject(sobject_name)
        self.data[sobject_name].append(sobject)

    def delete(self, sobject_name: str, record_id: str):
        sobject_name = sobject_name.lower()

        index = None
        for idx, object_ in enumerate(self.data[sobject_name]):
            if object_["id"] == record_id:
                index = idx

        self.data[sobject_name].pop(index)


virtual_salesforce = VirtualSalesforceInstance()