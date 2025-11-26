from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from .models import User

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # 🔥 核心修复：如果是 OPTIONS 请求，直接放行，不做鉴权
            # 这样 Flask-CORS 插件就能接手并返回正确的 CORS 头
            if request.method == 'OPTIONS':
                return fn(*args, **kwargs)

            # 1. 验证 JWT 是否存在且有效
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({'code': 401, 'message': '请先登录'}), 401

            # 2. 获取当前用户 ID
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'code': 401, 'message': '用户身份无效'}), 401

            # 3. 查库确认用户角色 (双重保险)
            user = User.query.get(user_id)
            if not user or user.role != 'admin':
                return jsonify({'code': 403, 'message': '权限不足，仅限管理员访问'}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper