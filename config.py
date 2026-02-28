import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///:memory:'
