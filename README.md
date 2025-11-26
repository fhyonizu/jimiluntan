# 极米论坛 (JiMiLunTan)

一个简单而功能完善的论坛系统，使用 Flask 和 Python 开发。

## 功能特性

- 用户注册和登录系统
- 论坛分类管理
- 主题/帖子发表与浏览
- 回复功能
- 分页浏览
- 响应式设计

## 技术栈

- **后端**: Python 3, Flask
- **数据库**: SQLite (可配置为其他数据库)
- **前端**: HTML5, CSS3, Jinja2 模板
- **认证**: Flask-Login
- **表单**: Flask-WTF

## 安装和运行

### 环境要求

- Python 3.7+
- pip

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/fhyonizu/jimiluntan.git
cd jimiluntan
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行应用：
```bash
python run.py
```

5. 在浏览器中访问：
```
http://127.0.0.1:5000
```

## 使用指南

1. **注册账号**: 点击导航栏的"注册"按钮创建账号
2. **登录**: 使用注册的用户名和密码登录
3. **创建分类**: 登录后可以创建论坛分类
4. **发表主题**: 在分类中发表新主题
5. **回复讨论**: 在主题页面发表回复

## 配置

在 `config.py` 中可以修改以下配置：

- `SECRET_KEY`: 应用密钥（生产环境请务必更改）
- `SQLALCHEMY_DATABASE_URI`: 数据库连接字符串

## 数据库

首次运行时会自动创建 SQLite 数据库文件 `forum.db`。

数据库模型包括：
- **User**: 用户表
- **Category**: 分类表
- **Thread**: 主题表
- **Post**: 回复表

## 项目结构

```
jimiluntan/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models.py            # 数据库模型
│   ├── forms.py             # 表单定义
│   ├── routes/              # 路由蓝图
│   │   ├── auth.py          # 认证路由
│   │   └── main.py          # 主要路由
│   ├── templates/           # HTML 模板
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── category.html
│   │   ├── thread.html
│   │   ├── new_thread.html
│   │   ├── new_category.html
│   │   └── auth/
│   │       ├── login.html
│   │       └── register.html
│   └── static/              # 静态文件
│       └── css/
│           └── style.css
├── config.py                # 配置文件
├── requirements.txt         # 依赖列表
├── run.py                   # 应用入口
└── README.md               # 说明文档
```

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，欢迎提交 Issue。