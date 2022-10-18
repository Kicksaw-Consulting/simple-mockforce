def add_parent_object_attributes(
    sobject: dict, record: dict, parent_fields: list, virtual_salesforce: object
):
    for parent_field in parent_fields:
        parent_sobject_name, parent_field = parent_field.split(".")

        is_custom_lookup_to_standard_object = parent_sobject_name in virtual_salesforce.relations_file

        normalized_parent_sobject_name = (
            virtual_salesforce._related_object_name_to_object_name(parent_sobject_name)
            if not is_custom_lookup_to_standard_object
            else virtual_salesforce.relations_file[parent_sobject_name]
        )
        # for some standard lookup fields, we need to append 'Id'
        lookup_field_name = (
            normalized_parent_sobject_name
            if normalized_parent_sobject_name in sobject
            else f"{normalized_parent_sobject_name}Id"
        )

        if is_custom_lookup_to_standard_object:
            lookup_field_name = virtual_salesforce._related_object_name_to_object_name(parent_sobject_name)

        parent_object = virtual_salesforce.get(
            normalized_parent_sobject_name,
            sobject[lookup_field_name],
        )
        if parent_sobject_name not in record:
            record[parent_sobject_name] = dict()
        record[parent_sobject_name][parent_field] = parent_object[parent_field]
