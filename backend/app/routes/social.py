from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Friend, Message, Follow
from ..extensions import db, socketio
from sqlalchemy import or_, and_, case, func
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

social_bp = Blueprint('social', __name__)

MAX_MSG_LEN = 2000
MAX_SEARCH_LEN = 120


def _int_identity() -> int:
    """统一将 JWT identity 转为 int"""
    return int(get_jwt_identity())


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
        if int(current_user_id) == user_id:
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


# 2. 搜索用户（参数化查询防注入）
@social_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    query = (request.args.get('q') or '').strip()
    if not query:
        return jsonify({'code': 400, 'message': '请输入邮箱'}), 400
    if len(query) > MAX_SEARCH_LEN:
        return jsonify({'code': 400, 'message': '搜索词过长'}), 400

    user = User.query.filter(User.email.ilike(f'%{query}%')).first()
    if not user:
        return jsonify({'code': 404, 'message': '未找到该用户'}), 404

    return jsonify({'code': 200, 'data': user.to_dict()}), 200


# 3. 发起好友请求（双向防重复）
@social_bp.route('/friend/request', methods=['POST'])
@jwt_required()
def add_friend():
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    target_id = data.get('user_id')
    current_id = _int_identity()

    if not target_id:
        return jsonify({'code': 400, 'message': '缺少目标用户ID'}), 400
    if int(target_id) == current_id:
        return jsonify({'code': 400, 'message': '不能加自己'}), 400

    # 双向检查：A→B 或 B→A 已存在
    existing = Friend.query.filter(
        or_(
            and_(Friend.user_id == current_id, Friend.friend_id == target_id),
            and_(Friend.user_id == target_id, Friend.friend_id == current_id)
        )
    ).first()
    if existing:
        if existing.status == 'accepted':
            return jsonify({'code': 400, 'message': '已经是好友了'}), 400
        return jsonify({'code': 400, 'message': '已申请或已被申请'}), 400

    try:
        new_friend = Friend(user_id=current_id, friend_id=target_id, status='pending')
        db.session.add(new_friend)
        db.session.commit()
        socketio.emit('friend_request', {'count': 1}, room=f"user_{target_id}")
        return jsonify({'code': 200, 'message': '好友申请已发送'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('发送好友申请失败')
        return jsonify({'code': 500, 'message': '操作失败'}), 500


# 4. 获取好友列表（批量查询最后消息，避免 N+1）
@social_bp.route('/friends', methods=['GET'])
@jwt_required()
def get_friends():
    current_id = _int_identity()

    friends_rel = Friend.query.filter(
        or_(Friend.user_id == current_id, Friend.friend_id == current_id),
        Friend.status == 'accepted'
    ).all()

    # 收集好友 ID
    friend_ids = []
    for rel in friends_rel:
        if int(rel.user_id) == current_id:
            friend_ids.append(rel.friend_id)
        else:
            friend_ids.append(rel.user_id)

    if not friend_ids:
        return jsonify({'code': 200, 'data': []}), 200

    # 批量查询好友用户
    friend_users = {u.id: u for u in User.query.filter(User.id.in_(friend_ids)).all()}

    # 使用窗口函数获取每个对话的最后一条消息
    pair_low = case(
        (Message.sender_id < Message.receiver_id, Message.sender_id),
        else_=Message.receiver_id
    )
    pair_high = case(
        (Message.sender_id < Message.receiver_id, Message.receiver_id),
        else_=Message.sender_id
    )

    subq = db.session.query(
        Message.id,
        Message.sender_id,
        Message.receiver_id,
        Message.body,
        Message.timestamp,
        func.row_number().over(
            partition_by=(pair_low, pair_high),
            order_by=Message.timestamp.desc()
        ).label('rn')
    ).filter(
        or_(
            and_(Message.sender_id == current_id, Message.receiver_id.in_(friend_ids)),
            and_(Message.sender_id.in_(friend_ids), Message.receiver_id == current_id)
        )
    ).subquery()

    last_msgs_raw = db.session.query(
        subq.c.sender_id, subq.c.receiver_id, subq.c.body, subq.c.timestamp
    ).filter(subq.c.rn == 1).all()

    # 按 friend_id 组织
    last_msgs = {}
    for row in last_msgs_raw:
        partner_id = row.receiver_id if row.sender_id == current_id else row.sender_id
        last_msgs[partner_id] = {'body': row.body, 'timestamp': row.timestamp}

    # 未读数：一次 GROUP BY 查询
    unread_rows = (
        db.session.query(Message.sender_id, func.count(Message.id))
        .filter(
            Message.sender_id.in_(friend_ids),
            Message.receiver_id == current_id,
            Message.is_read.is_(False)
        )
        .group_by(Message.sender_id)
        .all()
    )
    unread_counts = {row[0]: row[1] for row in unread_rows}

    friend_list = []
    for fid in friend_ids:
        friend_user = friend_users.get(fid)
        if not friend_user:
            continue

        last_msg = last_msgs.get(fid)
        unread = unread_counts.get(fid, 0)

        is_online = False
        if friend_user.last_seen:
            last_seen_utc = friend_user.last_seen.replace(tzinfo=timezone.utc) if friend_user.last_seen.tzinfo is None else friend_user.last_seen
            diff = datetime.now(timezone.utc) - last_seen_utc
            if diff.total_seconds() < 300:
                is_online = True

        friend_list.append({
            'id': friend_user.id,
            'username': friend_user.username,
            'avatar': friend_user.avatar,
            'is_online': is_online,
            'last_msg': last_msg['body'] if last_msg else '',
            'last_msg_time': last_msg['timestamp'].isoformat() + 'Z' if last_msg else None,
            'unread_count': unread
        })

    return jsonify({'code': 200, 'data': friend_list}), 200


# 5. 获取好友申请
@social_bp.route('/friend/requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    current_id = get_jwt_identity()
    reqs = Friend.query.filter_by(friend_id=current_id, status='pending').all()

    # 批量查询申请人信息，避免 N+1
    requester_ids = [r.user_id for r in reqs]
    requesters = {u.id: u for u in User.query.filter(User.id.in_(requester_ids)).all()} if requester_ids else {}

    data = []
    for r in reqs:
        u = requesters.get(r.user_id)
        if not u:
            continue
        data.append({
            'request_id': r.id,
            'user_id': u.id,
            'username': u.username,
            'avatar': u.avatar,
            'timestamp': r.timestamp.isoformat() + 'Z'
        })
    return jsonify({'code': 200, 'data': data}), 200


# 6. 处理好友申请
@social_bp.route('/friend/respond', methods=['POST'])
@jwt_required()
def respond_friend():
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    req_id = data.get('request_id')
    action = data.get('action')

    if not req_id or not action:
        return jsonify({'code': 400, 'message': '缺少必要参数'}), 400

    current_user_id = _int_identity()
    freq = Friend.query.get(req_id)

    if not freq:
        return jsonify({'code': 404, 'message': '请求不存在'}), 404

    if int(freq.friend_id) != current_user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    try:
        if action == 'accept':
            freq.status = 'accepted'
            db.session.commit()
            socketio.emit('friend_accepted', {'friend_id': freq.friend_id}, room=f"user_{freq.user_id}")
            return jsonify({'code': 200, 'message': '已添加好友'}), 200
        else:
            db.session.delete(freq)
            db.session.commit()
            return jsonify({'code': 200, 'message': '已拒绝'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('处理好友申请失败')
        return jsonify({'code': 500, 'message': '操作失败'}), 500


# 7. 发送私信 (存库)
@social_bp.route('/message/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    receiver_id = data.get('receiver_id')
    body = (data.get('body') or '').strip()

    if not receiver_id:
        return jsonify({'code': 400, 'message': '缺少接收者'}), 400
    if not body:
        return jsonify({'code': 400, 'message': '内容为空'}), 400
    if len(body) > MAX_MSG_LEN:
        return jsonify({'code': 400, 'message': f'消息不能超过{MAX_MSG_LEN}个字符'}), 400

    # 验证接收者存在
    if not User.query.get(receiver_id):
        return jsonify({'code': 404, 'message': '接收者不存在'}), 404

    try:
        msg = Message(sender_id=_int_identity(), receiver_id=receiver_id, body=body)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'code': 200, 'message': '发送成功', 'data': msg.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('发送私信失败')
        return jsonify({'code': 500, 'message': '发送失败'}), 500


# 8. 标记已读
@social_bp.route('/message/read', methods=['POST'])
@jwt_required()
def mark_read():
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    partner_id = data.get('partner_id')
    if not partner_id:
        return jsonify({'code': 400, 'message': '缺少对方用户ID'}), 400

    current_id = _int_identity()
    try:
        Message.query.filter_by(sender_id=partner_id, receiver_id=current_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({'code': 200, 'message': 'ok'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('标记已读失败')
        return jsonify({'code': 500, 'message': '操作失败'}), 500


# 9. 获取聊天记录
@social_bp.route('/messages/<int:partner_id>', methods=['GET'])
@jwt_required()
def get_chat_history(partner_id):
    current_id = _int_identity()
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_id, Message.receiver_id == partner_id),
            and_(Message.sender_id == partner_id, Message.receiver_id == current_id)
        )
    ).order_by(Message.timestamp.asc()).all()

    return jsonify({'code': 200, 'data': [m.to_dict() for m in messages]}), 200


# ==========================================
# 10. 关注 / 取关
# ==========================================
@social_bp.route('/follow/<int:user_id>', methods=['POST'])
@jwt_required()
def toggle_follow(user_id):
    current_id = _int_identity()
    if current_id == user_id:
        return jsonify({'code': 400, 'message': '不能关注自己'}), 400

    try:
        existing = Follow.query.filter_by(follower_id=current_id, followed_id=user_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({'code': 200, 'message': '已取关', 'following': False}), 200
        else:
            db.session.add(Follow(follower_id=current_id, followed_id=user_id))
            db.session.commit()
            return jsonify({'code': 200, 'message': '已关注', 'following': True}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('关注操作失败')
        return jsonify({'code': 500, 'message': '操作失败'}), 500


@social_bp.route('/follow/<int:user_id>', methods=['GET'])
@jwt_required(optional=True)
def check_follow(user_id):
    followers = Follow.query.filter_by(followed_id=user_id).count()
    following = Follow.query.filter_by(follower_id=user_id).count()
    is_following = False
    try:
        current_id = get_jwt_identity()
        if current_id:
            is_following = Follow.query.filter_by(follower_id=int(current_id), followed_id=user_id).first() is not None
    except Exception:
        pass
    return jsonify({'code': 200, 'data': {
        'followers': followers,
        'following': following,
        'is_following': is_following
    }}), 200
