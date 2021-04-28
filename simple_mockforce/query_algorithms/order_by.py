from typing import List

from python_soql_parser.core import ASC, DESC


class Sortable:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return other.value == self.value

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self) -> str:
        return str(self.value)


class ReverseSortable(Sortable):
    def __lt__(self, other):
        # This is backwards from the parent class
        return other.value < self.value

    def __repr__(self) -> str:
        # add a - to denote reverse (negative) sorting
        return f"-{self.value}"


def sort_by_order_by_clause(sobjects: List[dict], order_by_clauses: list):
    sort_keys = list()
    for order in order_by_clauses[0]:
        direction = ASC
        if order[-1] == DESC or order[-1] == ASC:
            direction = order.pop()
        sort_keys.append((order, direction))

    def order_records(record):
        sort_tuple = tuple()
        for sort_key in sort_keys:
            for key in sort_key[0]:
                SortableClass = ReverseSortable if sort_key[1] == DESC else Sortable
                sortable_value = SortableClass(record[key])
                sort_tuple += (sortable_value,)
        return sort_tuple

    sobjects.sort(key=order_records)