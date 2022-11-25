# -*- coding: utf-8 -*-
from flask_restful import reqparse

from apps.test.test_services import TestDemoService
from apps.common.utils.base_resource import BaseResource
from apps.common.http.response_formatter import RespFormatter


class ResourceBaseView(BaseResource):
    def __init__(self):
        super().__init__()
        self.test_demo_obj = TestDemoService()


class UserLoggedAuth(ResourceBaseView):
    # method_decorators = {'post': [login_required],
    #                      'get': [login_required],
    #                      'put': [login_required],
    #                      'delete': [login_required]
    #                      }
    pass


class AdminLoggedAuth(ResourceBaseView):
    # method_decorators = {'post': [admin_auth, login_required],
    #                      'get': [login_required],
    #                      'put': [admin_auth, login_required],
    #                      'delete': [admin_auth, login_required]
    #                      }
    pass


class TestView(UserLoggedAuth):

    def get(self):
        """
        获取XXX
        """
        # 获取请求参数, bundle_errors: 错误捆绑在一起并立即发送回客户端
        parse = reqparse.RequestParser(bundle_errors=True)

        # location表示获取args中的关键字段进行校验，required表示必填不传报错，type表示字段类型
        parse.add_argument("current-login-user", type=str, help="参数<current-login-user>校验错误",
                           required=True, location='headers', dest='current_login_user', trim=True)
        parse.add_argument("string", type=str, help="参数<string>校验错误", required=True, location='args', trim=True)
        # 获取传输的值/strict=True代表设置如果传以上未指定的参数主动报错
        kwargs = parse.parse_args(strict=True)
        status, result = self.test_demo_obj.test(**kwargs)
        if status:
            self.logger.info(self.logger_formatter + " 成功...")
            result["result"] = "success"
        else:
            self.logger.error(self.logger_formatter + " 失败...")
        return RespFormatter.body(**result), int(str(result.get("code"))[0:3])
