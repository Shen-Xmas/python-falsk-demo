# -*- coding: utf-8 -*-
from apps.common.http.error_code import MsgDesc
from apps.common.decorator.log_service import auto_log
from apps.common.utils.base_service import BaseService


class TestDemoService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @auto_log
    def test(self, string: str) -> tuple:
        return True, dict(code=200101, message=MsgDesc.h_200101.value, data=string)
