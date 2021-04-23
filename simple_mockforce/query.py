from typing import List, Tuple, Union

from python_soql_parser.binops import EQ, NEQ
from python_soql_parser.core import AND, OR, IN


def filter_by_where_clause(sobject: dict, where: list) -> bool:
    """
    Return True if the object passes the where clause
    Return False if it should be excluded
    """
    if where:
        results = list()
        _dive_into_clause(sobject, where, results)
        passes = not any(not x for x in results)
        return passes
    return False


def _dive_into_clause(
    sobject: dict, where: list, results: List[bool], previous: list = []
):
    for clause in where:
        is_list = type(clause) == list and len(clause) == 3
        if is_list and _needs_another_dive(clause):
            return _dive_into_clause(sobject, clause, results, previous)
        elif is_list:
            field, binop, value = parse_clause(clause)
            passes = evaluate_condition(sobject, field, binop, value)
            if previous:
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
    elif boolean_operator == OR:
        passes = current_bool or previous_result
    # elif boolean_operator == IN:
    #     passes =
    else:
        raise AssertionError(f"{previous_condition[1]} is not yet handled")
    # previous is a pass by reference hack to allow us to keep track of
    # whether or not we need to account for a boolean in the where condition
    # Clear the data stored in the reference once it's been accounted for
    previous.clear()
    return passes


def evaluate_condition(
    sobject: dict, field: str, binop: str, value: Union[str, List[str]]
):
    field_value = sobject[field]
    if binop == EQ:
        return field_value == value
    elif binop == IN:
        return field_value in value
    elif binop == NEQ:
        return field_value != value
    else:
        raise AssertionError(f"{binop} not yet handled")


def _needs_another_dive(clause: list):
    # return any(not isinstance(x, str) for x in clause)
    return type(clause[0]) != str


def parse_clause(clause: list) -> Union[str, List[str]]:
    field = clause[0]
    binop = clause[1]
    dirty_value = clause[2]
    if type(dirty_value) == list:
        if dirty_value[0] == "(" and dirty_value[-1] == ")":
            values = dirty_value[1:-1]
            value = [value.strip("'") for value in values]
    else:
        value = dirty_value.strip("'")
    return field, binop, value