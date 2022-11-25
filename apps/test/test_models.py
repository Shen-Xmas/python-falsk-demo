# -*- coding: utf-8 -*-
"""

"""
from apps.common.utils.extensions import db
from apps.common.utils.base_model import BaseModel


class TestDemoModel(BaseModel):
    """
    xxx实例模型
    """
    __tablename__ = 'app_xxx'
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, nullable=False, comment="主键id")

    # 给表添加注释
    __table_args__ = ({'comment': 'xxx实例'})

    def __repr__(self):
        return "<TestDemo %d>" % self.id
