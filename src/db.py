# Module for using CouchDB

import json
import uuid
from tornado import httpclient
from tornado import gen
from defines import *
from utils import *
from secrets import *


class Document:
    
    _headers = {'Content-Type': 'application/json'} 
    _key_id = '_id'
    _key_rev = '_rev'
    _cls_path = None

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return self._data[self._key_id]
    
    @property
    def rev(self):
        return self._data[self._key_rev]
 
    @property
    def data(self):
        return self._data
 
    @classmethod
    def get_path(cls, _id):
        return cls._cls_path + str(_id)

    @classmethod
    def get_path_with_rev(cls, _id, rev):
        return cls._cls_path + str(_id) + '?rev=' + str(rev)
 
    @classmethod
    @gen.coroutine
    def _send_request(cls, *args, **kwargs):
        err, ok = (None, None)
        try:
            response = yield httpclient.AsyncHTTPClient().fetch(
                *args, **kwargs
            )
            ok = cls._from_json(response.body)
        except httpclient.HTTPError as e:
            err = e.code
        raise gen.Return((err, ok))

    @staticmethod
    def _to_json(string):
        return json.dumps(string).encode(CODE)

    @staticmethod
    def _from_json(body):
        return json.loads(body.decode(CODE))

    @classmethod
    @gen.coroutine
    def create(cls, _id, data):
        obj = None
        body = cls._to_json(data)
        path = cls.get_path(_id)
        err, ok = yield cls._send_request(
            path, method='PUT', headers=cls._headers, body=body
        )
        if not err:
            err, ok = yield cls.get(_id)
        if not err:
            obj = ok
        return (err, obj)

    @gen.coroutine
    def delete(self):
        dct = None
        path = self.get_path_with_rev(self.id, self.rev)
        err, ok = yield self._send_request(path, method='DELETE')
        if not err:
            del self._data[self._key_rev]
            dct = self.data
        return (err, dct)

    @classmethod
    @gen.coroutine
    def get(cls, _id):
        obj = None
        path = cls.get_path(_id)
        err, ok = yield cls._send_request(path)
        if not err:
            obj = cls(ok)
        return (err, obj)

    @gen.coroutine
    def update(self, data):
        _id = self.id
        data[self._key_rev] = self.rev
        return (yield self.create(_id, data))


class CleanUsers(Document):
    
    _cls_path = DB_USERS
    _key_rec = 'records'

    @property
    def record(self):
        return self._data[self._key_rec]


class CleanRecords(Document):
    
    _cls_path = DB_RECORDS


class ClearSessions(Document):

    _cls_path = DB_SESSIONS


class Users(CleanUsers):

    pass 


class Records(CleanRecords):

    pass 


class Sessions(ClearSessions):

    _key_rec = 'records'

    @property
    def record(self):
        return self._data[self._key_rec]

    def get_create_link(self):
        return '{}/login?session={}&record={}'.format(BASE_URL,
            self.id, self.record
        ) 

    @classmethod
    @gen.coroutine
    def create(cls, record):
        rec = ID(record)
        id_ = uuid.uuid4().hex 
        dt_ = utils.ExpiresDate.fron_now(SESSION_SECOND)
        result = yield super().create(id_, **dict(
            record=rec.str,
            dt=dt_
        ))
        raise gen.Return(result)

