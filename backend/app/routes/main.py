import os
import uuid
from flask import Blueprint, jsonify, request, current_app
from ..models import Post, User, Category
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

# ==========================================
# 0. 配置与工具函数
# ==========================================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================================
# 1. 文件上传接口 (头像/图片)
# ==========================================
@main_bp.route('/upload', methods=['POST'])
def upload_file():
    # 1. 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未检测到文件'}), 400

    file = request.files['file']

    # 2. 检查文件名是否为空
    if file.filename == '':
        return jsonify({'code': 400, 'message': '未选择文件'}), 400

    # 3. 校验格式并保存
    if file and allowed_file(file.filename):
        # 生成唯一文件名 (uuid + 原后缀)
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"

        # 确保 static/uploads 目录存在
        # current_app.root_path 指向 backend 文件夹
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # 保存文件
        file.save(os.path.join(upload_folder, filename))

        # 返回相对路径 URL (前端需拼接 baseURL)
        file_url = f"/static/uploads/{filename}"

        return jsonify({
            'code': 200,
            'message': '上传成功',
            'url': file_url
        }), 200

    return jsonify({'code': 400, 'message': '不支持的文件格式'}), 400


# ==========================================
# 2. 全站统计数据 (罐头/投喂/在线)
# ==========================================
@main_bp.route('/stats', methods=['GET'])
def get_site_stats():
    # 1. 罐头储存 (总帖子数)
    total_posts = Post.query.count()

    # 2. 今日投喂 (今日发布数)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_posts = Post.query.filter(Post.timestamp >= today_start).count()

    # 3. 在线猫猫 (在线人数)
    # 修改为：过去 5 分钟内有过活动的用户 (更实时)
    active_threshold = datetime.utcnow() - timedelta(minutes=5)
    online_users = User.query.filter(User.last_seen >= active_threshold).count()

    # 修正：如果显示为0 (可能你自己刚登陆还没刷新 last_seen)，至少显示1
    if online_users == 0:
        online_users = 1

    return jsonify({
        'code': 200,
        'data': {
            'total_posts': total_posts,
            'today_posts': today_posts,
            'online_users': online_users
        }
    })


# ==========================================
# 3. 管理员通知 (获取“公告栏”分区的帖子)
# ==========================================
@main_bp.route('/notices', methods=['GET'])
def get_notices():
    notice_cat = Category.query.filter_by(name='公告栏').first()

    if not notice_cat:
        return jsonify({'code': 200, 'data': []})

    # 获取该分区下最新的 5 条帖子
    notices = Post.query.filter_by(category_id=notice_cat.id) \
        .order_by(Post.timestamp.desc()) \
        .limit(5).all()

    data = []
    for p in notices:
        data.append({
            'id': p.id,
            'title': p.title,
            'time': p.timestamp.isoformat() + 'Z'
        })

    return jsonify({'code': 200, 'data': data})


# ==========================================
# 4. (保留) 推广/广告位接口
# ==========================================
@main_bp.route('/promotions', methods=['GET'])
def promotions():
    return jsonify({'code': 200, 'data': [
        {'id': 1, 'title': '🔥 哈基米大促', 'link': '/vip'},
        {'id': 2, 'title': '📢 社区指南', 'link': '/about'}
    ]}), 200