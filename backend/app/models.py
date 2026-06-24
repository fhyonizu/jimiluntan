from datetime import datetime, timezone
from typing import Any

from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


# 1. 分区表
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(20))
    posts = db.relationship('Post', backref='category', lazy='dynamic')


# 2. 用户表
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.String(256), default='')
    about_me = db.Column(db.Text())
    role = db.Column(db.String(20), default='user')
    email_verified = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict[str, Any]:
        is_online = False
        if self.last_seen:
            # SQLite 存储的是 naive datetime，需要统一比较
            last_seen_utc = self.last_seen.replace(tzinfo=timezone.utc) if self.last_seen.tzinfo is None else self.last_seen
            diff = datetime.now(timezone.utc) - last_seen_utc
            if diff.total_seconds() < 300:
                is_online = True

        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'about_me': self.about_me,
            'role': self.role,
            'member_since': self.member_since.isoformat() + 'Z',
            'posts_count': self.posts.count(),
            'is_online': is_online,
        }


# 3. 帖子表
class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = (
        db.Index('ix_posts_category_time', 'category_id', 'timestamp'),
    )
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    body = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    tags = db.Column(db.String(200))

    comments_rel = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self) -> dict[str, Any]:
        # 优先使用批量注入的 likes_count，避免 N+1
        likes = getattr(self, '_likes_count', None)
        if likes is None:
            likes = PostLike.query.filter_by(post_id=self.id).count()

        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'content_md': self.body,
            'content_html': None,  # 由路由层注入
            'views': self.views,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'tags': self.tags.split(',') if self.tags else [],
            'category': {
                'id': self.category.id,
                'name': self.category.name,
                'icon': self.category.icon
            } if self.category else None,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'avatar': self.author.avatar
            } if self.author else None,
            'likes': likes
        }


# 4. 评论表
class Comment(db.Model):
    __tablename__ = 'comments'
    __table_args__ = (
        db.Index('ix_comments_post_time', 'post_id', 'timestamp'),
    )
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'body': self.body,
            'content_md': self.body,
            'content_html': None,  # 由路由层注入
            'timestamp': self.timestamp.isoformat() + 'Z',
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'avatar': self.author.avatar
            } if self.author else None
        }


# 5. 好友表
class Friend(db.Model):
    __tablename__ = 'friends'
    __table_args__ = (
        db.Index('ix_friends_user_status', 'user_id', 'status'),
        db.Index('ix_friends_friend_status', 'friend_id', 'status'),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='pending')
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# 6. 私信表
class Message(db.Model):
    __tablename__ = 'messages'
    __table_args__ = (
        db.Index('ix_messages_pair', 'sender_id', 'receiver_id', 'timestamp'),
        db.Index('ix_messages_unread', 'sender_id', 'receiver_id', 'is_read'),
    )
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.username if self.sender else '',
            'sender_avatar': self.sender.avatar if self.sender else '',
            'body': self.body,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'is_read': self.is_read
        }


# 7. 点赞表
class PostLike(db.Model):
    __tablename__ = 'post_likes'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# 8. 关注表
class Follow(db.Model):
    __tablename__ = 'follows'
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='uq_follow'),
    )
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# 9. 密码重置申请表
class PasswordResetRequest(db.Model):
    __tablename__ = 'password_reset_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending / approved / rejected
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='password_reset_requests')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
