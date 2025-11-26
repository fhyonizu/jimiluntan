from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'code': 400, 'message': '邮箱已存在'}), 200

    user = User(username=data.get('nickname'), email=data.get('email'))
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    return jsonify({'code': 200, 'message': '注册成功'}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not user.check_password(data.get('password')):
        return jsonify({'code': 401, 'message': '账号或密码错误'}), 200

    token = create_access_token(identity=str(user.id))
    return jsonify({'code': 200, 'message': '登录成功', 'access_token': token, 'user': user.to_dict()}), 200