# start up

from flask import Flask
from flask_bootstrap import Bootstrap
from config import config

bootstrap = Bootstrap()  # 初始化组件


def create_app(config_name):  # 这又被称为工厂函数
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)  # 按照应用配置启动应用

    bootstrap.init_app(app)

    from .main import main as main_blueprint  # 引入蓝本在最后
    app.register_blueprint(main_blueprint)

    return app





