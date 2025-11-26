from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User, Post, Category, Comment
from ..decorators import admin_required

admin_bp = Blueprint('admin', __name__)


# ==========================================
# 📊 核心统计 (Dashboard)
# ==========================================
@admin_bp.route('/stats', methods=['GET'])
@admin_required()
def stats():
    return jsonify({'code': 200, 'data': {
        'users': User.query.count(),
        'posts': Post.query.count(),
        'categories': Category.query.count(),
        'comments': Comment.query.count()
    }}), 200


# ==========================================
# 🌈 板块管理 (Categories)
# ==========================================
@admin_bp.route('/categories', methods=['GET'])
@admin_required()
def get_cats():
    return jsonify(
        {'code': 200, 'data': [{'id': c.id, 'name': c.name, 'icon': c.icon} for c in Category.query.all()]}), 200


@admin_bp.route('/categories', methods=['POST'])
@admin_required()
def add_cat():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'code': 400, 'message': '名称不能为空'}), 200

    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'code': 400, 'message': '已存在同名板块'}), 200

    db.session.add(Category(name=data['name'], icon=data.get('icon')))
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功'}), 200


@admin_bp.route('/categories/<int:id>', methods=['DELETE'])
@admin_required()
def del_cat(id):
    cat = Category.query.get(id)
    if cat:
        db.session.delete(cat)
        db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'}), 200


# ==========================================
# 👥 用户管理 (Users) - 已修复字段名
# ==========================================
@admin_bp.route('/users', methods=['GET'])
@admin_required()
def get_users():
    # 🔥 修复1：排序字段改为 member_since
    users = User.query.order_by(User.member_since.desc()).all()

    data = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'avatar': u.avatar,
        # 🔥 修复2：前端需要 'timestamp' 字段显示时间，我们将 member_since 映射过去
        'timestamp': u.member_since
    } for u in users]

    return jsonify({'code': 200, 'data': data}), 200


@admin_bp.route('/users/<int:id>', methods=['DELETE'])
@admin_required()
def del_user(id):
    user = User.query.get(id)
    if user:
        # 防止删除唯一的管理员（根据你的逻辑调整）
        if user.role == 'admin' and User.query.filter_by(role='admin').count() <= 1:
            return jsonify({'code': 403, 'message': '不能删除最后一个管理员！'}), 200

        # 因为你在 Post 模型里设置了级联删除 (comments_rel)，
        # 但 User 模型里的 posts 和 comments 是 lazy='dynamic'
        # SQLAlchemy 通常会自动处理 User 删除时的级联，前提是外键设置了 ON DELETE CASCADE
        # 如果报错，可能需要先手动删除关联数据
        db.session.delete(user)
        db.session.commit()
    return jsonify({'code': 200, 'message': '用户已移除'}), 200


# ==========================================
# 📝 文章管理 (Posts)
# ==========================================
@admin_bp.route('/posts', methods=['GET'])
@admin_required()
def get_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    data = [{
        'id': p.id,
        'title': p.title,
        'body': p.body,
        'views': p.views,
        'timestamp': p.timestamp,
        'author': {'username': p.author.username} if p.author else {'username': '已注销'},
        'category': {'name': p.category.name} if p.category else {'name': '未分类'}
    } for p in posts]
    return jsonify({'code': 200, 'data': data}), 200


@admin_bp.route('/posts/<int:id>', methods=['DELETE'])
@admin_required()
def del_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
    return jsonify({'code': 200, 'message': '文章已删除'}), 200


# ==========================================
# 💬 评论管理 (Comments)
# ==========================================
@admin_bp.route('/comments', methods=['GET'])
@admin_required()
def get_comments():
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    data = [{
        'id': c.id,
        'body': c.body,
        'timestamp': c.timestamp,
        'post_id': c.post_id,
        'author': {'username': c.author.username} if c.author else {'username': '未知'}
    } for c in comments]
    return jsonify({'code': 200, 'data': data}), 200


@admin_bp.route('/comments/<int:id>', methods=['DELETE'])
@admin_required()
def del_comment(id):
    comment = Comment.query.get(id)
    if comment:
        db.session.delete(comment)
        db.session.commit()
    return jsonify({'code': 200, 'message': '评论已删除'}), 200