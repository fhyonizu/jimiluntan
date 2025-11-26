from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Friend, Message
from ..extensions import db, socketio
from sqlalchemy import or_, and_

social_bp = Blueprint('social', __name__)


# 1. 获取用户信息
@social_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required(optional=True)
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = user.to_dict()
    current_user_id = get_jwt_identity()
    data['is_friend'] = False
    data['is_self'] = False

    if current_user_id:
        # 确保转成 int 比较
        if int(current_user_id) == int(user_id):
            data['is_self'] = True
        else:
            friendship = Friend.query.filter(
                or_(
                    and_(Friend.user_id == current_user_id, Friend.friend_id == user_id),
                    and_(Friend.user_id == user_id, Friend.friend_id == current_user_id)
                ),
                Friend.status == 'accepted'
            ).first()
            if friendship:
                data['is_friend'] = True

    return jsonify({'code': 200, 'data': data}), 200


# 2. 🔥 新增：搜索用户 (通过邮箱)
@social_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'code': 400, 'message': '请输入邮箱'}), 200

    # 模糊搜索邮箱
    user = User.query.filter(User.email.ilike(f"%{query}%")).first()
    if not user:
        return jsonify({'code': 404, 'message': '未找到该用户'}), 200

    return jsonify({'code': 200, 'data': user.to_dict()}), 200


# 3. 发起好友请求
@social_bp.route('/friend/request', methods=['POST'])
@jwt_required()
def add_friend():
    data = request.get_json()
    target_id = data.get('user_id')
    current_id = get_jwt_identity()

    if int(target_id) == int(current_id):
        return jsonify({'code': 400, 'message': '不能加自己'}), 200

    existing = Friend.query.filter_by(user_id=current_id, friend_id=target_id).first()
    if existing:
        return jsonify({'code': 400, 'message': '已申请或已是好友'}), 200

    new_friend = Friend(user_id=current_id, friend_id=target_id, status='pending')
    db.session.add(new_friend)
    db.session.commit()

    socketio.emit('friend_request', {'count': 1}, room=f"user_{target_id}")
    return jsonify({'code': 200, 'message': '好友申请已发送'}), 200


# 4. 🔥 修复：获取好友列表 (确保不显示自己)
@social_bp.route('/friends', methods=['GET'])
@jwt_required()
def get_friends():
    current_id = int(get_jwt_identity())

    # 查询所有相关且已通过的记录
    friends_rel = Friend.query.filter(
        or_(Friend.user_id == current_id, Friend.friend_id == current_id),
        Friend.status == 'accepted'
    ).all()

    friend_list = []
    for rel in friends_rel:
        # 🔥 逻辑核心：如果 user_id 是我，那朋友就是 friend_id；反之亦然
        if int(rel.user_id) == current_id:
            fid = rel.friend_id
        else:
            fid = rel.user_id

        friend_user = User.query.get(fid)

        if friend_user:
            # 获取最后一条消息
            last_msg = Message.query.filter(
                or_(
                    and_(Message.sender_id == current_id, Message.receiver_id == fid),
                    and_(Message.sender_id == fid, Message.receiver_id == current_id)
                )
            ).order_by(Message.timestamp.desc()).first()

            unread = Message.query.filter_by(sender_id=fid, receiver_id=current_id, is_read=False).count()

            friend_list.append({
                'id': friend_user.id,
                'username': friend_user.username,
                'avatar': friend_user.avatar,
                'is_online': friend_user.to_dict()['is_online'],
                'last_msg': last_msg.body if last_msg else '',
                'last_msg_time': last_msg.timestamp.isoformat() + 'Z' if last_msg else None,
                'unread_count': unread
            })

    return jsonify({'code': 200, 'data': friend_list})


# 5. 获取好友申请
@social_bp.route('/friend/requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    current_id = get_jwt_identity()
    # 我是被申请人
    reqs = Friend.query.filter_by(friend_id=current_id, status='pending').all()
    data = []
    for r in reqs:
        u = User.query.get(r.user_id)
        data.append({
            'request_id': r.id,
            'user_id': u.id,
            'username': u.username,
            'avatar': u.avatar,
            'timestamp': r.timestamp.isoformat() + 'Z'
        })
    return jsonify({'code': 200, 'data': data})


# 6. 处理好友申请
@social_bp.route('/friend/respond', methods=['POST'])
@jwt_required()
def respond_friend():
    data = request.get_json()
    req_id = data.get('request_id')
    action = data.get('action')

    current_user_id = get_jwt_identity()
    freq = Friend.query.get(req_id)

    if not freq:
        return jsonify({'code': 404, 'message': '请求不存在'}), 404

    # 权限检查
    if int(freq.friend_id) != int(current_user_id):
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    if action == 'accept':
        freq.status = 'accepted'
        db.session.commit()
        socketio.emit('friend_accepted', {'friend_id': freq.friend_id}, room=f"user_{freq.user_id}")
        return jsonify({'code': 200, 'message': '已添加好友'}), 200
    else:
        db.session.delete(freq)
        db.session.commit()
        return jsonify({'code': 200, 'message': '已拒绝'}), 200


# 7. 发送私信 (存库)
@social_bp.route('/message/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    body = data.get('body')

    if not body: return jsonify({'code': 400, 'message': '内容为空'}), 200

    msg = Message(sender_id=get_jwt_identity(), receiver_id=receiver_id, body=body)
    db.session.add(msg)
    db.session.commit()
    # 前端通过 socketio.emit 发送实时消息，这里只负责存库
    # 但为了保证数据 ID 一致，也可以在这里返回 msg ID
    return jsonify({'code': 200, 'message': '发送成功', 'data': msg.to_dict()}), 200


# 8. 标记已读
@social_bp.route('/message/read', methods=['POST'])
@jwt_required()
def mark_read():
    data = request.get_json()
    partner_id = data.get('partner_id')
    current_id = get_jwt_identity()

    Message.query.filter_by(sender_id=partner_id, receiver_id=current_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'code': 200, 'message': 'ok'}), 200


# 9. 获取聊天记录
@social_bp.route('/messages/<int:partner_id>', methods=['GET'])
@jwt_required()
def get_chat_history(partner_id):
    current_id = get_jwt_identity()
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_id, Message.receiver_id == partner_id),
            and_(Message.sender_id == partner_id, Message.receiver_id == current_id)
        )
    ).order_by(Message.timestamp.asc()).all()

    return jsonify({'code': 200, 'data': [m.to_dict() for m in messages]}), 200