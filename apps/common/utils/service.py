# -*- coding: utf-8 -*-
import traceback
from json import loads, dumps, decoder
from redis import Redis, ConnectionPool

from apps.common.http.error_code import MsgDesc
from apps.common.decorator.log_service import auto_log
from apps.common.utils.parse_yaml import ProjectConfig


class Service(object):
    # 此处拿到的配置对象，是根据环境变量 ENV_TYPE 过滤后的。
    # 因此，如果是线上环境部署，必须要在操作系统里面配置 ENV_TYPE环境变量
    CONFIG = ProjectConfig.get_object()
    db_config = CONFIG.db_config

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mq_chanel = None
        self.traceback = traceback

    @classmethod
    @auto_log
    def get_redis(cls, node_name: str, db_schema: str, decode_responses=False):
        redis_config = getattr(cls.db_config, node_name)
        redis_pool = ConnectionPool(host=redis_config.host,
                                    port=redis_config.port,
                                    password=redis_config.password,
                                    db=redis_config.get(db_schema),
                                    decode_responses=decode_responses)
        redis = Redis(connection_pool=redis_pool)
        return redis

    @classmethod
    @auto_log
    def save_to_redis(cls, node_name: str, db_schema: str, key: str, data, ex: int = 86400):
        redis = cls.get_redis(node_name, db_schema)
        if not isinstance(data, str):
            data = dumps(data)
        redis.set(key, data, ex=ex, nx=False)

    @classmethod
    @auto_log
    def get_redis_data(cls, node_name: str, db_schema: str, key: str = None) -> tuple:
        redis = cls.get_redis(node_name, db_schema)
        if redis.connection_pool:
            db = redis.connection_pool.connection_kwargs.get("db")
        else:
            db = redis.connection.connection_kwargs.get("db")
        if key:
            data = redis.get(key)
            if data:
                if cls.is_json(data):
                    data = loads(data)
                else:
                    data = str(data, encoding="utf-8")
            else:
                return False, dict(code=400113, message=MsgDesc.h_400113.value.format(db, key))
        else:
            data = dict()
            for key in redis.keys():
                key = str(key, encoding="utf-8")
                value = redis.get(key)
                if value:
                    if cls.is_json(value):
                        value = loads(value)
                    else:
                        value = str(value, encoding="utf-8")
                data[key] = value
            if not data:
                return False, dict(code=400114, message=MsgDesc.h_400114.value.format(db))
        return True, dict(code=200101, data=data, message=MsgDesc.h_200101.value)

    @staticmethod
    def is_json(args: str) -> bool:
        try:
            value = loads(args)
            if isinstance(value, list) or isinstance(value, dict) or \
                    isinstance(value, bytes) or isinstance(value, bytearray):
                return True
            else:
                return False
        except (decoder.JSONDecodeError, TypeError):
            return False
