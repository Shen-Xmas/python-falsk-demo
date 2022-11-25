# -*- coding: utf-8 -*-
"""
app工厂
"""
import os
import click
from flask_cors import CORS
from flask import Flask, request
from flask.logging import default_handler

from settings import config
from apps.test.test_brueprint import test_bp
from apps.common.utils.parse_yaml import ProjectConfig
from apps.common.logging import MultiprocessRotatingLog
from apps.common.utils.extensions import db, migrate, session

__all__ = ["flask_app"]


def create_app(config_name=None):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask('ProjectFrame', root_path=root_path)
    register_env(app, config_name)
    register_session(app)
    register_flask_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_request_handlers(app)
    register_commands(app)

    return app


def register_session(app):
    session.init_app(app)


def register_env(app, config_name):
    app.config.from_object(config[config_name])
    app.config.update(ProjectConfig.get_object().app_constant)


def register_flask_logging(app):
    logger = MultiprocessRotatingLog(app.config['PROJECT_HOME'], app.config['SERVICE_NAME']).log
    app.logger.removeHandler(default_handler)
    app.logger = logger


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, supports_credentials=True)


def register_blueprints(app):
    app.register_blueprint(test_bp, url_prefix='/' + test_bp.name)


def register_request_handlers(app):
    @app.before_request
    def http_request():
        request_method = request.headers.environ.get("REQUEST_METHOD")
        remote_port = request.headers.environ.get("REMOTE_PORT")
        # 前端调用服务端
        origin = request.headers.environ.get("HTTP_ORIGIN").split("//")[1] if request.headers.environ.get(
            "HTTP_ORIGIN") else None
        forwarded_for = request.headers.environ.get("HTTP_X_FORWARDED_FOR").split(",")[
            0] if request.headers.environ.get("HTTP_X_FORWARDED_FOR") else None
        remote_addr = forwarded_for if forwarded_for else \
            request.headers.environ.get("REMOTE_ADDR").split(",")[0]
        if origin:
            app.logger.info("来自域名：<{}>的转发主机IP：<{}>的端口：[{}]通过 {} 方法访问url：{}。".format(
                origin, remote_addr, remote_port, request_method, request.url))
        else:
            app.logger.info("来自主机IP：<{}>的端口：[{}]通过 {} 方法访问url：{}。".format(
                remote_addr, remote_port, request_method, request.url))


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def init_db(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')


# 操作系统需配置环境变量：ENV_TYPE，否则视为 development 环境
env_type = os.getenv("ENV_TYPE")
if not env_type:
    env_type = "development"

flask_app = create_app(env_type)
