# -*- coding: utf-8 -*-
"""
Api类继承flask_restful
"""
import sys
from flask_restful import Api
from flask import current_app, Blueprint
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException
from flask.signals import got_request_exception
from flask_restful.utils import http_status_message


class RestfulApi(Api):

    def handle_error(self, e):
        """
        自定义异常抛出类型
        :param object e: the raised Exception object
        """
        got_request_exception.send(current_app._get_current_object(), exception=e)

        if not isinstance(e, HTTPException) and current_app.propagate_exceptions:
            exc_type, exc_value, tb = sys.exc_info()
            if exc_value is e:
                raise
            else:
                raise e

        headers = Headers()
        if isinstance(e, HTTPException):
            if e.response is not None:
                resp = e.get_response()
                return resp

            code = e.code
            default_data = {'code': code,
                            'message': getattr(e, 'description', http_status_message(code))
                            }
            headers = e.get_response().headers
        else:
            code = 500
            default_data = {'code': code,
                            'message': http_status_message(code),
                            }

        remove_headers = ('Content-Length',)

        for header in remove_headers:
            headers.pop(header, None)

        try:
            message_dict = getattr(e, 'data')
            data = {"code": e.code,
                    "message": message_dict.get("message")}
        except AttributeError:
            data = default_data

        if code and code >= 500:
            exc_info = sys.exc_info()
            if exc_info[1] is None:
                exc_info = None
            current_app.log_exception(exc_info)

        error_cls_name = type(e).__name__
        if error_cls_name in self.errors:
            custom_data = self.errors.get(error_cls_name, {})
            code = custom_data.get('status', 500)
            data.update(custom_data)

        if code == 406 and self.default_mediatype is None:
            supported_media_types = list(self.representations.keys())
            fallback_media_type = supported_media_types[0] if supported_media_types else "text/plain"
            resp = self.make_response(
                data,
                code,
                headers,
                fallback_mediatype=fallback_media_type
            )
        else:
            resp = self.make_response(data, code, headers)

        if code == 401:
            resp = self.unauthorized(resp)
        return resp


def api_factory(blueprint_name: Blueprint, decorators=None):
    """
    api工厂
    :param object blueprint_name: 蓝本
    :param list decorators: 装饰器列表  例如：[check_http_headers, check_request_frequency]
    :return: api对象
    """
    api = RestfulApi(blueprint_name)
    api.catch_all_404s = False
    api.serve_challenge_on_401 = False
    api.default_mediatype = "application/json; charset=UTF-8"
    # api.prefix = "/" + blueprint_name.name
    api.decorators = decorators if decorators else []
    return api
