from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from ..extensions import db
from ..models import User, Post, Category, Comment, Friend, Message, PostLike, Follow, PasswordResetRequest
from ..decorators import admin_required
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
import subprocess
import os

admin_bp = Blueprint('admin', __name__)

MAX_PER_PAGE = 50

# 版本文件路径（项目根目录下的 VERSION）
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_VERSION_FILE = os.path.join(_PROJECT_ROOT, 'VERSION')


def _read_version() -> str:
    """读取当前版本号"""
    try:
        with open(_VERSION_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return 'unknown'


def _git_available() -> bool:
    """检测 git 是否可用且仓库存在"""
    try:
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'],
                       capture_output=True, timeout=5,
                       cwd=os.path.dirname(_VERSION_FILE))
        return True
    except Exception:
        return False


def _docker_available() -> bool:
    """检测是否运行在 Docker 中"""
    return os.path.exists('/.dockerenv')


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
    if not data or not (data.get('name') or '').strip():
        return jsonify({'code': 400, 'message': '名称不能为空'}), 400

    name = data['name'].strip()
    if len(name) > 50:
        return jsonify({'code': 400, 'message': '名称不能超过50个字符'}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({'code': 400, 'message': '已存在同名板块'}), 400

    try:
        db.session.add(Category(name=name, icon=(data.get('icon') or '')[:20]))
        db.session.commit()
        return jsonify({'code': 200, 'message': '创建成功'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('创建板块失败')
        return jsonify({'code': 500, 'message': '创建失败'}), 500


@admin_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@admin_required()
def del_cat(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return jsonify({'code': 404, 'message': '板块不存在'}), 404
    try:
        db.session.delete(cat)
        db.session.commit()
        return jsonify({'code': 200, 'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('删除板块失败')
        return jsonify({'code': 500, 'message': '删除失败'}), 500


# ==========================================
# 👥 用户管理 (Users)
# ==========================================
@admin_bp.route('/users', methods=['GET'])
@admin_required()
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), MAX_PER_PAGE)
    pagination = User.query.order_by(User.member_since.desc()).paginate(page=page, per_page=per_page, error_out=False)

    data = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'avatar': u.avatar,
        'timestamp': u.member_since
    } for u in pagination.items]

    return jsonify({
        'code': 200,
        'data': data,
        'total': pagination.total,
        'pages': pagination.pages
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def del_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    # 防止删除唯一的管理员
    if user.role == 'admin' and User.query.filter_by(role='admin').count() <= 1:
        return jsonify({'code': 403, 'message': '不能删除最后一个管理员！'}), 403

    try:
        # 好友关系
        Friend.query.filter(
            (Friend.user_id == user_id) | (Friend.friend_id == user_id)
        ).delete(synchronize_session=False)
        # 私信
        Message.query.filter(
            (Message.sender_id == user_id) | (Message.receiver_id == user_id)
        ).delete(synchronize_session=False)
        # 点赞
        PostLike.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        # 关注
        Follow.query.filter(
            (Follow.follower_id == user_id) | (Follow.followed_id == user_id)
        ).delete(synchronize_session=False)

        db.session.delete(user)
        db.session.commit()
        return jsonify({'code': 200, 'message': '用户已移除'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('删除用户失败')
        return jsonify({'code': 500, 'message': '删除失败'}), 500


# ==========================================
# 📝 文章管理 (Posts)
# ==========================================
@admin_bp.route('/posts', methods=['GET'])
@admin_required()
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), MAX_PER_PAGE)
    pagination = Post.query.options(
        joinedload(Post.author),
        joinedload(Post.category)
    ).order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    data = [{
        'id': p.id,
        'title': p.title,
        'body': p.body,
        'views': p.views,
        'timestamp': p.timestamp,
        'author': {'username': p.author.username} if p.author else {'username': '已注销'},
        'category': {'name': p.category.name} if p.category else {'name': '未分类'}
    } for p in pagination.items]
    return jsonify({
        'code': 200,
        'data': data,
        'total': pagination.total,
        'pages': pagination.pages
    }), 200


@admin_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@admin_required()
def del_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'code': 200, 'message': '文章已删除'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('删除帖子失败')
        return jsonify({'code': 500, 'message': '删除失败'}), 500


# ==========================================
# 💬 评论管理 (Comments)
# ==========================================
@admin_bp.route('/comments', methods=['GET'])
@admin_required()
def get_comments():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), MAX_PER_PAGE)
    pagination = Comment.query.options(
        joinedload(Comment.author)
    ).order_by(Comment.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    data = [{
        'id': c.id,
        'body': c.body,
        'timestamp': c.timestamp,
        'post_id': c.post_id,
        'author': {'username': c.author.username} if c.author else {'username': '未知'}
    } for c in pagination.items]
    return jsonify({
        'code': 200,
        'data': data,
        'total': pagination.total,
        'pages': pagination.pages
    }), 200


@admin_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@admin_required()
def del_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'code': 404, 'message': '评论不存在'}), 404
    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'code': 200, 'message': '评论已删除'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('删除评论失败')
        return jsonify({'code': 500, 'message': '删除失败'}), 500


# ==========================================
# 🔑 密码重置申请管理
# ==========================================
@admin_bp.route('/password-resets', methods=['GET'])
@admin_required()
def get_password_resets():
    """获取密码重置申请列表"""
    status_filter = request.args.get('status', 'pending')
    if status_filter not in ('pending', 'approved', 'rejected', 'all'):
        status_filter = 'pending'

    query = PasswordResetRequest.query.options(joinedload(PasswordResetRequest.user))
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    requests = query.order_by(PasswordResetRequest.timestamp.desc()).all()

    data = []
    for r in requests:
        item = {
            'id': r.id,
            'user_id': r.user_id,
            'username': r.user.username if r.user else '',
            'email': r.user.email if r.user else '',
            'status': r.status,
            'timestamp': r.timestamp.isoformat() + 'Z',
        }
        if r.reviewer_id:
            item['reviewer_id'] = r.reviewer_id
        if r.reviewed_at:
            item['reviewed_at'] = r.reviewed_at.isoformat() + 'Z'
        data.append(item)

    return jsonify({'code': 200, 'data': data}), 200


@admin_bp.route('/password-resets/<int:req_id>/approve', methods=['POST'])
@admin_required()
def approve_password_reset(req_id):
    """批准密码重置，生成临时密码"""
    reset_req = PasswordResetRequest.query.get(req_id)
    if not reset_req:
        return jsonify({'code': 404, 'message': '申请不存在'}), 404
    if reset_req.status != 'pending':
        return jsonify({'code': 400, 'message': '该申请已处理'}), 400

    user = User.query.get(reset_req.user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    # 生成8位随机临时密码
    import secrets
    import string
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    user.set_password(temp_password)

    reset_req.status = 'approved'
    reset_req.reviewer_id = int(get_jwt_identity())
    reset_req.reviewed_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '已批准，临时密码已生成',
            'data': {
                'temp_password': temp_password,
                'username': user.username,
                'email': user.email
            }
        }), 200
    except Exception:
        db.session.rollback()
        current_app.logger.error('批准密码重置失败')
        return jsonify({'code': 500, 'message': '操作失败'}), 500


@admin_bp.route('/password-resets/<int:req_id>/reject', methods=['POST'])
@admin_required()
def reject_password_reset(req_id):
    """拒绝密码重置申请"""
    reset_req = PasswordResetRequest.query.get(req_id)
    if not reset_req:
        return jsonify({'code': 404, 'message': '申请不存在'}), 404
    if reset_req.status != 'pending':
        return jsonify({'code': 400, 'message': '该申请已处理'}), 400

    reset_req.status = 'rejected'
    reset_req.reviewer_id = int(get_jwt_identity())
    reset_req.reviewed_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '已拒绝'}), 200
    except Exception:
        db.session.rollback()
        current_app.logger.error('拒绝密码重置失败')
        return jsonify({'code': 500, 'message': '操作失败'}), 500


# ==========================================
# 🚀 系统升级管理
# ==========================================

@admin_bp.route('/system/info', methods=['GET'])
@admin_required()
def system_info():
    """获取当前系统信息：版本、git 状态、运行环境"""
    project_dir = os.path.dirname(_VERSION_FILE)
    info = {
        'version': _read_version(),
        'is_docker': _docker_available(),
        'git_available': False,
        'git_branch': '',
        'git_commit': '',
        'git_dirty': False,
        'git_remote_url': '',
    }

    if _git_available():
        try:
            def _git(*args):
                r = subprocess.run(['git'] + list(args), capture_output=True, text=True, timeout=10, cwd=project_dir)
                return r.stdout.strip() if r.returncode == 0 else ''

            info['git_available'] = True
            info['git_branch'] = _git('rev-parse', '--abbrev-ref', 'HEAD')
            info['git_commit'] = _git('rev-parse', '--short', 'HEAD')
            info['git_dirty'] = _git('status', '--porcelain') != ''
            info['git_remote_url'] = _git('remote', 'get-url', 'origin')
        except Exception as e:
            current_app.logger.warning('获取 git 信息失败: %s', e)

    return jsonify({'code': 200, 'data': info}), 200


@admin_bp.route('/system/check-update', methods=['GET'])
@admin_required()
def check_update():
    """检查是否有新版本（git fetch + 对比远程分支）"""
    if not _git_available():
        return jsonify({'code': 400, 'message': '当前环境不支持 git 操作'}), 400

    project_dir = os.path.dirname(_VERSION_FILE)
    try:
        # fetch 远程
        subprocess.run(['git', 'fetch', 'origin'], capture_output=True, timeout=30, cwd=project_dir)

        def _git(*args):
            r = subprocess.run(['git'] + list(args), capture_output=True, text=True, timeout=10, cwd=project_dir)
            return r.stdout.strip() if r.returncode == 0 else ''

        local_commit = _git('rev-parse', 'HEAD')
        remote_commit = _git('rev-parse', 'FETCH_HEAD')

        # 查看远程 HEAD 对应的分支
        remote_branch = _git('rev-parse', '--abbrev-ref', 'FETCH_HEAD')
        if not remote_branch:
            remote_branch = 'origin/master'

        if not local_commit or not remote_commit:
            return jsonify({'code': 500, 'message': '无法获取版本信息'}), 500

        has_update = local_commit != remote_commit

        # 如果有更新，获取 changelog
        changelog = ''
        if has_update:
            changelog = _git('log', '--oneline', f'{local_commit}..{remote_commit}', '--max-count=20')

        # 读取远程版本号
        remote_version = 'unknown'
        if has_update:
            # 临时 checkout 远程的 VERSION 文件
            v = subprocess.run(
                ['git', 'show', f'{remote_commit}:VERSION'],
                capture_output=True, text=True, timeout=5, cwd=project_dir
            )
            if v.returncode == 0:
                remote_version = v.stdout.strip()

        return jsonify({'code': 200, 'data': {
            'has_update': has_update,
            'local_commit': local_commit[:7],
            'remote_commit': remote_commit[:7],
            'remote_branch': remote_branch,
            'local_version': _read_version(),
            'remote_version': remote_version,
            'changelog': changelog,
        }}), 200
    except subprocess.TimeoutExpired:
        return jsonify({'code': 504, 'message': '检查更新超时，请稍后再试'}), 504
    except Exception as e:
        current_app.logger.error('检查更新失败')
        return jsonify({'code': 500, 'message': f'检查更新失败: {e}'}), 500


@admin_bp.route('/system/upgrade', methods=['POST'])
@admin_required()
def do_upgrade():
    """执行一键升级：git pull + 重建前端 + 重启服务"""
    if not _git_available():
        return jsonify({'code': 400, 'message': '当前环境不支持 git 操作'}), 400

    project_dir = os.path.dirname(_VERSION_FILE)

    # 检查本地是否有未提交的改动
    try:
        r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, timeout=5, cwd=project_dir)
        if r.returncode == 0 and r.stdout.strip():
            return jsonify({'code': 400, 'message': '存在未提交的本地修改，请先处理后再升级'}), 400
    except Exception:
        pass

    is_docker = _docker_available()
    logs = []

    def _run(cmd, desc, timeout=60):
        """运行命令并记录日志"""
        logs.append(f'→ {desc}')
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=project_dir, shell=isinstance(cmd, str))
            out = (r.stdout or '').strip()
            err = (r.stderr or '').strip()
            if r.returncode != 0:
                logs.append(f'  ✗ 失败 (exit {r.returncode})')
                if err:
                    logs.append(f'  错误: {err[:200]}')
                return False
            if out:
                logs.append(f'  {out[:200]}')
            else:
                logs.append(f'  ✓ 成功')
            return True
        except subprocess.TimeoutExpired:
            logs.append(f'  ✗ 超时 ({timeout}s)')
            return False
        except Exception as e:
            logs.append(f'  ✗ 异常: {e}')
            return False

    # 1) git pull
    if not _run(['git', 'pull', 'origin', 'master'], '拉取最新代码', timeout=60):
        return jsonify({'code': 500, 'message': '拉取代码失败', 'logs': logs}), 500

    # 2) 安装 Python 依赖（如果有变化）
    pip_cmd = ['pip', 'install', '-r', 'backend/requirements.txt']
    if is_docker:
        pip_cmd = ['pip', 'install', '-r', '/app/backend/requirements.txt']
    _run(pip_cmd, '更新 Python 依赖', timeout=120)

    # 3) 数据库迁移
    if is_docker:
        _run(['flask', 'db', 'upgrade'], '执行数据库迁移', timeout=30)
    else:
        _run(['python', '-m', 'flask', 'db', 'upgrade'], '执行数据库迁移', timeout=30)

    # 4) 构建前端
    _run(['npm', 'install', '--prefix', 'frontend'], '安装前端依赖', timeout=120)
    _run(['npm', 'run', 'build', '--prefix', 'frontend'], '构建前端', timeout=120)

    # 5) 重启服务
    if is_docker:
        # Docker 环境下向 supervisor 发送重启信号
        restart_ok = _run(['bash', '-c', 'kill -HUP 1 2>/dev/null || supervisorctl restart all 2>/dev/null || echo "restart_signal_sent"'], '发送重启信号', timeout=10)
    else:
        # 非 Docker：写入一个标记文件，由外部监控脚本处理重启
        restart_marker = os.path.join(project_dir, '.restart-requested')
        try:
            with open(restart_marker, 'w') as f:
                f.write('1')
            logs.append('→ 请求重启')
            logs.append('  ✓ 重启标记已写入，服务将自动重启')
            restart_ok = True
        except Exception as e:
            logs.append(f'  ✗ 写入重启标记失败: {e}')
            restart_ok = False

    # 读取新版本号
    new_version = _read_version()

    return jsonify({
        'code': 200,
        'message': '升级完成' + ('，服务将重启' if restart_ok else '，请手动重启服务'),
        'data': {
            'new_version': new_version,
            'logs': logs,
        }
    }), 200
