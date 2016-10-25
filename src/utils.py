# Module for help

import datetime as DT
from defines import *


class ID():
    
    def __init__(self, number):
        if isinstance(number, str):
            number = STR.join(number.split(QUERY_SPLITER))
        try:
            self._number = int(number)
        except ValueError:
            self._number = None

    
    def _get_number(self, func):
        if self._number != None:
            return func(self._number)
    
    @staticmethod
    def _to_str(n):
        return '0' * (LEN_ID - len(str(n))) + str(n)
    
    @property
    def int(self):
        return self._get_number(int)

    @property
    def str(self):
        return self._get_number(self._to_str)


class ExpiresDate():

    def __init__(self, date, delta_seconds=None):
        if isinstance(date, DT.datetime):
            _date = date
        elif isinstance(date, str) or isinstance(date, float):
            _date = DT.datetime.fromtimestamp(float(date))
        else:
            raise TypeError('Date must be datetime.datetime or str instance')

        if delta_seconds == None:
            self._expires_date = _date
        else:
            self._expires_date = (_date + DT.timedelta(seconds=delta_seconds))
    
    @classmethod
    def from_now(cls, delta_seconds=None):
        return cls(DT.datetime.utcnow(), delta_seconds)

    def check_date(self, date):
        return not ((self._expires_date - date).days < 0)

    def check_now(self):
        return self.check_date(DT.datetime.utcnow())

    @property
    def timestamp(self):
       return self._expires_date.timestamp() 

    @property
    def dt(self):
       return self._expires_date 

