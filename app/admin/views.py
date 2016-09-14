#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from . import admin
from .. import db
from .forms import CreateUserForm, DeactiveUserForm, ActiveUserForm
from .forms import RenewfeeForm, RenewPackageForm, RenewTrafficForm
from ..models import User, Userlog, Package, Usertraffic
from flask import render_template, session, redirect, url_for, request
from datetime import datetime
from dateutil.relativedelta import *


def get_period(payday):
    d = datetime.utcnow()
    if d.day < payday:
        d = d + relativedelta(months=-1)
        return datetime(d.year, d.month, payday, 0, 0, 0).strftime("%y-%m-%d")
    else:
        return datetime(d.year, d.month, payday, 0, 0, 0).strftime("%y-%m-%d")


@admin.route("/")
def admin_main():
     users = []
     for user in User.query.all():
         package = Package.query.filter_by(id=user.package_id).first()

         if user.status == 'active':
             if relativedelta(user.expired, datetime.utcnow()).months >= 1:
                 left = ""
             else:
                 left = "({0} days left)".format(relativedelta(user.expired, datetime.utcnow()).days)
             users.append({"id":user.id, "name":user.name, "payday":user.payday, "package":package.name, "package_traffic":package.traffic, \
                 "expired":user.expired.strftime("%y-%m-%d"), "left":left, "status":user.status})
         else:
             users.append({"id":user.id, "name":user.name, "payday":user.payday, "package_traffic":package.traffic, \
                 "package":package.name, "expired":user.expired.strftime("%y-%m-%d"), "left":"","status":user.status})
     return render_template("admin/main.html", users=users)


@admin.route("/renewfee", methods=['GET', 'POST'])
def admin_renewfee_user():
    form = RenewfeeForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None:
            return redirect(url_for("admin.admin_main"))
        periods = 1
        expired = None
        if form.renew.data == '1m':
            expired = user.expired + relativedelta(months=+1)
        elif form.renew.data == '3m':
            expired = user.expired + relativedelta(months=+3)
            periods = 3
        elif form.renew.data == '6m':
            expired = user.expired + relativedelta(months=+6)
            periods = 6
        elif form.renew.data == '1y':
            expired = user.expired + relativedelta(years=+1)
            periods = 12
        else:
            pass
        package = Package.query.filter_by(id = user.package_id).first()
        for p in range(0, periods):
            period = (user.expired + relativedelta(months=+p)).strftime("%y-%m-%d")
            usertraffic = Usertraffic(package_traffic=package.traffic, period=period, user_id=user.id)
            db.session.add(usertraffic)
            db.session.commit()

        user.expired = expired
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("admin.admin_main"))
    else:
        return render_template("admin/renewfee.html", form=form)


@admin.route("/renewtraffic", methods=['GET', 'POST'])
def admin_renewtraffic_user():
    form = RenewTrafficForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name = form.name.data).first()
        if user is None:
            return "ok", 404
        usertraffic = Usertraffic.query.filter_by(user_id=user.id).filter_by(period=get_period(user.payday)).first()
        if usertraffic is None:
            return "ok", 404
        usertraffic.package_traffic = usertraffic.package_traffic + int(form.traffic.data)
        db.session.add(usertraffic)
        db.session.commit()
        return redirect(url_for("admin.admin_main"))
    else:
        return render_template("admin/renewtraffic.html", form=form)


@admin.route("/createuser", methods=['GET', 'POST'])
def admin_create_user():
    form = CreateUserForm()
    packages=[]
    for package in Package.query.all():
        packages.append((str(package.id), package.name))
    form.package.choices = packages

    if form.validate_on_submit():
        expired = datetime.now()
        periods = 1
        if form.expired.data == '3d':
            expired = expired + relativedelta(days=+3)
        elif form.expired.data == '1m':
            expired = expired + relativedelta(months=+1)
        elif form.expired.data == '3m':
            expired = expired + relativedelta(months=+3)
            periods = 3
        elif form.expired.data == '6m':
            expired = expired + relativedelta(months=+6)
            periods = 6
        elif form.expired.data == '1y':
            expired = expired + relativedelta(years=+1)
            periods = 12
        else:
            pass
        user = User(name=form.name.data, password = form.password.data,
             payday = int(datetime.utcnow().day),  package_id = int(form.package.data),
            expired = datetime(expired.year, expired.month, expired.day, 0, 0, 0), status="active")
        db.session.add(user)
        db.session.commit()
        package = Package.query.filter_by(id = form.package.data).first()
        for p in range(0, periods):
            period = (datetime.now() + relativedelta(months=+p)).strftime("%y-%m-%d")
            usertraffic = Usertraffic(package_traffic=package.traffic, period=period, user_id=user.id)
            db.session.add(usertraffic)
            db.session.commit()
        return redirect(url_for("admin.admin_main"))
    else:
        return render_template("admin/create_user.html", form=form)


@admin.route("/deactiveuser", methods=['GET', 'POST'])
def admin_deactive_user():
    form = DeactiveUserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None:
            return "ok", 404
        for usertraffic in user.traffics.all():
            db.session.delete(usertraffic)
            db.session.commit()
        user.status = "inactive"
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("admin.admin_main"))
    else:
        return render_template("admin/deactive_user.html", form=form)


@admin.route("/activeuser", methods=['POST', 'GET'])
def admin_active_user():
    form = ActiveUserForm()
    packages=[]
    for package in Package.query.all():
        packages.append((str(package.id), package.name))
    form.package.choices = packages

    if form.validate_on_submit():
        expired = datetime.now()
        periods = 1
        if form.expired.data == '1m':
            expired = expired + relativedelta(months=+1)
        elif form.expired.data == '3m':
            expired = expired + relativedelta(months=+3)
            periods = 3
        elif form.expired.data == '6m':
            expired = expired + relativedelta(months=+6)
            periods = 6
        elif form.expired.data == '1y':
            expired = expired + relativedelta(years=+1)
            periods = 12
        else:
            pass
        user = User.query.filter_by(name=form.name.data).first()
        user.payday = int(datetime.utcnow().day)
        user.package_id = int(form.package.data)
        user.expired = datetime(expired.year, expired.month, expired.day, 0, 0, 0)
        user.status = "active"
        db.session.add(user)
        db.session.commit()

        package = Package.query.filter_by(id = form.package.data).first()
        for p in range(0, periods):
            period = (datetime.now() + relativedelta(months=+p)).strftime("%y-%m-%d")
            usertraffic = Usertraffic(package_traffic=package.traffic, period=period, user_id=user.id)
            db.session.add(usertraffic)
            db.session.commit()
        return redirect(url_for("admin.admin_main"))
    else:
        return render_template("admin/active_user.html", form=form)

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

    user = User.query.filter_by(id=userlog.user_id).first()
    usertraffic = Usertraffic.query.filter_by(user_id=userlog.user_id).filter_by(period=get_period(user.payday)).first()
    usertraffic.consume_traffic = usertraffic.consume_traffic + int(request.form["traffic"])
    db.session.add(usertraffic)
    db.session.commit()
    return "ok", 200
