#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from . import db
from datetime import datetime


class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    traffic = db.Column(db.Integer)
    maxshare = db.Column(db.Integer)
    users = db.relationship('User', backref='packages', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    password = db.Column(db.String(8))
    expired = db.Column(db.DateTime)
    payday = db.Column(db.Integer)
    status = db.Column(db.String(8))
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"))
    traffics = db.relationship('Usertraffic', backref='users', lazy='dynamic')
    logs = db.relationship('Userlog', backref='users', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class Usertraffic(db.Model):
    __tablename__ = 'usertraffics'
    id = db.Column(db.Integer, primary_key=True)
    package_traffic = db.Column(db.Integer, default=0)
    last_traffic = db.Column(db.Integer, default=0)
    consume_traffic = db.Column(db.Integer, default=0)
    period = db.Column(db.String(32))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return '<Role> %r' % self.period


class Userlog(db.Model):
    __tablename__ = 'userlogs'
    id = db.Column(db.Integer, primary_key=True)
    interface = db.Column(db.String(8), index=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    status = db.Column(db.String(8))
    traffic = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return "<Role %r>" % self.name
