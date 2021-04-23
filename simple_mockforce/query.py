# TODO: import tokens
from python_soql_parser.binops import EQ


def filter_by_where_clause(sobject: dict, where: list) -> bool:
    """
    Return True if the object passes the where clause
    Return False if it should be excluded
    """
    if where:
        return _dive_into_clause(sobject, where)
    return False


def _dive_into_clause(sobject: dict, where: list):
    for clause in where:
        is_list = type(clause) == list and len(clause) == 3
        if is_list and _is_not_clause(clause):
            return _dive_into_clause(sobject, clause)
        elif is_list:
            print(clause)
            field, binop, value = parse_clause(clause)
            passes = evaluate_condition(sobject, field, binop, value)
            print(passes)
            return passes
        else:
            print(clause)


def parse_clause(clause: list):
    field = clause[0]
    binop = clause[1]
    value = clause[2].strip("'")
    return field, binop, value


def evaluate_condition(sobject: dict, field: str, binop: str, value: str):
    if binop == EQ:
        return sobject[field] == value
    else:
        raise AssertionError(f"{binop} not yet handled")


def _is_not_clause(clause: list):
    return any(not isinstance(x, str) for x in clause)