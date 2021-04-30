def add_parent_object_attributes(
    sobject: dict, record: dict, parent_fields: list, virtual_salesforce: object
):
    for parent_field in parent_fields:
        parent_sobject_name, parent_field = parent_field.split(".")
        normalized_parent_sobject_name = (
            virtual_salesforce._related_object_name_to_object_name(parent_sobject_name)
        )
        parent_object = virtual_salesforce.get(
            normalized_parent_sobject_name,
            sobject[normalized_parent_sobject_name],
        )
        if parent_sobject_name not in record:
            record[parent_sobject_name] = dict()
        record[parent_sobject_name][parent_field] = parent_object[parent_field]
