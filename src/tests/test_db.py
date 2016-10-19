import pytest
import tornado.ioloop
from tornado import gen
from tornado import httpclient
from main import *

@pytest.fixture(scope='module')
def tloop():
    return tornado.ioloop.IOLoop.current()


@gen.coroutine
def get_records():
    res = yield Records.get('000000000') 
    return res


def test_get_client(tloop):
    err, response = tloop.run_sync(get_records)
    assert isinstance(response, dict)
