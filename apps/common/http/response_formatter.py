# -*- coding: utf-8 -*-
"""
响应消息格式化
"""
from copy import deepcopy
from flask_restful import fields

from apps.common.http.error_code import MsgDesc


class RespFormatter(object):
    success_resp = {
        "code": 200101,
        "message": MsgDesc.h_200101.value
    }

    failed_resp = {
        "code": 500101,
        "message": MsgDesc.h_500101.value
    }

    @classmethod
    def __formatter(cls, **kwargs):
        if kwargs.get("result") == "success":
            success_resp = deepcopy(cls.success_resp)
            if kwargs.get("code") is not None:
                success_resp['code'] = kwargs.get("code")
            if kwargs.get("message") is not None:
                success_resp["message"] = kwargs.get("message")
            if kwargs.get("data") is not None:
                success_resp['data'] = kwargs.get("data")
            if kwargs.get("current_page"):
                success_resp["current_page"] = kwargs.get("current_page")
                success_resp['per_page'] = kwargs.get("per_page")
                success_resp["pages"] = kwargs.get("pages")
                success_resp["has_prev"] = kwargs.get("has_prev")
                success_resp['has_next'] = kwargs.get("has_next")
                success_resp['total'] = kwargs.get("total")
            return success_resp
        else:
            failed_resp = deepcopy(cls.failed_resp)
            if kwargs.get("code") is not None:
                failed_resp['code'] = kwargs.get("code")
            if kwargs.get("message") is not None:
                failed_resp["message"] = kwargs.get("message")
            return failed_resp

    @classmethod
    def body(cls, **kwargs):
        return cls.__formatter(**kwargs)


class FieldFormatter(fields.Raw):

    # 自定义格式化函数
    def format(self, value):
        if isinstance(value, str) or isinstance(value, dict) or isinstance(value, list) or \
                isinstance(value, bool) or isinstance(value, int):
            return value
        # elif isinstance(value, int) and value > 18:
        #     return "adult"
        # elif isinstance(value, int) and value <= 18:
        #     return "child"
        else:
            return None
