from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User
from flask_jwt_extended import create_access_token
from datetime import timedelta
import re

auth_bp = Blueprint('auth', __name__)

# 邮箱正则
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = (data.get('email') or '').strip()
    nickname = (data.get('nickname') or '').strip()
    password = data.get('password') or ''

    # 验证邮箱
    if not email or not EMAIL_REGEX.match(email):
        return jsonify({'code': 400, 'message': '请输入有效的邮箱地址'}), 200

    # 验证昵称
    if not nickname or len(nickname) < 2:
        return jsonify({'code': 400, 'message': '昵称至少需要2个字符'}), 200
    if len(nickname) > 32:
        return jsonify({'code': 400, 'message': '昵称不能超过32个字符'}), 200

    # 验证密码
    if not password or len(password) < 6:
        return jsonify({'code': 400, 'message': '密码至少需要6个字符'}), 200

    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'message': '邮箱已存在'}), 200

    if User.query.filter_by(username=nickname).first():
        return jsonify({'code': 400, 'message': '昵称已被占用'}), 200

    user = User(username=nickname, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'code': 200, 'message': '注册成功'}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'code': 400, 'message': '请输入邮箱和密码'}), 200

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'code': 401, 'message': '账号或密码错误'}), 200

    token = create_access_token(identity=str(user.id))
    return jsonify({'code': 200, 'message': '登录成功', 'access_token': token, 'user': user.to_dict()}), 200


# ==========================================
# 邮箱验证 (简化版：注册时发送验证token到控制台)
# ==========================================
@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    email = (data.get('email') or '').strip()
    token = data.get('token') or ''

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 200

    # 简化：用 JWT 作为验证 token
    try:
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        if str(decoded.get('sub')) == str(user.id) and decoded.get('type') == 'email_verify':
            user.email_verified = True
            db.session.commit()
            return jsonify({'code': 200, 'message': '邮箱验证成功！'}), 200
    except Exception:
        return jsonify({'code': 400, 'message': '验证链接无效或已过期'}), 200

    return jsonify({'code': 400, 'message': '验证失败'}), 200


# ==========================================
# 忘记密码 — 发送重置链接
# ==========================================
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = (data.get('email') or '').strip()
    if not email:
        return jsonify({'code': 400, 'message': '请输入邮箱'}), 200

    user = User.query.filter_by(email=email).first()
    if not user:
        # 不暴露用户是否存在
        return jsonify({'code': 200, 'message': '如果该邮箱已注册，重置链接已发送'}), 200

    # 生成重置 token (有效期30分钟)
    from flask_jwt_extended import create_access_token
    reset_token = create_access_token(
        identity=str(user.id),
        additional_claims={'type': 'password_reset'},
        expires_delta=timedelta(minutes=30)
    )

    # 生产环境应发送邮件，这里打印到控制台供开发测试
    print(f"\n{'='*60}")
    print(f"密码重置链接 (开发模式):")
    print(f"  邮箱: {email}")
    print(f"  Token: {reset_token}")
    print(f"  POST /auth/reset-password  body: {{email:'{email}', token:'{reset_token}', password:'newpass123'}}")
    print(f"{'='*60}\n")

    return jsonify({'code': 200, 'message': '如果该邮箱已注册，重置链接已发送', 'debug_token': reset_token}), 200


# ==========================================
# 重置密码
# ==========================================
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = (data.get('email') or '').strip()
    token = data.get('token') or ''
    new_password = data.get('password') or ''

    if not new_password or len(new_password) < 6:
        return jsonify({'code': 400, 'message': '新密码至少需要6个字符'}), 200

    try:
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        if decoded.get('type') != 'password_reset':
            return jsonify({'code': 400, 'message': '无效的重置链接'}), 200

        user = User.query.filter_by(id=decoded['sub'], email=email).first()
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 200

        user.set_password(new_password)
        db.session.commit()
        return jsonify({'code': 200, 'message': '密码重置成功，请重新登录'}), 200
    except Exception as e:
        return jsonify({'code': 400, 'message': '重置链接无效或已过期'}), 200