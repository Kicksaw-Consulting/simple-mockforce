# TODO: determine if provisioning should be implicit like it is now, or if it should be explicitly done


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

    def create(self, sobject_name: str, sobject: dict):
        sobject_name = sobject_name.lower()
        self._provision_sobject(sobject_name)
        self.data[sobject_name].append(sobject)


virtual_salesforce = VirtualSalesforceInstance()