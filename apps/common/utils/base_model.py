# -*- coding: utf-8 -*-
"""
ORM基础模型
"""
import json
from sqlalchemy import inspect
from datetime import datetime, timezone
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy.sql.sqltypes import DateTime

from apps.common.utils.extensions import db

__all__ = ['BaseModel']


class AdminMixin(object):
    """
    数据管理模型
    """
    creator_key = db.Column('creator_key', db.String(50), nullable=True, comment='创建人标识')
    create_time = db.Column('create_time', db.DateTime, default=datetime.utcnow, nullable=True, comment='创建时间')
    update_time = db.Column('update_time', db.DateTime, onupdate=datetime.utcnow, nullable=True,
                            default=datetime.utcnow, comment='更新时间')
    is_deleted = db.Column('is_deleted', db.Boolean, nullable=True, default=False, comment='已删除')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BaseModel(db.Model, AdminMixin):
    # __abstract__这个属性设置为True,这个类为基类，不会被创建为表！
    __abstract__ = True

    @staticmethod
    def str_is_object(args: str) -> bool:
        try:
            value = json.loads(args)
            if isinstance(value, list) or isinstance(value, dict):
                return True
            else:
                return False
        except (json.decoder.JSONDecodeError, TypeError):
            return False

    def to_dict(self):
        """
        转换为字典datetime为字符串，json自动解析
        """
        d = {}
        for column_name, column_attr in self.columns_attr_dict().items():
            if isinstance(column_attr.get("type"), JSON) and column_attr.get("value") is not None:
                if self.str_is_object(column_attr.get("value")) or \
                        isinstance(column_attr.get("value"), bytes) or \
                        isinstance(column_attr.get("value"), bytearray):
                    v = json.loads(column_attr.get("value"))
                else:
                    v = column_attr.get("value")
            elif isinstance(column_attr.get("type"), DateTime):
                """
                %Y-%m-%dT%H:%M:%S%z      2020-06-08T10:53:32+0800
                %Y-%m-%dT%H:%M:%S.%f%z   2020-06-08T10:53:32.000000+0800
                isoformat()              2020-06-08T10:53:32+08:00   
                """
                # v = c_value.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%Y-%m-%dT%H:%M:%S%z")
                # v = c_value.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                v = column_attr.get("value").replace(tzinfo=timezone.utc).astimezone(
                    tz=None).isoformat()  # 等效。isoformat就是上面的格式
            else:
                v = column_attr.get("value")
            d[column_name] = v
        return d

    def update(self, **kwargs):
        columns_dict = self.columns_attr_dict()
        for key, value in kwargs.items():
            # 过滤掉参数值为空和主键
            if key in columns_dict.keys() and not columns_dict.get(key).get("primary_key") and value is not None:
                setattr(self, key, value)

    def columns_attr_dict(self):
        # from sqlalchemy.sql.schema import Column
        columns_attr_dict = inspect(self).mapper.column_attrs
        # 获取模型列的必填属性，必填为True，非必填为False
        data = dict()
        for column_name, column_attr in columns_attr_dict.items():
            column_attr_dict = dict(value=getattr(self, column_attr.key),
                                    nullable=column_attr.columns[0].nullable,
                                    primary_key=column_attr.columns[0].primary_key,
                                    default=column_attr.columns[0].default,
                                    server_default=column_attr.columns[0].server_default,
                                    server_onupdate=column_attr.columns[0].server_onupdate,
                                    index=column_attr.columns[0].index,
                                    unique=column_attr.columns[0].unique,
                                    doc=column_attr.columns[0].doc,
                                    onupdate=column_attr.columns[0].onupdate,
                                    autoincrement=column_attr.columns[0].autoincrement,
                                    constraints=column_attr.columns[0].constraints,
                                    foreign_keys=column_attr.columns[0].foreign_keys,
                                    comment=column_attr.columns[0].comment,
                                    type=column_attr.columns[0].type,
                                    computed=column_attr.columns[0].computed,
                                    )
            data[column_name] = column_attr_dict
        return data
