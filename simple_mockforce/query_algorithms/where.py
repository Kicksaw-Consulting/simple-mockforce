import datetime

# explicity import this so we can monkeypatch it in the tests
from datetime import date
from typing import List, Tuple, Union

from dateutil.relativedelta import relativedelta

from python_soql_parser.binops import EQ, NEQ, LT, LTE, GT, GTE
from python_soql_parser.core import AND, OR, IN, NULL, TRUE, FALSE
from python_soql_parser.tokens import (
    TODAY,
    TOMORROW,
    YESTERDAY,
    THIS_MONTH,
    NEXT_MONTH,
    LAST_MONTH,
)

from simple_mockforce.query_algorithms.date_token import SalesforceDateToken


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
    return True


def _dive_into_clause(
    sobject: dict, where: list, results: List[bool], previous: list = []
):
    for clause in where:
        is_list = type(clause) == list
        if is_list and _needs_another_dive(clause):
            _dive_into_clause(sobject, clause, results, previous)
        elif is_list:
            field, binop, value = _parse_clause(clause)
            passes = _evaluate_condition(sobject, field, binop, value)
            if previous:
                passes = _evaluate_boolean_expression(previous, passes)
            results.append(passes)
        else:
            previous_evaluation = results.pop()
            previous.append((previous_evaluation, clause))


def _evaluate_boolean_expression(previous: list, current_bool: bool):
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
    # TODO: just use a class; would be cleaner to track state in an instance rather than this
    previous.clear()
    return passes


def parse_date(value: str):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def parse_date_token(value):
    if isinstance(value, SalesforceDateToken):
        return value
    return None


def _evaluate_condition(
    sobject: dict, field: str, binop: str, value: Union[str, List[str]]
):
    if field not in sobject:
        return False
    field_value = sobject[field]

    date_value = parse_date(field_value)
    date_token = parse_date_token(value)
    if date_value and not date_token:
        field_value = date_value
    elif date_value and date_token:
        field_value = date_token.truncate_date(date_value)
        value = date_token.date_token_date
    # if our value isn't a date, but we have a date token, time to leave
    elif date_token:
        return False

    # check if we're comparing None to a date
    if not field_value and isinstance(value, datetime.date):
        return False

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


def _parse_clause(clause: list) -> Union[str, List[str]]:
    field = clause[0]
    binop = clause[1]
    dirty_value = clause[2]
    if type(dirty_value) == list:
        if dirty_value[0] == "(" and dirty_value[-1] == ")":
            values = dirty_value[1:-1]
            value = [_clean_string(dirty_value) for value in values]
    else:
        value = _clean_string(dirty_value)
    return field, binop, _to_python(value)


def _clean_string(value):
    if type(value) == str:
        return value.strip("'")
    return value


def _to_python(value: Union[str, list]):
    if type(value) == list:
        return [x if x != NULL else None for x in value]
    if value == TRUE:
        return True
    elif value == FALSE:
        return False
    elif value == NULL:
        return None
    elif value == YESTERDAY:
        return date.today() - datetime.timedelta(days=1)
    elif value == TODAY:
        return date.today()
    elif value == TOMORROW:
        return date.today() + datetime.timedelta(days=1)
    elif value == THIS_MONTH:
        today = date.today()
        return SalesforceDateToken(
            date(today.year, month=today.month, day=1), SalesforceDateToken.MONTH
        )
    elif value == NEXT_MONTH:
        day_next_month = date.today() + relativedelta(months=1)
        return SalesforceDateToken(
            date(day_next_month.year, month=day_next_month.month, day=1),
            SalesforceDateToken.MONTH,
        )
    elif value == LAST_MONTH:
        day_last_month = date.today() - relativedelta(months=1)
        return SalesforceDateToken(
            date(day_last_month.year, month=day_last_month.month, day=1),
            SalesforceDateToken.MONTH,
        )
    return value
