# Defines vars for application

# Common
CODE = 'utf-8'
LEN_ID = 9 
STR = ''
QUERY_SPLITER = ' '


# Database
DB_BASE_URL = 'http://local.ikp:5984/'
DB_RECORDS = DB_BASE_URL + 'ikp_records/'
DB_REGISTRATIONS = DB_BASE_URL + 'ikp_registrations/'
DB_SESSIONS = DB_BASE_URL + 'ikp_sessions/'
DB_USERS = DB_BASE_URL + 'ikp_users/'


# Mailer
SENDER_PATH = '/send'


# Templates
TEMPLATE_PATH = './templates/'
T_400 = '400.html'
T_404 = '404.html'


# Email templates
EMAIL_SENDER = 'Команда ИКАКПАЛКА.РФ'
EMAIL_TEMPLATE_PATH = 'email'
TM_LOGIN_USER = 'login_user.txt'
