import re
from datetime import datetime, timezone
from typing import Optional

from flask import request
from flask_jwt_extended import decode_token
from flask import current_app
from .extensions import socketio, db
from .models import Message, User, Friend

# ── SocketIO 鉴权工具 ──

# sid → user_id 映射表（避免每次 decode_token）
_sid_user_map: dict[str, int] = {}


def _verify_socket_token() -> Optional[int]:
    """从请求参数中验证 JWT，返回 user_id 或 None"""
    token = request.args.get('token')
    if not token:
        return None
    try:
        decoded = decode_token(token)
        exp = decoded.get('exp')
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            return None
        user_id = decoded['sub']
        return int(user_id) if isinstance(user_id, str) else user_id
    except Exception:
        return None


@socketio.on('connect')
def handle_connect() -> bool:
    user_id = _verify_socket_token()
    if not user_id:
        return False  # 拒绝连接

    # 存入映射表
    _sid_user_map[request.sid] = user_id
    from flask_socketio import join_room
    join_room(f"user_{user_id}")
    current_app.logger.info('SocketIO: User %s connected (sid=%s)', user_id, request.sid)
    return True


@socketio.on('disconnect')
def handle_disconnect() -> None:
    _sid_user_map.pop(request.sid, None)


@socketio.on('send_message')
def handle_send_message(data: dict) -> None:
    # 优先从映射表获取，避免重复 decode
    user_id = _sid_user_map.get(request.sid)
    if not user_id:
        user_id = _verify_socket_token()
    if not user_id:
        return

    receiver_id = data.get('receiver_id')
    body = data.get('body', '').strip()

    if not body or not receiver_id:
        return

    # 输入长度限制
    if len(body) > 2000:
        return

    # 存入数据库
    msg = Message(sender_id=user_id, receiver_id=receiver_id, body=body)
    db.session.add(msg)
    db.session.commit()

    # 实时推送
    socketio.emit('new_message', msg.to_dict(), room=f"user_{receiver_id}")
    socketio.emit('new_message', msg.to_dict(), room=f"user_{user_id}")


def send_friend_request_notification(receiver_id: int) -> None:
    """推送好友申请通知"""
    socketio.emit('friend_request', {'msg': '你有新的好友申请'}, room=f"user_{receiver_id}")