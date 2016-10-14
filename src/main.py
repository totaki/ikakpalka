import json
import re
import smtplib
import tornado.ioloop
import tornado.web
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
QUERY = '_id'
ID_REGEX = r'\d{9}'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465


@gen.coroutine    
def _get_users(email):
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


def _send_email(email, text):
    msg = MIMEText(text)
    msg['Subject'] = 'Test'
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


class MainHandler(BaseHandler):

    def get(self):
        self.render('main.html')


class SearchHandler(BaseHandler):

    def _validate_query(self):
        _id = ''.join(str(self._id).split('-'))
        if not (str(_id).isdigit() and len(_id) == 9):
            _id = None
        return _id

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
                            response=self._prepare_json(response)
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


class ChangeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class LoginHandler(tornado.web.RequestHandler):

    @gen.coroutine    
    def get(self):
        self.write("Hello, world")

    @gen.coroutine    
    def post(self):
        email = self.get_body_argument('email', default=None) 
        _send_email('totaki@mail.ru', 'Some text')        
        self.write("Hello, world")


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/search", SearchHandler),
        (r"/registration", RegistrationHandler),
        (r"/change", ChangeHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static/"}),

    ], debug=False, template_path='./templates/')
    application.listen(10000)
    tornado.ioloop.IOLoop.current().start()

