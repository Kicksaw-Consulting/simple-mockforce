from typing import List

from python_soql_parser.core import ASC, DESC


def sort_by_order_by_clause(sobjects: List[dict], order_by_clauses: list):
    sort_keys = list()
    for order in order_by_clauses[0]:
        direction = ASC
        if order[-1] == DESC or order[-1] == ASC:
            direction = order.pop()
        sort_keys.append((order, direction))

    for sort_key in sort_keys:

        def order_records(record):
            sort_tuple = tuple()
            for key in sort_key[0]:
                sort_tuple += tuple(record[key])
            return sort_tuple

        sobjects.sort(key=order_records, reverse=sort_key[1] == DESC)