import functools
import pytest
import tornado.ioloop
from tornado import gen
from tornado import httpclient
from main import *


@pytest.fixture(scope='module')
def tloop():
    return tornado.ioloop.IOLoop.current()


@gen.coroutine
def get_records(_id):
    res = yield Records.get(_id) 
    return res


@gen.coroutine
def create_records(_id, data):
    res = yield Records.create(_id, data) 
    return res


def test_get_client(tloop):
    err, response = tloop.run_sync(functools.partial(get_records, '000000000'))
    assert isinstance(response, Records)


def test_get_client_not_found(tloop):
    err, response = tloop.run_sync(functools.partial(get_records, '999999999'))
    assert isinstance(response, type(None))


def test_create_records(tloop):
    err, response = tloop.run_sync(functools.partial(
        create_records, '888888888', {}
    ))
    assert isinstance(response, Records)
    err, response = tloop.run_sync(functools.partial(
        response.update, {'key': 'value'}
    ))
    assert response.data['key'] == 'value'
    err, response = tloop.run_sync(response.delete)
    assert isinstance(response, dict)


