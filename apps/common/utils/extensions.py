# -*- coding: utf-8 -*-
"""
服务使用到的扩展模块对象
"""
from flask_session import Session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
session = Session()
migrate = Migrate()
