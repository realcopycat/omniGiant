import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:  # 这是一个很重要的基本配置文件, 用来适配不同环境下的不同配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess'  # 任何密码都不应该放在源码中，而是应该在环境变量中配置
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    @staticmethod  # 这个意思是指静态方法
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
