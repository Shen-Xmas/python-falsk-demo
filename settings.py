# -*- coding: utf-8 -*-
"""
服务环境变量及其配置
"""
import os, platform
from pathlib import Path
from base64 import b64encode
from datetime import timedelta

from apps.common.utils.parse_yaml import ProjectConfig

__all__ = ['config']


class BaseConfig(object):
    """
    环境基类
    """
    __random_32 = b64encode(os.urandom(32)).decode()

    def __init__(self, env, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 获取项目根目录
        self.PROJECT_HOME = Path(__file__).parent
        # 加载第三方配置
        self.ENV = env
        self.CONFIG = ProjectConfig.get_object(env)

        # 给日志提供服务名，目前的日志头只支持flask启动的 werkzeug 服务和 linux上启动的 gunicor 服务
        self.SERVICE_NAME = "werkzeug" if "Windows" in platform.system() else "gunicorn.error"

        # 加盐的秘钥
        self.SECRET_KEY = os.getenv("SECRET_KEY", self.__random_32)

        self.DB_CONFIG = self.CONFIG.db_config

        # 绑定数据库
        self.SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
            self.DB_CONFIG.db.type,
            self.DB_CONFIG.db.driver,
            self.DB_CONFIG.db.username,
            self.DB_CONFIG.db.password,
            self.DB_CONFIG.db.host,
            self.DB_CONFIG.db.port,
            self.DB_CONFIG.db.database
        )

        # 绑定rabbitmq
        self.FLASK_PIKA_PARAMS = {
            "host": self.DB_CONFIG.rabbitmq.host,
            "username": self.DB_CONFIG.rabbitmq.username,
            "password": self.DB_CONFIG.rabbitmq.password,
            "port": self.DB_CONFIG.rabbitmq.port,
            "virtual_host": self.DB_CONFIG.rabbitmq.virtual_host,
        }
        # self.FLASK_PIKA_POOL_PARAMS = {
        #     "pool_size": self.DB_CONFIG.rabbitmq.pool_size,
        #     "pool_recycle": self.DB_CONFIG.rabbitmq.pool_recycle
        # }
        self.FLASK_PIKA_POOL_PARAMS = None


class DevelopmentConfig(BaseConfig):
    """
    开发环境
    """

    def __init__(self, env, *args, **kwargs):
        super().__init__(env, *args, **kwargs)
        # 日志记录器的名称
        # self.LOGGER_NAME = None

        # 日志记录级别
        # self.LOG_LEVEL = DEBUG

        # Session的生命周期(天), 默认31天
        self.PERMANENT_SESSION_LIFETIME = timedelta(days=7)

        # 是否开启Debug模式
        self.DEBUG = True

        # 关闭Flask-DebugToolbar拦截重定向请求
        self.DEBUG_TB_INTERCEPT_REDIRECTS = False

        # 开启查询记录
        self.SQLALCHEMY_RECORD_QUERIES = True

        # 是否开启测试模式
        # self.TESTING = True

        # 异常传播(是否在控制台打印LOG) 当Debug或者testing开启后,自动为True
        # self.PROPAGATE_EXCEPTIONS = True


class ProductionConfig(BaseConfig):
    """
    生产环境
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Session的生命周期(天), 默认31天
        self.PERMANENT_SESSION_LIFETIME = timedelta(days=1)

        # 是否开启Debug模式
        self.DEBUG = False

        # 日志记录级别
        # self.LOG_LEVEL = DEBUG


config = {
    "development": DevelopmentConfig("development"),
    "production": ProductionConfig("production")
}
