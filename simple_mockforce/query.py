from typing import List, Tuple, Union

from python_soql_parser.binops import EQ, NEQ, LT, LTE, GT, GTE
from python_soql_parser.core import AND, OR, IN, NULL


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
    if field not in sobject:
        return False
    field_value = sobject[field]
    if binop == EQ:
        return field_value == value
    elif binop == IN:
        return field_value in value
    elif binop == NEQ:
        return field_value != value
    elif binop == LT:
        return field_value < value
    elif binop == LTE:
        return field_value <= value
    elif binop == GT:
        return field_value > value
    elif binop == GTE:
        return field_value >= value
    else:
        raise AssertionError(f"{binop} not yet handled")


def _needs_another_dive(clause: list):
    return type(clause[0]) != str


def parse_clause(clause: list) -> Union[str, List[str]]:
    field = clause[0]
    binop = clause[1]
    dirty_value = clause[2]
    if type(dirty_value) == list:
        if dirty_value[0] == "(" and dirty_value[-1] == ")":
            values = dirty_value[1:-1]
            value = [clean_string(dirty_value) for value in values]
    else:
        value = clean_string(dirty_value)
    return field, binop, coerce_to_none_if_applicable(value)


def clean_string(value):
    if type(value) == str:
        return value.strip("'")
    return value


def coerce_to_none_if_applicable(value: Union[str, list]):
    if type(value) == list:
        return [x if x != NULL else None for x in value]
    return value if value != NULL else None
