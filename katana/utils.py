from datetime import date, datetime, timedelta
from inicheck.checkers import CheckType
import dateparser


def parse_date(value):
    if isinstance(value, datetime):
        return value
    elif isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    else:
        converted = dateparser.parse(value, settings={'STRICT_PARSING': True})
        if converted is None:
            raise TypeError("{} is not a date".format(value))

        return converted


def daterange(start_date, end_date, delta=timedelta(hours=1)):
    """Create a `datetime` list between the start and end date
    by a given timedelta.

    Arguments:
        start_date {datetime} -- start date
        end_date {datetime} -- end date

    Keyword Arguments:
        delta {timedelta} -- timedelta for the step (default: {timedelta(hours=1)})

    Returns:
        [list] -- List of `datetime` objects
    """

    dr = []
    while start_date <= end_date:
        dr.append(start_date)
        start_date += delta

    return dr


class CheckRawString(CheckType):
    """
    Custom `inicheck` checker that will not change the input string
    """

    def __init__(self, **kwargs):
        super(CheckRawString, self).__init__(**kwargs)

    def type_func(self, value):
        """
        Do not change the passed value at all

        Args:
            value: A single string 
        Returns:
            value: A single string unchanged
        """

        return value
