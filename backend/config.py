import os
from datetime import timedelta, timezone

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 数据库路径 (Windows 路径兼容)
    _db_path = os.path.join(basedir, 'forum.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + _db_path.replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # 密钥 (务必通过环境变量设置，开发时可用 .env)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-this'

    # Token 有效期
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_DAYS', '7')))


config = {
    'default': Config
}