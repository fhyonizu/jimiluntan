from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__)


# ==========================================
# 修改个人资料 (昵称、简介、头像URL)
# ==========================================
@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()

    # 1. 修改昵称 (需要检查查重)
    new_nickname = data.get('nickname')
    if new_nickname and new_nickname != user.username:
        if User.query.filter_by(username=new_nickname).first():
            return jsonify({'code': 400, 'message': '这个昵称太受欢迎了，换一个吧'}), 200
        user.username = new_nickname

    # 2. 修改简介
    if 'about_me' in data:
        user.about_me = data['about_me']

    # 3. 修改头像 (目前暂时只支持 URL 链接，后面我们做图片上传功能)
    if 'avatar' in data:
        user.avatar = data['avatar']

    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '资料更新成功！',
            'data': user.to_dict()  # 返回最新的用户信息
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500