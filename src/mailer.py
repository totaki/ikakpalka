# Module for send emails

import os
import smtplib
import tornado.web
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
from tornado import gen
from defines import *
from secrets import *


# Templates keys
K_LOGIN_USER = 'login'


# Templates from keys
TM_TEMPLATES = {
    K_LOGIN_USER: TM_LOGIN_USER, # Send when user login 
}

# Subjects from keys
SUBJECTS = {
    K_LOGIN_USER: 'Данные для входа на икакпалка.рф'
}


def _get_template(file_name):
    with open(os.path.join(TEMPLATE_PATH, EMAIL_TEMPLATE_PATH, file_name)) as f:
        return f.read()


def _load_all_templates():
    templates = {}
    for k, v in TM_TEMPLATES.items():
        templates[k] = _get_template(v)
    return templates


class Mailer():

    _templates = _load_all_templates()
    _smtp = EMAIL_HOST
    _port = EMAIL_PORT
    _user = EMAIL_USER
    _password = EMAIL_PASSWORD
    _sender =formataddr((str(Header(EMAIL_SENDER, 'utf-8')), _user)) 
   
    @classmethod
    def _render(cls, template, **kwargs):
        return cls._templates[template].format(**kwargs)

    @classmethod
    def send(cls, to, template, **kwargs):
        text = cls._render(template, **kwargs)
        msg = MIMEText(text)
        msg['Subject'] = SUBJECTS[template]
        msg['From'] = cls._sender
        msg['To'] = to 
        s = smtplib.SMTP_SSL(cls._smtp, cls._port)
        s.login(cls._user, cls._password)
        s.send_message(msg)
        s.quit()


class SendMailHandler(tornado.web.RequestHandler):

    _query_args = ['to', 'template', 'link']

    def _get_args(self):
        return {
            i:self.get_query_argument(i, default=None) for i in
            self._query_args
        }
    
    @gen.coroutine
    def get(self):
        Mailer.send(**self._get_args())
        self.write(STR)


if __name__ == "__main__":
    application = tornado.web.Application([
        (r'/send', SendMailHandler),

    ], debug=DEBUG_MODE)
    application.listen(NODE_PORT)
    tornado.ioloop.IOLoop.current().start()

