from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class ProdConfig():
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = environ.get('SECRET_KEY')


class DevConfig():
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'dev'