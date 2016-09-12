#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from . import admin
from .. import db
from .forms import CreateUserForm
from ..models import User, Userlog, Package
from flask import render_template, session, redirect, url_for, request
from datetime import datetime
from dateutil.relativedelta import *

@admin.route("/")
def admin_main():
     return render_template("admin/main.html")


@admin.route("/createuser", methods=['GET', 'POST'])
def admin_create_user():
    form = CreateUserForm()
    packages=[]
    for package in Package.query.all():
        packages.append((str(package.id), package.name))
    form.package.choices = packages

    if form.validate_on_submit():
        expired = datetime.now()
        if form.expired.data == '3d':
            expired = expired + relativedelta(days=+3)
        elif form.expired.data == '1m':
            expired = expired + relativedelta(months=+1)
        elif form.expired.data == '3m':
            expired = expired + relativedelta(months=+3)
        elif form.expired.data == '6m':
            expired = expired + relativedelta(months=+6)
        elif form.expired.data == '1y':
            expired = expired + relativedelta(years=+1)
        else:
            pass
        user = User(name=form.name.data, password = form.password.data,
            checkout = int(form.checkout.data),  package_id = int(form.package.data),
            expired = datetime(expired.year, expired.month, expired.day, 0, 0, 0), status="active")
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("admin.admin_main"))
    else:
        return render_template("admin/create_user.html", form=form)


@admin.route("/startuserlog", methods=['POST'])
def admin_start_user_log():
    start = datetime.now()
    user = User.query.filter_by(name=request.form['user']).first()
    if user is None:
        return "ok", 404
    userlog = Userlog(interface=request.form['interface'], outip=request.form['outip'], status="up",
            start=datetime(start.year, start.month, start.day, start.hour, start.minute, start.second),
            end=datetime(start.year, start.month, start.day, 0, 0, 0), traffic=0, user_id=user.id)
    db.session.add(userlog)
    db.session.commit()
    return "ok", 200

@admin.route("/stopuserlog", methods=['POST'])
def admin_stop_user_log():
    end = datetime.now()
    user = User.query.filter_by(name=request.form['user']).first()
    userlog = Userlog.query.filter_by(user_id=user.id).filter_by(interface=request.form["interface"]).filter_by(status='up').first()
    if user is None or userlog is None:
        return "ok", 404
    userlog.end =  datetime(end.year, end.month, end.day, end.hour, end.minute, end.second)
    userlog.status = 'down'
    userlog.traffic = 102400
    db.session.add(userlog)
    db.session.commit()
    return "ok", 200
