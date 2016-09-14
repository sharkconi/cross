#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint

user = Blueprint('user', __name__)

from . import views, errors
