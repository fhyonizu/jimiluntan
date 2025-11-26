import sys
import os

# 将当前目录加入 Python 路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Category

app = create_app()

with app.app_context():
    # ⚠️ 这会清空数据！如果只想更新表结构，请用 flask db migrate
    db.drop_all()
    db.create_all()

    # 1. 创建初始分区
    print("正在创建分区...")
    categories = [
        {'name': '前端猫窝', 'icon': '🎨'},
        {'name': '后端爬架', 'icon': '⚡'},
        {'name': '摸鱼广场', 'icon': '🐟'},
        {'name': '公告栏', 'icon': '📢'},
    ]
    for c in categories:
        db.session.add(Category(name=c['name'], icon=c['icon']))

    # 2. 创建管理员
    print("正在创建管理员...")
    admin = User(username='Admin', email='admin@example.com', role='admin')
    admin.set_password('123456')
    db.session.add(admin)

    db.session.commit()
    print("✅ 数据库重置成功！")
    print("👉 管理员账号: admin@example.com")
    print("👉 密码: 123456")