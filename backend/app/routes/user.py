from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models import User
from ..routes.auth import MAX_NICKNAME, MIN_PASSWORD
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__)

MAX_ABOUT = 500


# ==========================================
# 获取当前用户信息
# ==========================================
@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    return jsonify({'code': 200, 'data': user.to_dict()}), 200


# ==========================================
# 修改个人资料
# ==========================================
@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    # 1. 修改昵称
    new_nickname = (data.get('nickname') or '').strip()
    if new_nickname and new_nickname != user.username:
        if len(new_nickname) < 2:
            return jsonify({'code': 400, 'message': '昵称至少需要2个字符'}), 400
        if len(new_nickname) > MAX_NICKNAME:
            return jsonify({'code': 400, 'message': f'昵称不能超过{MAX_NICKNAME}个字符'}), 400
        if User.query.filter_by(username=new_nickname).first():
            return jsonify({'code': 400, 'message': '这个昵称太受欢迎了，换一个吧'}), 400
        user.username = new_nickname

    # 2. 修改简介
    if 'about_me' in data:
        about = (data['about_me'] or '')[:MAX_ABOUT]
        user.about_me = about

    # 3. 修改头像
    if 'avatar' in data:
        user.avatar = (data['avatar'] or '')[:256]

    # 4. 修改密码
    if 'password' in data and data['password']:
        if len(data['password']) < MIN_PASSWORD:
            return jsonify({'code': 400, 'message': f'新密码至少需要{MIN_PASSWORD}个字符'}), 400
        user.set_password(data['password'])

    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '资料更新成功！',
            'data': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('更新用户资料失败')
        return jsonify({'code': 500, 'message': '更新失败'}), 500