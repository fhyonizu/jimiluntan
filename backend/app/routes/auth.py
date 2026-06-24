from flask import Blueprint, request, jsonify, current_app
from ..extensions import db, limiter
from ..models import User, PasswordResetRequest
from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta
import re

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# 输入长度限制
MAX_NICKNAME = 32
MAX_EMAIL = 120
MIN_PASSWORD = 6


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    email = (data.get('email') or '').strip()
    nickname = (data.get('nickname') or '').strip()
    password = data.get('password') or ''

    # 验证邮箱
    if not email or not EMAIL_REGEX.match(email):
        return jsonify({'code': 400, 'message': '请输入有效的邮箱地址'}), 400
    if len(email) > MAX_EMAIL:
        return jsonify({'code': 400, 'message': f'邮箱不能超过{MAX_EMAIL}个字符'}), 400

    # 验证昵称
    if not nickname or len(nickname) < 2:
        return jsonify({'code': 400, 'message': '昵称至少需要2个字符'}), 400
    if len(nickname) > MAX_NICKNAME:
        return jsonify({'code': 400, 'message': f'昵称不能超过{MAX_NICKNAME}个字符'}), 400

    # 验证密码
    if not password or len(password) < MIN_PASSWORD:
        return jsonify({'code': 400, 'message': f'密码至少需要{MIN_PASSWORD}个字符'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'message': '邮箱已存在'}), 400

    if User.query.filter_by(username=nickname).first():
        return jsonify({'code': 400, 'message': '昵称已被占用'}), 400

    user = User(username=nickname, email=email)
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'code': 201, 'message': '注册成功'}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('注册失败')
        return jsonify({'code': 500, 'message': '注册失败'}), 500


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'code': 400, 'message': '请输入邮箱和密码'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'code': 401, 'message': '账号或密码错误'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'code': 200, 'message': '登录成功', 'access_token': token, 'user': user.to_dict()}), 200


# ==========================================
# 邮箱验证 (简化版)
# ==========================================
@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    email = (data.get('email') or '').strip()
    token = data.get('token') or ''

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    try:
        decoded = decode_token(token)
        if str(decoded.get('sub')) == str(user.id) and decoded.get('type') == 'email_verify':
            user.email_verified = True
            db.session.commit()
            return jsonify({'code': 200, 'message': '邮箱验证成功！'}), 200
        return jsonify({'code': 400, 'message': '验证失败，链接与用户不匹配'}), 400
    except Exception:
        return jsonify({'code': 400, 'message': '验证链接无效或已过期'}), 400


# ==========================================
# 密码重置 — 向管理员申请重置
# ==========================================
@auth_bp.route('/request-password-reset', methods=['POST'])
@limiter.limit("3 per minute")
def request_password_reset():
    """用户申请重置密码，需管理员审批"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    email = (data.get('email') or '').strip()
    if not email:
        return jsonify({'code': 400, 'message': '请输入邮箱'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        # 不暴露用户是否存在
        return jsonify({'code': 200, 'message': '如果该邮箱已注册，重置申请已提交，请等待管理员处理'}), 200

    # 检查是否有待处理的申请
    existing = PasswordResetRequest.query.filter_by(user_id=user.id, status='pending').first()
    if existing:
        return jsonify({'code': 200, 'message': '您已有待处理的重置申请，请耐心等待管理员审核'}), 200

    try:
        req = PasswordResetRequest(user_id=user.id)
        db.session.add(req)
        db.session.commit()
        return jsonify({'code': 200, 'message': '重置申请已提交，管理员审核通过后您将可以设置新密码'}), 200
    except Exception:
        db.session.rollback()
        current_app.logger.error('提交密码重置申请失败')
        return jsonify({'code': 500, 'message': '提交失败，请稍后再试'}), 500