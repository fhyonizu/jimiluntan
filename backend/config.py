import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 数据库路径
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'forum.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # 密钥 (生产环境请修改)
    SECRET_KEY = 'dev-secret-key-change-this'
    JWT_SECRET_KEY = 'jwt-secret-key-change-this'

    # Token 有效期：30天 (方便测试)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)


config = {
    'default': Config
}