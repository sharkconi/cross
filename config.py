#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'iwalk4u+6'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI=os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductConfig(Config):
    PRODUCT = True
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
        'postgresql://infrasim:initial@10.32.136.19/infrasim'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductConfig,
    'default': DevelopmentConfig
}
