#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from . import user 
from .. import db
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


@user.route("/<string:username>")
def admin_main(username):
    if username is None:
        return "error", 404
    user = User.query.filter_by(name=username).first()
    if user is None:
        return "We don't know who you are", 404

    package = Package.query.filter_by(id=user.package_id).first()
    usertraffic = Usertraffic.query.filter_by(user_id=user.id).filter_by(period=get_period(user.payday)).first()
    if user.status == 'inactive':
        return "Sorry, Your service is out of date, you can renew your service"

    info = {"name":user.name, "package":package.name, "package_traffic":package.traffic, "package_price":5, \
        "period_traffic":usertraffic.package_traffic, "progress":(usertraffic.consume_traffic/1024/1024)*100/usertraffic.package_traffic, \
        "lastperiod_traffic":usertraffic.last_traffic, "consume_traffic":usertraffic.consume_traffic/1024/1024, "expired":user.expired.strftime("%y-%m-%d")}
  
    return render_template("user/user_info.html", info=info)
