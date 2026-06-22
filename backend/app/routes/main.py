import os
import uuid
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Post, User, Category
from datetime import datetime, timedelta, timezone

main_bp = Blueprint('main', __name__)

# ==========================================
# 0. 配置与工具函数
# ==========================================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================================
# 1. 文件上传接口 (头像/图片)
# ==========================================
@main_bp.route('/upload', methods=['POST'])
@jwt_required()
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
        # 读取文件头验证真实类型（防止伪造扩展名）
        file.seek(0)
        header = file.read(8)
        file.seek(0)
        valid_headers = {
            b'\x89PNG\r\n\x1a\n': 'png',
            b'\xff\xd8\xff': 'jpeg',
            b'GIF87a': 'gif',
            b'GIF89a': 'gif',
            b'RIFF': 'webp',
        }
        is_valid = False
        for magic, _ in valid_headers.items():
            if header.startswith(magic):
                is_valid = True
                break
        if not is_valid:
            return jsonify({'code': 400, 'message': '文件内容与扩展名不匹配'}), 400

        # 检查文件大小（先读到内存判断大小）
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'code': 400, 'message': f'文件过大，最大允许 {MAX_FILE_SIZE // (1024 * 1024)}MB'}), 400

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
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_posts = Post.query.filter(Post.timestamp >= today_start).count()

    # 3. 在线猫猫 (在线人数)
    # 修改为：过去 5 分钟内有过活动的用户 (更实时)
    active_threshold = datetime.now(timezone.utc) - timedelta(minutes=5)
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
# 5. GIF 搜索代理 (多源: Giphy / Tenor / 免费内置)
# ==========================================
import requests

GIPHY_API_KEY = os.environ.get('GIPHY_API_KEY')
TENOR_API_KEY = os.environ.get('TENOR_API_KEY')  # 免费申请: https://tenor.com/developer

# 内置免费表情包 (无需任何 API Key)
FREE_GIFS = [
    {"id": "free_001", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/JIX9t2j0ZTN9S/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif"}}},
    {"id": "free_002", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/8Iv5lqKwKsZ2g/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/8Iv5lqKwKsZ2g/giphy.gif"}}},
    {"id": "free_003", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/mlvseq9yvZhba/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/mlvseq9yvZhba/giphy.gif"}}},
    {"id": "free_004", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/13CoXDiaCcCoyk/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/13CoXDiaCcCoyk/giphy.gif"}}},
    {"id": "free_005", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/GeimqsH0TLDt4tScGw/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/GeimqsH0TLDt4tScGw/giphy.gif"}}},
    {"id": "free_006", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif"}}},
    {"id": "free_007", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/l0HlNQ03J5JxX6lva/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif"}}},
    {"id": "free_008", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/26ufdipQqU2lhNA4g/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif"}}},
    {"id": "free_009", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/xT0GqssRweIlyz3i4E/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/xT0GqssRweIlyz3i4E/giphy.gif"}}},
    {"id": "free_010", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/3orieLHrJOlQHcMvIs/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/3orieLHrJOlQHcMvIs/giphy.gif"}}},
    {"id": "free_011", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/3o7TKuY6Z8FkPQMh7i/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/3o7TKuY6Z8FkPQMh7i/giphy.gif"}}},
    {"id": "free_012", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/XbOkpDQ2dx8GL80JMI/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/XbOkpDQ2dx8GL80JMI/giphy.gif"}}},
    {"id": "free_013", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/11sBLVxNs7v6WA/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/11sBLVxNs7v6WA/giphy.gif"}}},
    {"id": "free_014", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif"}}},
    {"id": "free_015", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/5VKbvrjxpVJCM/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif"}}},
    {"id": "free_016", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif"}}},
    {"id": "free_017", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/kaq6Gnx1cf4IM/giphy.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/kaq6Gnx1cf4IM/giphy.gif"}}},
    {"id": "free_018", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/dkGhBWE3SyzXW/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/dkGhBWE3SyzXW/giphy.gif"}}},
    {"id": "free_019", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/l3q2K5jinAlChoCLS/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif"}}},
    {"id": "free_020", "images": {"fixed_height_small": {"url": "https://media.giphy.com/media/xT9DPldJHzZKtORo2A/200w.gif"}, "fixed_height": {"url": "https://media.giphy.com/media/xT9DPldJHzZKtORo2A/giphy.gif"}}},
]

@main_bp.route('/gifs', methods=['GET'])
def proxy_gifs():
    query = (request.args.get('q', 'reaction') or '').strip()
    limit = request.args.get('limit', 20, type=int)

    # 1. 优先 Giphy (如果有 Key)
    if GIPHY_API_KEY:
        try:
            resp = requests.get(
                'https://api.giphy.com/v1/gifs/search',
                params={'api_key': GIPHY_API_KEY, 'q': query, 'limit': limit, 'rating': 'g'},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json().get('data', [])
                if data:
                    return jsonify({'code': 200, 'data': data, 'source': 'giphy'}), 200
        except Exception:
            pass

    # 2. 尝试 Tenor (免费 API, 每天 10,000 次)
    if TENOR_API_KEY:
        try:
            resp = requests.get(
                'https://tenor.googleapis.com/v2/search',
                params={'key': TENOR_API_KEY, 'q': query, 'limit': limit, 'media_filter': 'gif,tinygif'},
                timeout=5
            )
            if resp.status_code == 200:
                results = resp.json().get('results', [])
                data = []
                for r in results:
                    media = r.get('media_formats', {}).get('gif', {})
                    tiny = r.get('media_formats', {}).get('tinygif', {})
                    data.append({
                        'id': r.get('id'),
                        'images': {
                            'fixed_height_small': {'url': tiny.get('url', media.get('url', ''))},
                            'fixed_height': {'url': media.get('url', '')}
                        }
                    })
                if data:
                    return jsonify({'code': 200, 'data': data, 'source': 'tenor'}), 200
        except Exception:
            pass

    # 3. 兜底: 内置免费表情包 (按 query 简单筛选)
    import random
    rng = random.Random(query if query else 'cat')
    result = FREE_GIFS.copy()
    rng.shuffle(result)
    return jsonify({'code': 200, 'data': result[:limit], 'source': 'builtin'}), 200
@main_bp.route('/promotions', methods=['GET'])
def promotions():
    return jsonify({'code': 200, 'data': [
        {'id': 1, 'title': '🔥 哈基米大促', 'link': '/vip'},
        {'id': 2, 'title': '📢 社区指南', 'link': '/about'}
    ]}), 200