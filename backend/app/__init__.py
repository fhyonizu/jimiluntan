import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import config
from .extensions import db, migrate, socketio, cache, compress, limiter
from sqlalchemy import event
from sqlalchemy.engine import Engine


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    app_config = config[config_name]
    app.config.from_object(app_config)

    # CORS — 从配置读取；Docker+Nginx 同域部署时 CORS_ORIGINS 为空则不添加 CORS 头
    cors_origins = app.config.get('CORS_ORIGINS', '')
    if cors_origins:
        CORS(app, resources={r"/*": {"origins": cors_origins.split(','), "supports_credentials": True}})

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

    # SocketIO — 从配置读取 CORS
    socketio_cors = app.config.get('SOCKETIO_CORS', '')
    socketio.cors_allowed_origins = socketio_cors.split(',') if socketio_cors else []
    socketio.init_app(app)

    # 缓存
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

    # ── 全局错误处理 ──
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'code': 400, 'message': '请求参数错误'}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'code': 401, 'message': '未授权，请先登录'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'code': 404, 'message': '资源不存在'}), 404

    @app.errorhandler(429)
    def too_many(e):
        return jsonify({'code': 429, 'message': '请求过于频繁，请稍后再试'}), 429

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error('服务器内部错误')
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

    # 生产环境校验
    if config_name == 'production' and hasattr(app_config, 'validate'):
        app_config.validate()

    return app