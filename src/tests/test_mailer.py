
import functools
import pytest
import tornado.ioloop
from main import *


@pytest.fixture(scope='module')
def tloop():
    return tornado.ioloop.IOLoop.current()


def test_send_login(tloop):
    response = tloop.run_sync(functools.partial(
        LoginHandler.send_email,
        'totaki@mail.ru',
        'some @ link'
    ))
