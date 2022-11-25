import platform
import logging
import traceback
from functools import wraps

from apps.common.http.error_code import MsgDesc

# 在windows上调式运行，使用flask的wsgi模块运行，需要抓取werkzeug日志
# 在linux上运行，通常会使用gunicorn替代wsgi，则需要抓取gunicorn.error日志
logger = logging.getLogger('werkzeug') if "Windows" in platform.system() else logging.getLogger('gunicorn.error')


def auto_log(func):
    """
    自动打印日志
    :param func:
    :return:
    """

    @wraps(func)
    def _deco(*args, **kwargs):
        try:
            real_func = func(*args, **kwargs)
            return real_func
        except Exception as e:
            logger.error(traceback.format_exc())
            return False, dict(code=500101, message=MsgDesc.h_500101.value + str(e))

    return _deco
