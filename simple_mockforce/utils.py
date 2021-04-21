def parse_detail_url(url: str):
    split_up = url.split("/")
    # TODO: use pyparsing
    sobject = split_up[-2]
    record_id = split_up[-1]

    return sobject, record_id


def parse_create_url(url: str):
    split_up = url.split("/")
    # TODO: use pyparsing
    sobject = split_up[-2]

    return sobject