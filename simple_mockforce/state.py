class VirtualSalesforceInstance:
    def __init__(self):
        # will store {'Contact': [{"Id": "123456789123456789", # ... }], # ... }
        # self.data = dict()
        self.data = {
            "contact": [{"id": "123", "name": "Bob"}, {"id": "124", "name": "John"}]
        }


virtual_salesforce = VirtualSalesforceInstance()