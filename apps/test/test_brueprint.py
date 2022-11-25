# -*- coding: utf-8 -*-
from flask import Blueprint

from apps.test.test_views import TestView
from apps.common.http.restfulApi import api_factory


test_blue_name = "test"
test_bp = Blueprint(test_blue_name, __name__)

test_api = api_factory(test_bp)

# 添加路由
test_api.add_resource(TestView, '/test', endpoint='test')
