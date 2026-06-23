import sys
import os

# 将父目录加入 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 修复 Windows 终端编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Category, PostLike, Follow

app = create_app()

with app.app_context():
    print("[!] 警告：此操作将清空所有数据并重置数据库！")
    print("=" * 44)
    confirm = input("请输入 'YES' 确认操作: ")
    if confirm != 'YES':
        print("[X] 操作已取消。")
        sys.exit(0)

    # 这会清空数据！如果只想更新表结构，请用 flask db migrate
    db.drop_all()
    db.create_all()

    # 1. 创建初始分区
    print("正在创建分区...")
    categories = [
        {'name': '前端开发', 'icon': '🎨'},
        {'name': '后端开发', 'icon': '⚡'},
        {'name': '闲聊广场', 'icon': '💬'},
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
    print("[OK] 数据库重置成功！")
    print("管理员账号: admin@example.com")
    print("密码: 123456")
