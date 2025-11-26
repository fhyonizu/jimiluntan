from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Post, User, Category, Comment
from flask_jwt_extended import jwt_required, get_jwt_identity

posts_bp = Blueprint('posts', __name__)


# ... (get_posts, get_post_detail, add_comment 保持不变，省略以节省篇幅，请保留原有的) ...
# 为了方便，这里只展示修改了的 create_post 和 get_categories

@posts_bp.route('/', methods=['GET'])
def get_posts():
    sort_by = request.args.get('sort', 'latest')
    category_id = request.args.get('category_id')  # <--- 新增这行：接收分类ID
    query = Post.query
    if category_id:
        query = query.filter_by(category_id=category_id)

    if sort_by == 'hot':
        posts = query.order_by(Post.views.desc()).all()
    else:
        posts = query.order_by(Post.timestamp.desc()).all()
    return jsonify({'code': 200, 'data': [post.to_dict() for post in posts]}), 200


@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    post = Post.query.get(post_id)
    if not post: return jsonify({'code': 404, 'message': '帖子找不到了喵~'}), 404
    post.views += 1
    db.session.commit()
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.timestamp.asc()).all()
    post_data = post.to_dict()
    post_data['comments'] = [c.to_dict() for c in comments]
    return jsonify({'code': 200, 'data': post_data}), 200


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
            return jsonify({'code': 403, 'message': '大胆！只有猫神（管理员）才能发布公告！'}), 403

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
def get_categories():
    cats = Category.query.all()
    return jsonify({
        'code': 200,
        'data': [{'id': c.id, 'name': c.name, 'icon': c.icon} for c in cats]
    }), 200