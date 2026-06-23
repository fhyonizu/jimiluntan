from flask import Blueprint, request, jsonify, current_app
from ..extensions import db, cache
from ..models import Post, User, Category, Comment, PostLike
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from sqlalchemy.orm import joinedload

posts_bp = Blueprint('posts', __name__)

MAX_PER_PAGE = 50
MAX_TITLE_LEN = 128
MAX_BODY_LEN = 10000
MAX_COMMENT_LEN = 2000


@posts_bp.route('/', methods=['GET'])
def get_posts():
    sort_by = request.args.get('sort', 'latest')
    category_id = request.args.get('category_id')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), MAX_PER_PAGE)

    query = Post.query.options(joinedload(Post.author), joinedload(Post.category))
    if category_id:
        query = query.filter_by(category_id=category_id)

    if sort_by == 'hot':
        query = query.order_by(Post.views.desc())
    else:
        query = query.order_by(Post.timestamp.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items

    # 批量查询 likes count（避免 N+1）
    post_ids = [p.id for p in posts]
    likes_map = {}
    if post_ids:
        rows = db.session.query(PostLike.post_id, func.count(PostLike.id)) \
            .filter(PostLike.post_id.in_(post_ids)) \
            .group_by(PostLike.post_id).all()
        likes_map = {r[0]: r[1] for r in rows}

    # 注入 likes count
    for p in posts:
        p._likes_count = likes_map.get(p.id, 0)

    return jsonify({
        'code': 200,
        'data': [post.to_dict() for post in posts],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    post = Post.query.options(joinedload(Post.author), joinedload(Post.category)).filter_by(id=post_id).first()
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    # 浏览量防刷：同一 IP + post_id 60 秒内只计一次
    client_ip = request.remote_addr or 'unknown'
    view_cache_key = f"view:{post_id}:{client_ip}"
    if not cache.get(view_cache_key):
        post.views += 1
        db.session.commit()
        cache.set(view_cache_key, True, timeout=60)

    comments = Comment.query.filter_by(post_id=post_id) \
        .options(joinedload(Comment.author)) \
        .order_by(Comment.timestamp.asc()).all()

    # 单帖 likes
    likes = PostLike.query.filter_by(post_id=post_id).count()
    post._likes_count = likes

    post_data = post.to_dict()
    post_data['comments'] = [c.to_dict() for c in comments]
    return jsonify({'code': 200, 'data': post_data}), 200


@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user or (post.user_id != current_user_id and user.role != 'admin'):
        return jsonify({'code': 403, 'message': '无权编辑此帖子'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    title = (data.get('title') or '').strip()
    body = (data.get('body') or '').strip()

    if not title or not body:
        return jsonify({'code': 400, 'message': '标题和内容不能为空'}), 400
    if len(title) > MAX_TITLE_LEN:
        return jsonify({'code': 400, 'message': f'标题不能超过{MAX_TITLE_LEN}个字符'}), 400
    if len(body) > MAX_BODY_LEN:
        return jsonify({'code': 400, 'message': f'内容不能超过{MAX_BODY_LEN}个字符'}), 400

    post.title = title
    post.body = body
    if 'tags' in data:
        tags = data['tags']
        if not isinstance(tags, list):
            tags = []
        post.tags = ','.join(str(t)[:50] for t in tags)
    if 'category_id' in data:
        post.category_id = data['category_id']

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '更新成功', 'data': post.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('更新帖子失败')
        return jsonify({'code': 500, 'message': '更新失败'}), 500


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user or (post.user_id != current_user_id and user.role != 'admin'):
        return jsonify({'code': 403, 'message': '无权删除此帖子'}), 403

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'code': 200, 'message': '帖子已删除'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('删除帖子失败')
        return jsonify({'code': 500, 'message': '删除失败'}), 500


@posts_bp.route('/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    body = (data.get('body') or '').strip()
    if not body:
        return jsonify({'code': 400, 'message': '不能发空评论哦'}), 400
    if len(body) > MAX_COMMENT_LEN:
        return jsonify({'code': 400, 'message': f'评论不能超过{MAX_COMMENT_LEN}个字符'}), 400

    new_comment = Comment(body=body, post_id=post_id, user_id=get_jwt_identity())
    try:
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'code': 200, 'message': '评论成功！', 'data': new_comment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('添加评论失败')
        return jsonify({'code': 500, 'message': '评论失败'}), 500


# ==========================================
# 评论编辑 + 删除
# ==========================================

@posts_bp.route('/<int:post_id>/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def edit_comment(post_id, comment_id):
    comment = Comment.query.filter_by(id=comment_id, post_id=post_id).first()
    if not comment:
        return jsonify({'code': 404, 'message': '评论不存在'}), 404

    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user or (comment.user_id != current_user_id and user.role != 'admin'):
        return jsonify({'code': 403, 'message': '无权编辑此评论'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    body = (data.get('body') or '').strip()
    if not body:
        return jsonify({'code': 400, 'message': '不能发空评论哦'}), 400
    if len(body) > MAX_COMMENT_LEN:
        return jsonify({'code': 400, 'message': f'评论不能超过{MAX_COMMENT_LEN}个字符'}), 400

    comment.body = body
    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '评论已更新', 'data': comment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('更新评论失败')
        return jsonify({'code': 500, 'message': '更新失败'}), 500


@posts_bp.route('/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(post_id, comment_id):
    comment = Comment.query.filter_by(id=comment_id, post_id=post_id).first()
    if not comment:
        return jsonify({'code': 404, 'message': '评论不存在'}), 404

    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user or (comment.user_id != current_user_id and user.role != 'admin'):
        return jsonify({'code': 403, 'message': '无权删除此评论'}), 403

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'code': 200, 'message': '评论已删除'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('删除评论失败')
        return jsonify({'code': 500, 'message': '删除失败'}), 500


# ==========================================
# 搜索帖子（参数化查询防 SQL 注入）
# ==========================================

@posts_bp.route('/search', methods=['GET'])
def search_posts():
    q = (request.args.get('q') or '').strip()
    if not q or len(q) < 2:
        return jsonify({'code': 400, 'message': '搜索词太短'}), 400

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), MAX_PER_PAGE)

    # 安全的参数化 LIKE 查询
    like_pattern = f'%{q}%'
    query = Post.query.options(joinedload(Post.author), joinedload(Post.category)) \
        .filter(Post.title.ilike(like_pattern) | Post.body.ilike(like_pattern)) \
        .order_by(Post.timestamp.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # 批量 likes
    post_ids = [p.id for p in pagination.items]
    likes_map = {}
    if post_ids:
        rows = db.session.query(PostLike.post_id, func.count(PostLike.id)) \
            .filter(PostLike.post_id.in_(post_ids)) \
            .group_by(PostLike.post_id).all()
        likes_map = {r[0]: r[1] for r in rows}
    for p in pagination.items:
        p._likes_count = likes_map.get(p.id, 0)

    return jsonify({
        'code': 200,
        'data': [post.to_dict() for post in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages
    }), 200


# ==========================================
# 帖子点赞/取消点赞
# ==========================================

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@jwt_required()
def toggle_like(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    current_user_id = get_jwt_identity()
    existing = PostLike.query.filter_by(user_id=current_user_id, post_id=post_id).first()
    try:
        if existing:
            db.session.delete(existing)
            db.session.commit()
            count = PostLike.query.filter_by(post_id=post_id).count()
            return jsonify({'code': 200, 'message': '已取消点赞', 'liked': False, 'count': count}), 200
        else:
            db.session.add(PostLike(user_id=current_user_id, post_id=post_id))
            db.session.commit()
            count = PostLike.query.filter_by(post_id=post_id).count()
            return jsonify({'code': 200, 'message': '已点赞', 'liked': True, 'count': count}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('点赞操作失败')
        return jsonify({'code': 500, 'message': '操作失败'}), 500


@posts_bp.route('/<int:post_id>/like', methods=['GET'])
def get_likes(post_id):
    count = PostLike.query.filter_by(post_id=post_id).count()
    liked = False
    try:
        current_user_id = get_jwt_identity()
        if current_user_id:
            liked = PostLike.query.filter_by(user_id=current_user_id, post_id=post_id).first() is not None
    except Exception:
        pass
    return jsonify({'code': 200, 'data': {'count': count, 'liked': liked}}), 200


# ==========================================
# 发布帖子
# ==========================================

@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    title = (data.get('title') or '').strip()
    body = (data.get('body') or '').strip()
    category_id = data.get('category_id')

    if not title or not body:
        return jsonify({'code': 400, 'message': '标题和内容不能为空'}), 400
    if len(title) > MAX_TITLE_LEN:
        return jsonify({'code': 400, 'message': f'标题不能超过{MAX_TITLE_LEN}个字符'}), 400
    if len(body) > MAX_BODY_LEN:
        return jsonify({'code': 400, 'message': f'内容不能超过{MAX_BODY_LEN}个字符'}), 400

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'code': 401, 'message': '用户身份无效，请重新登录'}), 401

    # 公告栏权限检查
    category = Category.query.get(category_id)
    if category and category.name == '公告栏':
        if user.role != 'admin':
            return jsonify({'code': 403, 'message': '仅管理员可发布公告'}), 403

    tags = data.get('tags')
    if not isinstance(tags, list):
        tags = []
    tags_str = ",".join(str(t)[:50] for t in tags)

    new_post = Post(
        title=title,
        body=body,
        user_id=current_user_id,
        category_id=category_id,
        tags=tags_str
    )

    try:
        db.session.add(new_post)
        db.session.commit()
        return jsonify({'code': 200, 'message': '发布成功', 'data': new_post.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('创建帖子失败')
        return jsonify({'code': 500, 'message': '发布失败'}), 500


@posts_bp.route('/categories', methods=['GET'])
@cache.cached(timeout=120)
def get_categories():
    cats = Category.query.all()
    return jsonify({
        'code': 200,
        'data': [{'id': c.id, 'name': c.name, 'icon': c.icon} for c in cats]
    }), 200