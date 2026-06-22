from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Post, User, Category, Comment
from ..extensions import cache
from flask_jwt_extended import jwt_required, get_jwt_identity

posts_bp = Blueprint('posts', __name__)


# ... (get_posts, get_post_detail, add_comment 保持不变，省略以节省篇幅，请保留原有的) ...
# 为了方便，这里只展示修改了的 create_post 和 get_categories

@posts_bp.route('/', methods=['GET'])
def get_posts():
    sort_by = request.args.get('sort', 'latest')
    category_id = request.args.get('category_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Post.query
    if category_id:
        query = query.filter_by(category_id=category_id)

    if sort_by == 'hot':
        query = query.order_by(Post.views.desc())
    else:
        query = query.order_by(Post.timestamp.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items

    return jsonify({
        'code': 200,
        'data': [post.to_dict() for post in posts],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    post = Post.query.get(post_id)
    if not post: return jsonify({'code': 404, 'message': '帖子不存在'}), 404
    post.views += 1
    db.session.commit()
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.timestamp.asc()).all()
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
    user = User.query.get(current_user_id)
    if not user or (int(post.user_id) != int(current_user_id) and user.role != 'admin'):
        return jsonify({'code': 403, 'message': '无权编辑此帖子'}), 403

    data = request.get_json()
    title = data.get('title')
    body = data.get('body')

    if not title or not body:
        return jsonify({'code': 400, 'message': '标题和内容不能为空'}), 200

    post.title = title
    post.body = body
    if 'tags' in data:
        tags = data['tags']
        if not isinstance(tags, list):
            tags = []
        post.tags = ','.join(tags)
    if 'category_id' in data:
        post.category_id = data['category_id']

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '更新成功', 'data': post.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or (int(post.user_id) != int(current_user_id) and user.role != 'admin'):
        return jsonify({'code': 403, 'message': '无权删除此帖子'}), 403

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'code': 200, 'message': '帖子已删除'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@posts_bp.route('/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    post = Post.query.get(post_id)
    if not post: return jsonify({'code': 404, 'message': '帖子不存在'}), 404
    data = request.get_json()
    body = data.get('body')
    if not body or not body.strip(): return jsonify({'code': 400, 'message': '不能发空评论哦'}), 200
    new_comment = Comment(body=body, post_id=post_id, user_id=get_jwt_identity())
    try:
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'code': 200, 'message': '评论成功！', 'data': new_comment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


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
    user = User.query.get(current_user_id)
    if not user or (int(comment.user_id) != int(current_user_id) and user.role != 'admin'):
        return jsonify({'code': 403, 'message': '无权编辑此评论'}), 403

    data = request.get_json()
    body = data.get('body')
    if not body or not body.strip():
        return jsonify({'code': 400, 'message': '不能发空评论哦'}), 200

    comment.body = body
    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '评论已更新', 'data': comment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@posts_bp.route('/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(post_id, comment_id):
    comment = Comment.query.filter_by(id=comment_id, post_id=post_id).first()
    if not comment:
        return jsonify({'code': 404, 'message': '评论不存在'}), 404

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or (int(comment.user_id) != int(current_user_id) and user.role != 'admin'):
        return jsonify({'code': 403, 'message': '无权删除此评论'}), 403

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'code': 200, 'message': '评论已删除'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


# ==========================================
# 搜索帖子
# ==========================================

@posts_bp.route('/search', methods=['GET'])
def search_posts():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'code': 400, 'message': '搜索词太短'}), 200

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Post.query.filter(
        Post.title.ilike(f'%{q}%') | Post.body.ilike(f'%{q}%')
    ).order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': [post.to_dict() for post in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages
    }), 200


# ==========================================
# 帖子点赞/收藏
# ==========================================

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@jwt_required()
def toggle_like(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    current_user_id = get_jwt_identity()
    # 简单实现：直接增加 views（后续可建 likes 表）
    # 先检查是否已点赞
    from ..models import PostLike
    existing = PostLike.query.filter_by(user_id=current_user_id, post_id=post_id).first()
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


@posts_bp.route('/<int:post_id>/like', methods=['GET'])
def get_likes(post_id):
    from ..models import PostLike
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
# 🔥 核心修改：发布帖子接口
# ==========================================

@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    title = data.get('title')
    body = data.get('body')
    category_id = data.get('category_id')

    if not title or not body:
        return jsonify({'code': 400, 'message': '标题和内容不能为空'}), 200

    # 获取当前用户
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    # 🔥 修复：如果没有找到用户（说明Token过期或数据库已重置）
    if not user:
        return jsonify({'code': 401, 'message': '用户身份无效，请重新登录'}), 401

    # 🔥 权限检查：如果是公告栏，必须是管理员
    category = Category.query.get(category_id)
    if category and category.name == '公告栏':
        if user.role != 'admin':
            return jsonify({'code': 403, 'message': '仅管理员可发布公告'}), 403

    tags = data.get('tags')
    # 确保 tags 是列表
    if not isinstance(tags, list):
        tags = []
    tags_str = ",".join(tags)

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
        print(f"Create Post Error: {e}") # 打印错误日志到控制台
        return jsonify({'code': 500, 'message': str(e)}), 500

@posts_bp.route('/categories', methods=['GET'])
@cache.cached(timeout=120)
def get_categories():
    cats = Category.query.all()
    return jsonify({
        'code': 200,
        'data': [{'id': c.id, 'name': c.name, 'icon': c.icon} for c in cats]
    }), 200