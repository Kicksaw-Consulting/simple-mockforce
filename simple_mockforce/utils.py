import re


def parse_detail_url(path: str):
    path_end = re.sub(r"^.*?sobjects/", "", path)
    split_up = path_end.split("/")

    if len(split_up) == 2:
        sobject = split_up[-2]
        record_id = split_up[-1]
        return sobject, None, record_id
    elif len(split_up) == 3:
        sobject = split_up[-3]
        custom_id_field = split_up[-2]
        record_id = split_up[-1]
        return sobject, custom_id_field, record_id
    raise AssertionError(f"Unexpected path format: {path}")


def parse_create_url(url: str):
    split_up = url.split("/")
    sobject = split_up[-2]
    return sobject


def parse_job_batch_url(url: str):
    split_up = url.split("/")
    job_id = split_up[-2]
    return job_id


def parse_batch_detail_url(url: str):
    split_up = url.split("/")
    job_id = split_up[-3]
    batch_id = split_up[-1]
    return job_id, batch_id


def parse_batch_result_url(url: str):
    split_up = url.split("/")
    job_id = split_up[-4]
    batch_id = split_up[-2]
    return job_id, batch_id

def parse_batch_query_result_url(url: str):
    split_up = url.split("/")
    job_id = split_up[-5]
    batch_id = split_up[-3]
    result_set_id = split_up[-1]
    return job_id, batch_id, result_set_id


def find_object_and_index(objects: list, pk_name: str, pk: str):
    index = None
    original = None
    for idx, object_ in enumerate(objects):
        if object_.get(pk_name) == pk:
            index = idx
            original = object_

    return original, index


def terminate_regex(url_pattern):
    """
    Simple terminates the given pattern (which is supplied from constants.py)
    """
    return re.compile(url_pattern + "$")
