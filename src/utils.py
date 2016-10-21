# Module for help

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

    def __init__(self, date):
        pass
    
    @classmethod
    def from_now(cls):
        pass

    @classmethod
    def from_date(cls, date):
        pass

    def check_date(self, date):
        pass

    def check_now(self):
        pass

    @property
    def object(self):
        pass

    @property
    def timestamp(self):
        pass


