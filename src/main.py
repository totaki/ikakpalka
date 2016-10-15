import datetime
import json
import re
import smtplib
import tornado.ioloop
import tornado.web
import uuid
from email.mime.text import MIMEText
from secrets import *
from tornado import gen
from tornado import httpclient


RECORDS_TYPES = [
    'email',
    'url',
    'facebook',
    'vk'
]


DB_BASE_URL = 'http://local.ikp:5984/'
DB_RECORDS = DB_BASE_URL + 'ikp_records/'
DB_USERS = DB_BASE_URL + 'ikp_users/'
DB_SESSIONS = DB_BASE_URL + 'ikp_sessions/'
QUERY = '_id'
ID_REGEX = r'\d{9}'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465


def _closed_date(dt):
    return (dt + datetime.timedelta(seconds=600)).timestamp()


@gen.coroutine    
def _get_user(email):
    try:
        response = yield httpclient.AsyncHTTPClient().fetch(
            DB_USERS + str(email)
        )
    except httpclient.HTTPError as err:
        if err.code == 404:
            response = None
        else:
            response = False
    raise gen.Return(response)


@gen.coroutine 
def _change_record(record, dct):
    try:
        response = yield httpclient.AsyncHTTPClient().fetch(
            DB_RECORDS + str(record), method='PUT', 
            headers={'Content-Type': 'application/json'},
            body=json.dumps(dct).encode('utf-8')
        )
    except httpclient.HTTPError as err:
        if err.code == 404:
            response = None
        else:
            response = False
    raise gen.Return(response)


@gen.coroutine 
def _create_session(record, dt, session=None):
    try:
        if not session:
            session = uuid.uuid4().hex
        response = yield httpclient.AsyncHTTPClient().fetch(
            DB_SESSIONS + session, method='PUT', 
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'record': record, 'date': dt}).encode('utf-8')
        )
        response = session
    except httpclient.HTTPError as err:
        if err.code == 404:
            response = None
        else:
            response = False
    raise gen.Return(response)


@gen.coroutine 
def _delete_session(session, rev):
    raise gen.Return(True)


@gen.coroutine 
def _get_session(session):
    try:
        response = yield httpclient.AsyncHTTPClient().fetch(
            DB_SESSIONS + session 
        )
    except httpclient.HTTPError as err:
        if err.code == 404:
            response = None
        else:
            response = False
    raise gen.Return(response)


@gen.coroutine 
def _check_session(data, session, record):
    response = None
    dct = json.loads(data.body.decode('utf-8'))
    if dct['_id'] == session and dct['record'] == record:
        cur_dt = datetime.datetime.utcnow()
        s_dt = datetime.datetime.fromtimestamp(float(dct['date']))
        if (s_dt - cur_dt).days < 0:
            (yield _delete_session(dct['_id'], dct['_rev']))
        else:
            response = (session, record)
    raise gen.Return(response)
            

@gen.coroutine 
def _check_auth(session, record):
    data = yield _get_session(session)
    if data:
        check = yield _check_session(data, session, record)
        if check:
            return check


def _send_email(email, subject, text):
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = email
    s = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
    s.login(EMAIL_USER, EMAIL_PASSWORD)
    s.send_message(msg)
    s.quit()


class BaseHandler(tornado.web.RequestHandler):

    @property
    def _id(self):
        return self.get_query_argument(QUERY, default=None)
        
    def render_error(self, status, text):
        self.render('error.html', status=status, text=text)

    @gen.coroutine    
    def _get_records(self, _id):
        try:
            response = yield httpclient.AsyncHTTPClient().fetch(DB_RECORDS + str(_id))
        except httpclient.HTTPError as err:
            if err.code == 404:
                response = None
            else:
                response = False
        raise gen.Return(response)


class MainHandler(BaseHandler):

    def get(self):
        self.render('main.html')


class SearchHandler(BaseHandler):

    def _validate_query(self):
        _id = ''.join(str(self._id).split('-'))
        if not (str(_id).isdigit() and len(_id) == 9):
            _id = None
        return _id

    def _prepare_json(self, response):
        if response:
            ok = json.loads(response.body.decode('utf-8'))
            del ok['_id']; del ok['_rev']
        else:
            ok = response
        return ok

    @gen.coroutine    
    def get(self):
        err = (500, 'Server error')
        _id = self._validate_query() 
        if _id:
            response = yield self._get_records(_id)
            if response != False:
                self.render('search.html', _id=_id, 
                            response=self._prepare_json(response),
                )
                err = None
        else:
            err = (400, 'Bad request')

        if err:
            self.render_error(*err)        


class RegistrationHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("Hello, world")

    @gen.coroutine    
    def post(self):
        self.write("Hello, world")


class ChangeHandler(BaseHandler):
    
    @gen.coroutine    
    def get_user(self):
        user = None
        if self.request.method == 'GET':
            get_func = self.get_query_argument 
        elif self.request.method == 'POST':
            get_func = self.get_body_argument
        else:
            get_func = None
        if get_func:
            session, record = (
                get_func('_session', None),
                get_func('_record', None)
            )
            if session and record:
                user = yield _check_auth(session, record)
        raise gen.Return(user)

    @gen.coroutine    
    def get(self):
        user = yield self.get_user() 
        if user: 
            response = yield self._get_records(user[1])
            dct = json.loads(response.body.decode('utf-8'))
            self.render('change.html', session=user[0], record=user[1],
                        records=dct, types=RECORDS_TYPES
                        )
        else:
            self.write("Invalid login")
            

    @gen.coroutine    
    def post(self):
        user = yield self.get_user() 
        if user: 
            dct = dict((i, self.get_body_arguments(i)) for i in RECORDS_TYPES)
            response = yield self._get_records(user[1])
            rec = json.loads(response.body.decode('utf-8'))
            dct['_rev'] = rec['_rev']
            (yield _change_record(user[1], dct))
            self.redirect(BASE_URL + '/search?_id=' + str(user[1]))
        else:
            self.write("Invalid login")


class LoginHandler(BaseHandler):

    _page_text = 'На ваш почтовый ящик отправленна ссылка для входа' 
    _nouser_text = 'Пользователь с таким email не найден' 
    _subject = 'Данные для входа на икакпалка.рф'

    def _get_login_text(self, session, record):
        link = '{}/change?_session={}&_record={}'.format(
            BASE_URL, session, record
        )
        text = 'Вам выслана ссылка которая по который вы можете внести \
изменения в течении 5 минут с момента получения\n\n{}\n\nКоманда \
икакпалка.рф'.format(link)
        return text

    @gen.coroutine    
    def post(self):
        err = (400, 'Bad request')
        text = self._nouser_text
        email = self.get_body_argument('email', default=None)
        if email:
            user = yield _get_user(email)
            if user:
                user_data = json.loads(user.body.decode('utf-8'))
                dt = _closed_date(datetime.datetime.utcnow())
                session = yield _create_session(user_data['record'], dt)
                if session:
                    _send_email(
                        user_data['_id'], self._subject, 
                        self._get_login_text(session, user_data['record'])
                    )
                    text = self._page_text
            self.render('account.html', text=text)
        else:
            self.render_error(*err)



if __name__ == "__main__":
    application = tornado.web.Application([
        (r'/', MainHandler),
        (r'/search', SearchHandler),
        (r'/registration', RegistrationHandler),
        (r'/change', ChangeHandler),
        (r'/login', LoginHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': './static/'}),

    ], debug=True, template_path='./templates/')
    application.listen(10000)
    tornado.ioloop.IOLoop.current().start()

