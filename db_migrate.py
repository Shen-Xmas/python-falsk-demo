# -*- coding: utf-8 -*-
"""
数据库迁移

"""
from pathlib import Path
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate

from apps.init_app import flask_app
from apps.common.utils.extensions import db
from apps.test.test_models import TestDemoModel


def create_migrate(app):
    manager = Manager(app)

    # 绑定APP和DB, 可指定migrations目录
    migrate = Migrate(app, db, Path(app.config["PROJECT_HOME"], "migrations"), compare_type=True,
                      compare_server_default=True)

    # 添加迁移脚本的命令道manager中
    manager.add_command('db', MigrateCommand)

    return manager


migrate = create_migrate(flask_app)

if __name__ == '__main__':
    migrate.run()
