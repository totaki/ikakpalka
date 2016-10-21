import os
from defines import *


TM_TEMPLATES = {
    0: TM_LOGIN_USER, # Send when user login 
}


def _get_template(file_name):
    with open(os.path.join(TEMPLATE_PATH, EMAIL_TEMPLATE_PATH, file_name)) as f:
        return f.read()

