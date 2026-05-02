# 部署指南

## 概述

本文档提供热点信息自动收集与处理系统的多种部署方案，包括本地部署、Docker部署和服务器部署。

## 环境要求

### 系统要求
- Python 3.8+
- pip 或 conda 包管理器
- 网络连接（用于访问信息源和发送邮件）

### 硬件要求
- CPU: 1核心以上
- 内存: 512MB以上
- 磁盘: 1GB以上

## 方案一：本地部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd 热点信息自动收集与处理系统
```

### 2. 创建虚拟环境

```bash
# 使用venv
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件
# 填入邮箱配置等敏感信息
```

### 5. 配置信息源

编辑 `config/settings.yaml` 和 `config/sources.yaml` 文件，启用/禁用特定信息源。

### 6. 测试运行

```bash
# 测试邮件配置
python -m src.main --test-connection

# 测试邮件发送
python -m src.main --test-email

# 手动执行一次
python -m src.main --run-once
```

### 7. 启动定时任务

```bash
# 启动调度器（前台运行）
python -m src.main --start-scheduler

# 或使用nohup后台运行
nohup python -m src.main --start-scheduler > output.log 2>&1 &
```

## 方案二：Docker部署

### 1. 构建Docker镜像

```bash
docker build -t hotnews-collector .
```

### 2. 运行容器

```bash
# 创建.env文件
cat > .env << EOF
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=your-email-password
LOG_LEVEL=INFO
EOF

# 运行容器
docker run -d \
  --name hotnews-collector \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/output:/app/output \
  --env-file .env \
  --restart unless-stopped \
  hotnews-collector
```

### 3. 使用Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 4. Docker Compose配置说明

```yaml
version: '3.8'

services:
  hotnews-collector:
    build: .
    container_name: hotnews-collector
    restart: unless-stopped
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./output:/app/output
    env_file:
      - .env
    environment:
      - TZ=Asia/Shanghai
```

## 方案三：系统服务部署（Linux）

### 1. 创建系统用户

```bash
sudo useradd -r -s /bin/false hotnews
```

### 2. 安装项目

```bash
# 安装到系统目录
sudo mkdir -p /opt/hotnews
sudo cp -r . /opt/hotnews/
sudo chown -R hotnews:hotnews /opt/hotnews

# 创建虚拟环境
cd /opt/hotnews
sudo -u hotnews python -m venv venv
sudo -u hotnews venv/bin/pip install -r requirements.txt
```

### 3. 创建系统服务文件

```bash
sudo nano /etc/systemd/system/hotnews.service
```

服务文件内容：

```ini
[Unit]
Description=Hot News Collector Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=hotnews
Group=hotnews
WorkingDirectory=/opt/hotnews
EnvironmentFile=/opt/hotnews/.env
ExecStart=/opt/hotnews/venv/bin/python -m src.main --start-scheduler
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4. 启用并启动服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable hotnews

# 启动服务
sudo systemctl start hotnews

# 查看服务状态
sudo systemctl status hotnews

# 查看日志
sudo journalctl -u hotnews -f
```

## 方案四：定时任务（Cron）

如果不想使用内置调度器，可以使用系统cron：

### 1. 编辑crontab

```bash
crontab -e
```

### 2. 添加定时任务

```bash
# 每天19:00执行
0 19 * * * cd /opt/hotnews && /opt/hotnews/venv/bin/python -m src.main --run-once >> /var/log/hotnews.log 2>&1
```

## 配置说明

### 环境变量

创建 `.env` 文件：

```env
# 邮箱配置（必填）
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=your-email-password-or-app-specific-password

# SMTP配置（可选，覆盖settings.yaml）
EMAIL_SMTP_SERVER=smtp.example.com
EMAIL_SMTP_PORT=587

# 收件人（可选，逗号分隔）
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com

# 日志级别
LOG_LEVEL=INFO

# 调试模式
DEBUG=false
```

### 配置文件

#### config/settings.yaml

主配置文件，包含系统、调度、邮件和内容配置。

#### config/sources.yaml

信息源配置文件，包含RSS、社交媒体和新闻网站配置。

## 监控和维护

### 日志查看

```bash
# 实时查看日志
tail -f logs/app.log

# 查看错误日志
grep -i error logs/app.log

# 使用journalctl（系统服务）
sudo journalctl -u hotnews -f
```

### 磁盘空间管理

```bash
# 查看日志大小
du -sh logs/*

# 清理旧日志
find logs/ -name "*.log" -mtime +30 -delete
```

### 性能监控

```bash
# 查看进程资源使用
top -p $(pgrep -f "hotnews")

# 查看容器资源使用
docker stats hotnews-collector
```

## 故障排除

### 1. 邮件发送失败

**问题**: 邮件发送失败，连接超时

**解决方案**:
- 检查SMTP服务器配置
- 确认授权码是否正确
- 检查防火墙设置
- 尝试使用不同的端口（465/587）

### 2. 信息源访问失败

**问题**: 爬虫无法访问信息源

**解决方案**:
- 检查网络连接
- 验证信息源URL是否有效
- 调整访问频率限制
- 检查代理配置

### 3. 定时任务不执行

**问题**: 调度器启动但任务不执行

**解决方案**:
- 检查调度器状态
- 验证cron表达式
- 查看系统时间设置
- 检查日志中的错误信息

### 4. 内存不足

**问题**: 程序运行时内存占用过高

**解决方案**:
- 减少同时运行的爬虫数量
- 降低每个信息源的最大条目数
- 增加系统内存
- 使用内存限制（Docker）

## 安全建议

1. **敏感信息管理**
   - 使用环境变量存储密码和API密钥
   - 不要将 `.env` 文件提交到版本控制
   - 定期更换授权码

2. **访问控制**
   - 限制日志文件访问权限
   - 使用最小权限原则
   - 定期更新依赖包

3. **网络安全**
   - 使用HTTPS连接
   - 配置防火墙规则
   - 监控异常访问

## 升级指南

### 1. 备份配置

```bash
cp -r config config.backup
cp .env .env.backup
```

### 2. 拉取更新

```bash
git pull origin main
```

### 3. 更新依赖

```bash
pip install -r requirements.txt
```

### 4. 重启服务

```bash
# 系统服务
sudo systemctl restart hotnews

# Docker
docker-compose restart
```