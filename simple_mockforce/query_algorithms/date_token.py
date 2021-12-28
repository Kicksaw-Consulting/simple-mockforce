import datetime


class SalesforceDateToken:
    MONTH = "MONTH"

    def __init__(self, date: datetime.date, truncate_point: str) -> None:
        self.date_token_date = date
        self.truncate_point = truncate_point

    def truncate_date(self, date_to_compare: datetime.date):
        if self.truncate_point == SalesforceDateToken.MONTH:
            return datetime.date(
                year=date_to_compare.year, month=date_to_compare.month, day=1
            )
        raise AssertionError(f"{self.truncate_point} not yet supported")
