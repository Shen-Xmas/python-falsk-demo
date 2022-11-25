import logging
import platform
from apps.common.utils.service import Service

# 在windows上调式运行，使用flask的wsgi模块运行，需要抓取werkzeug日志
# 在linux上运行，通常会使用gunicorn替代wsgi，则需要抓取gunicorn.error日志
logger = logging.getLogger('werkzeug') if "Windows" in platform.system() else logging.getLogger('gunicorn.error')


class Cache(object):

    def __init__(self, cache_key: str):
        self.cache_key = cache_key

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            service = Service()
            flag, result = service.get_redis_data("redis_cache", "cache_instance_schema", self.cache_key)
            if not flag:
                flag, result = func(*args, **kwargs)
                if not flag:
                    return flag, result
                cache_value = result.get("data")
                service.save_to_redis("redis_cache", "cache_instance_schema", self.cache_key, cache_value)
            return flag, result

        return wrapped


class CacheProxy(object):
    __cls = dict()

    def __init__(self, cache_group: str, inbound: bool = False, outbound: bool = False, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.inbound = inbound
        self.outbound = outbound
        self.cache_group = cache_group

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            flag, result = func(*args, **kwargs)
            if flag:
                cache_key = result.pop("cache_key") if "cache_key" in result.keys() else None
                if self.inbound and not self.outbound and cache_key:
                    self.pub(cache_key)
                elif not self.inbound and self.outbound:
                    self.sub()
            return flag, result

        return wrapped

    def pub(self, *args):
        """生产者"""
        keys = self.__cls.get(self.cache_group)
        logger.info("当前缓存代理组[{}]保存的数据为： <{}>。".format(self.cache_group, keys if keys else "无"))
        if args:
            logger.info("缓存代理组[{}]需要插入新数据为： <{}>。".format(self.cache_group, args))
            if keys:
                for x in args:
                    if x not in keys:
                        keys.append(x)
            else:
                keys = list(args)
            self.__cls[self.cache_group] = keys
            logger.info("当前缓存代理组[{}]刷新后的数据为： <{}>。".format(self.cache_group, self.__cls))
        else:
            logger.info("缓存代理组[{}]无需刷新。".format(self.cache_group))

    def sub(self):
        """消费者"""
        if self.cache_group in self.__cls.keys():
            from apps.common.utils.service import Service
            service = Service()
            keys = self.__cls.get(self.cache_group)
            if keys:
                logger.info("开始消费当前缓存代理组[{}]的缓存keys: <{}>".format(self.cache_group, keys))
                cmdb_cache = service.db_config.rabbitmq.queue.cmdb_cache
                service.set_mq_client(cmdb_cache)
                service.publish(cmdb_cache, dict(keys=keys))
                logger.info("当前缓存代理状态：<{}>".format(self.__cls))
