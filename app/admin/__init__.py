#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import views, errors
