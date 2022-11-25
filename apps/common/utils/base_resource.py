# -*- coding: utf-8 -*-
"""
api的基类
"""
from flask import session
from flask_restful import Resource
from flask import request, current_app

from apps.common.utils.parse_yaml import ProjectConfig


class BaseResource(Resource):
    CONFIG = ProjectConfig.get_object()

    def __init__(self):
        self.__env = request.headers.environ
        self.origin = self.__env.get("HTTP_ORIGIN").split("//")[1] if self.__env.get("HTTP_ORIGIN") else None
        self.forwarded_for = self.__env.get("HTTP_X_FORWARDED_FOR").split(",")[0] if self.__env.get(
            "HTTP_X_FORWARDED_FOR") else None
        self.remote_ip = self.forwarded_for if self.forwarded_for else \
            self.__env.get("REMOTE_ADDR").split(",")[0]
        self.remote_port = self.__env.get("REMOTE_PORT")
        self.method = self.__env.get("REQUEST_METHOD")
        self.url = request.url
        self.access_user = request.remote_user
        self.logger = current_app.logger
        self.session = session

        if self.access_user:
            if self.origin:
                self.logger_formatter = "来自域名：<{}>的转发主机".format(self.origin) + \
                                        "IP：<{}>".format(self.remote_ip) + \
                                        "的端口：[{}]的 {} 用户".format(self.remote_port, self.access_user) + \
                                        "通过 {} ".format(self.method) + \
                                        "方法访问url：{}".format(self.url)
            else:
                self.logger_formatter = "来自主机IP：<{}>".format(self.remote_ip) + \
                                        "的端口：[{}]的 {} 用户".format(self.remote_port, self.access_user) + \
                                        "通过 {} ".format(self.method) + \
                                        "方法访问url：{}".format(self.url)
        else:
            if self.origin:
                self.logger_formatter = "来自域名：<{}>的转发主机".format(self.origin) + \
                                        "IP：<{}>".format(self.remote_ip) + \
                                        "的端口：[{}]".format(self.remote_port) + \
                                        "通过 {} ".format(self.method) + \
                                        "方法访问url：{}".format(self.url)
            else:
                self.logger_formatter = "来自主机IP：<{}>".format(self.remote_ip) + \
                                        "的端口：[{}]".format(self.remote_port) + \
                                        "通过 {} ".format(self.method) + \
                                        "方法访问url：{}".format(self.url)
