# 热点信息自动收集与处理系统 Docker镜像

# 使用Python 3.11 slim镜像作为基础
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/output /app/config/templates

# 设置权限
RUN chmod +x /app/entrypoint.sh 2>/dev/null || true

# 暴露端口（如果需要）
# EXPOSE 8000

# 入口点
ENTRYPOINT ["python", "-m", "src.main"]

# 默认参数
CMD ["--start-scheduler"]