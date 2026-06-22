import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import config
from .extensions import db, migrate, socketio, cache, compress, limiter
from sqlalchemy import event
from sqlalchemy.engine import Engine


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # CORS
    CORS(app, resources={r"/*": {"origins": os.environ.get('CORS_ORIGINS', 'http://localhost:5173')}}, supports_credentials=True)

    # 数据库
    db.init_app(app)
    migrate.init_app(app, db)

    # SQLite WAL 模式 + 外键 (高并发优化)
    with app.app_context():
        from sqlalchemy import text
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=-8000")
                cursor.close()

    # JWT
    JWTManager(app)

    # SocketIO
    socketio.init_app(app)

    # 缓存 (60s TTL for hot endpoints)
    cache.init_app(app)

    # Gzip 压缩
    compress.init_app(app)

    # 限流
    limiter.init_app(app)

    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.posts import posts_bp
    from .routes.admin import admin_bp
    from .routes.main import main_bp
    from .routes.user import users_bp
    from .routes.social import social_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(social_bp, url_prefix='/api/social')

    from . import events

    return app
