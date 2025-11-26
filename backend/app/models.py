from datetime import datetime
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
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    # 注意：好友和私信通常通过查询表直接获取，不需要这里定义复杂的 relationship，除非你需要 user.friends 这种调用

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        is_online = False
        if self.last_seen:
            diff = datetime.utcnow() - self.last_seen
            if diff.total_seconds() < 300:  # 300秒 = 5分钟
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
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    body = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    tags = db.Column(db.String(200))

    # 级联删除
    comments_rel = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
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
                'avatar': self.author.avatar  # 确保这里有 avatar
            }
        }

# 4. 评论表
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'avatar': self.author.avatar # 确保这里有 avatar
            }
        }

# 5. 好友表
class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))   # 申请人
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id')) # 被申请人
    status = db.Column(db.String(20), default='pending')         # pending(申请中), accepted(已同意)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 6. 私信表
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # 关系便于查询
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.username,
            'sender_avatar': self.sender.avatar,
            'body': self.body,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'is_read': self.is_read
        }