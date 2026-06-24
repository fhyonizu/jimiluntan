# ==================== 基米论坛 Dockerfile ====================
# 多阶段构建：前端构建 → 运行时镜像

# ---- Stage 1: 构建前端 ----
FROM node:22-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --registry=https://registry.npmmirror.com
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: 运行时 ----
FROM python:3.12-slim

# 安装系统依赖 + git（升级功能需要） + node（前端构建需要） + supervisord
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    nodejs \
    npm \
    supervisor \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python 依赖
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY backend/ ./backend/
COPY VERSION ./VERSION

# 复制前端构建产物
COPY --from=frontend-builder /build/dist ./frontend/dist

# Nginx 配置
COPY docker/nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default && \
    rm -f /etc/nginx/sites-enabled/default.bak

# Supervisor 配置
COPY docker/supervisord-base.conf /etc/supervisor/supervisord.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/jimiluntan.conf

# 日志目录
RUN mkdir -p /var/log/supervisor

# 数据目录
RUN mkdir -p /app/backend/app/static/uploads && \
    mkdir -p /app/data

# 环境变量
ENV FLASK_DEBUG=0 \
    PYTHONPATH=/app \
    DB_HOST=db \
    DB_PORT=3306 \
    DB_NAME=jimiluntan \
    DB_USER=jimiluntan

# 暴露端口（Nginx 代理）
EXPOSE 80

# 启动 supervisord
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
