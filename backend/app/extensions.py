from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_caching import Cache
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")  # 在 create_app 中根据配置重置
cache = Cache()
compress = Compress()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per minute"])