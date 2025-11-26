from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO # 新增

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*") # 新增，允许跨域