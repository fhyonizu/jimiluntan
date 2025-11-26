from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import config
from .extensions import db, migrate, socketio # 引入 socketio

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)
    socketio.init_app(app) # 🔥 初始化 SocketIO

    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.posts import posts_bp
    from .routes.admin import admin_bp
    from .routes.main import main_bp
    from .routes.user import users_bp
    from .routes.social import social_bp # 确保有这个

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(main_bp, url_prefix='/api') # upload 在这里，所以是 /api/upload
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(social_bp, url_prefix='/api/social')

    # 引入 Socket 事件处理
    from . import events

    return app