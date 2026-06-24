import os
from datetime import timedelta, timezone
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))


class Config:
    # ==================== 数据库 ====================
    _db_path = os.path.join(basedir, 'forum.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + _db_path.replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'connect_args': {'check_same_thread': False},
    }

    # ==================== 密钥 ====================
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-this'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_DAYS', '7')))

    # ==================== 缓存 (内存) ====================
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_TTL', '60'))

    # ==================== 压缩 ====================
    COMPRESS_MIN_SIZE = 500

    # ==================== 限流 ====================
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'

    # ==================== CORS ====================
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '')

    # ==================== SocketIO ====================
    SOCKETIO_CORS = os.environ.get('SOCKETIO_CORS', '')


class ProductionConfig(Config):
    SQLALCHEMY_ECHO = False
    DEBUG = False

    @classmethod
    def validate(cls) -> None:
        """生产环境必须设置真实密钥"""
        if cls.SECRET_KEY == 'dev-secret-key-change-this':
            raise RuntimeError('⚠️  生产环境必须设置 SECRET_KEY 环境变量！')
        if cls.JWT_SECRET_KEY == 'jwt-secret-key-change-this':
            raise RuntimeError('⚠️  生产环境必须设置 JWT_SECRET_KEY 环境变量！')


config = {
    'default': Config,
    'production': ProductionConfig,
}
