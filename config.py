import os
import psycopg2


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ricchipicchi'