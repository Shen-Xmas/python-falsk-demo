# -*- coding: utf-8 -*-
"""
基础服务
"""
from flask import current_app
from flask_sqlalchemy import BaseQuery

from apps.common.utils.extensions import db
from apps.common.utils.service import Service
from apps.common.http.error_code import MsgDesc
from apps.common.decorator.log_service import auto_log


class BaseService(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db
        self.logger = current_app.logger
        self.app = current_app._get_current_object()

    @classmethod
    @auto_log
    def pagination(cls, data: BaseQuery, current_page: int = 1, per_page: int = 10, max_per_page: int = 100) -> tuple:
        # 根据SQLAlchemy直接分页
        total = data.count()
        info_list = list()
        # 总页码数
        pages = 0
        # 是否有前一页
        has_prev = False
        # 是否有后一页
        has_next = True
        if total > 0:
            if total % per_page == 0:
                pages = total // per_page
            else:
                pages = total // per_page + 1
            # 如果请求的页面数大于数据的总页面数，将报错
            if current_page > pages or per_page > max_per_page:
                return False, dict(code=400126, message=MsgDesc.h_400126.value)
            pagination_object = data.paginate(page=current_page, per_page=per_page, error_out=True,
                                              max_per_page=max_per_page)
            info_list = [x.to_dict() for x in pagination_object.items]
        if current_page > 1 and total > 0:
            has_prev = True
        if current_page == pages or pages == 0:
            has_next = False
        return True, dict(code=200101, message=MsgDesc.h_200101.value, data=info_list,
                          current_page=current_page, per_page=per_page,
                          has_prev=has_prev, has_next=has_next, pages=pages, total=total)
