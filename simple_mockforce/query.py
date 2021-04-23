from typing import List, Tuple

from python_soql_parser.binops import EQ
from python_soql_parser.core import AND


def filter_by_where_clause(sobject: dict, where: list) -> bool:
    """
    Return True if the object passes the where clause
    Return False if it should be excluded
    """
    if where:
        results = list()
        _dive_into_clause(sobject, where, results)
        print("results", results)
        passes = not any(not x for x in results)
        print("passes", passes)
        return passes
    return False


def _dive_into_clause(
    sobject: dict, where: list, results: List[bool], previous: list = []
):
    for clause in where:
        is_list = type(clause) == list and len(clause) == 3
        if is_list and _is_not_clause(clause):
            return _dive_into_clause(sobject, clause, results, previous)
        elif is_list:
            field, binop, value = parse_clause(clause)
            passes = evaluate_condition(sobject, field, binop, value)
            if previous:
                print(previous)
                passes = evaluate_boolean_expression(previous, passes)
            results.append(passes)
        else:
            previous_evaluation = results.pop()
            previous.append((previous_evaluation, clause))


def evaluate_boolean_expression(previous: list, current_bool: bool):
    previous_condition: Tuple[bool, str] = previous[0]
    previous_result, boolean_operator = previous_condition
    if boolean_operator == AND:
        passes = current_bool and previous_result
        previous.clear()
    else:
        raise AssertionError(f"{previous_condition[1]} is not yet handled")
    return passes


def evaluate_condition(sobject: dict, field: str, binop: str, value: str):
    if binop == EQ:
        return sobject[field] == value
    else:
        raise AssertionError(f"{binop} not yet handled")


def _is_not_clause(clause: list):
    return any(not isinstance(x, str) for x in clause)


def parse_clause(clause: list):
    field = clause[0]
    binop = clause[1]
    value = clause[2].strip("'")
    return field, binop, value