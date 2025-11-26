from flask_socketio import emit, join_room
from flask_jwt_extended import decode_token
from .extensions import socketio, db
from .models import Message, User, Friend
from flask import request

# 鉴权：连接时验证 Token
@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if not token:
        return False # 拒绝连接
    try:
        decoded = decode_token(token)
        user_id = decoded['sub']
        # 让用户加入自己的专属房间，房间名叫 "user_{id}"
        join_room(f"user_{user_id}")
        print(f"User {user_id} connected")
    except Exception:
        return False

# 发送消息事件
@socketio.on('send_message')
def handle_send_message(data):
    # data: { receiver_id: 1, body: "Hello" }
    token = request.args.get('token')
    user_id = decode_token(token)['sub'] # 发送者 ID
    receiver_id = data.get('receiver_id')
    body = data.get('body')

    if not body or not receiver_id:
        return

    # 1. 存入数据库
    msg = Message(sender_id=user_id, receiver_id=receiver_id, body=body)
    db.session.add(msg)
    db.session.commit()

    # 2. 实时推送到接收者的房间
    # 推送给接收者
    socketio.emit('new_message', msg.to_dict(), room=f"user_{receiver_id}")
    # 推送给发送者自己（为了多端同步，或者确认发送成功）
    socketio.emit('new_message', msg.to_dict(), room=f"user_{user_id}")

# 处理好友申请通知
def send_friend_request_notification(receiver_id):
    socketio.emit('friend_request', {'msg': '你有新的好友申请'}, room=f"user_{receiver_id}")