#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from . import admin
from .. import db
from .forms import CreateUserForm, RenewfeeForm
from ..models import User, Userlog, Package
from flask import render_template, session, redirect, url_for, request
from datetime import datetime
from dateutil.relativedelta import *

@admin.route("/")
def admin_main():
     users = []
     for user in User.query.all():
         traffics = 0
         for log in Userlog.query.filter_by(user_id=user.id).all():
             traffics = traffics + log.traffic
         if traffics > 1024*1024:
             traffics = str(traffics/1024/1024) + "MB"
         elif traffics > 1024:
             traffics = str(traffics/1024) + "KB"
         else:
             pass
         if user.status == 'active':
             if relativedelta(user.expired, datetime.utcnow()).months >= 1:
                 left = ""
             else:
                 left = "({0} days left)".format(relativedelta(user.expired, datetime.utcnow()).days)
             users.append({"id":user.id, "name":user.name, "payday":user.checkout, \
                 "expired":user.expired.strftime("%y-%m-%d"), "left":left, "traffic":traffics})
         else:
             user.append({"id":user.id, "name":user.name, "payday":user.checkout, "expired":"NA", "left":0,"traffic":0})
     return render_template("admin/main.html", users=users)


@admin.route("/renewfee", methods=['GET', 'POST'])
def admin_renewfee_user():
    form = RenewfeeForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None:
            return redirect(url_for("admin.admin_main"))
        if form.renew.data == '1m':
            user.expired = user.expired + relativedelta(months=+1)
        elif form.renew.data == '3m':
            user.expired = user.expired + relativedelta(months=+3)
        elif form.renew.data == '6m':
            user.expired = user.expired + relativedelta(months=+6)
        elif form.renew.data == '1y':
            user.expired = user.expired + relativedelta(years=+1)
        else:
            pass
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("admin.admin_main"))
    else:
        return render_template("admin/renewfee.html", form=form)


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
            checkout = int(datetime.utcnow().day),  package_id = int(form.package.data),
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
    userlog = Userlog(interface=request.form['interface'], status="up",
            start=datetime(start.year, start.month, start.day, start.hour, start.minute, start.second),
            end=datetime(start.year, start.month, start.day, 0, 0, 0), traffic=0, user_id=user.id)
    db.session.add(userlog)
    db.session.commit()
    return "ok", 200


@admin.route("/stopuserlog", methods=['POST'])
def admin_stop_user_log():
    end = datetime.now()
    userlog = Userlog.query.filter_by(interface=request.form["interface"]).filter_by(status='up').first()
    if userlog is None:
        return "ok", 404
    userlog.end =  datetime(end.year, end.month, end.day, end.hour, end.minute, end.second)
    userlog.status = 'down'
    userlog.traffic = int(request.form['traffic'])
    db.session.add(userlog)
    db.session.commit()
    return "ok", 200
