# 热点信息自动收集与处理系统

一个自动化的热点信息收集、分析、总结和分发系统，支持多信息源采集、智能内容分析、定时任务调度和邮件自动发送。

## 🚀 功能特性

### 核心功能
- **多源信息采集**：支持新闻网站RSS、社交媒体API、技术社区等多种信息源
- **智能内容分析**：自动提取关键词、分析热度、过滤无关内容
- **公众号级总结**：生成排版整洁、结构清晰、可直接使用的公众号内容
- **定时自动执行**：每日19:00准时执行信息汇总与分发
- **邮件自动发送**：将生成的总结自动发送至指定邮箱

### 技术特性
- **模块化架构**：各组件低耦合，易于维护和扩展
- **错误容错机制**：单个信息源故障不影响整体系统运行
- **频率控制**：避免对目标网站造成访问负担
- **安全配置**：敏感信息通过环境变量管理，不硬编码
- **完整日志**：详细的运行日志和错误追踪

## 📁 项目结构

```
热点信息自动收集与处理系统/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── main.py                   # 主程序入口
│   ├── config/                   # 配置管理模块
│   │   ├── __init__.py
│   │   ├── settings.py           # 配置设置
│   │   └── loader.py            # 配置加载器
│   ├── crawlers/                 # 信息爬取模块
│   │   ├── __init__.py
│   │   ├── base.py              # 爬虫基类
│   │   ├── rss_crawler.py       # RSS源爬虫
│   │   ├── weibo_crawler.py     # 微博热搜爬虫
│   │   ├── zhihu_crawler.py     # 知乎热榜爬虫
│   │   └── news_crawler.py      # 新闻网站爬虫
│   ├── analyzers/                # 内容分析模块
│   │   ├── __init__.py
│   │   ├── text_analyzer.py     # 文本分析器
│   │   └── keyword_extractor.py # 关键词提取器
│   ├── summarizers/              # 总结生成模块
│   │   ├── __init__.py
│   │   ├── template_engine.py   # 模板引擎
│   │   └── summary_generator.py # 总结生成器
│   ├── mailers/                  # 邮件发送模块
│   │   ├── __init__.py
│   │   └── email_sender.py      # 邮件发送器
│   ├── schedulers/               # 任务调度模块
│   │   ├── __init__.py
│   │   └── workflow_scheduler.py # 工作流调度器
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── logger.py            # 日志工具
│       ├── retry.py             # 重试机制
│       └── helpers.py           # 辅助函数
├── config/                       # 配置文件目录
│   ├── settings.yaml            # 主配置文件
│   ├── sources.yaml             # 信息源配置
│   ├── templates/               # 邮件模板
│   │   └── daily_summary.html
│   └── .env.example            # 环境变量示例
├── tests/                        # 测试代码目录
│   ├── __init__.py
│   ├── unit/                    # 单元测试
│   ├── integration/             # 集成测试
│   └── conftest.py             # 测试配置
├── docs/                         # 文档目录
│   ├── architecture.md         # 架构文档
│   ├── api.md                  # API文档
│   └── deployment.md           # 部署指南
├── examples/                     # 示例数据目录
│   ├── sample_output.html      # 示例输出
│   └── config_example.yaml     # 配置示例
├── logs/                         # 日志目录
├── requirements.txt             # Python依赖
├── setup.py                     # 安装脚本
├── Dockerfile                   # Docker配置
├── docker-compose.yml           # Docker Compose配置
├── .github/                     # GitHub配置
│   └── workflows/
│       └── ci.yml              # CI/CD配置
├── .gitignore                   # Git忽略文件
└── README.md                   # 项目说明文档
```

## 🛠️ 安装指南

### 环境要求
- Python 3.8+
- pip 或 conda 包管理器
- 网络连接（用于访问信息源）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd 热点信息自动收集与处理系统
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   # 复制环境变量示例文件
   cp config/.env.example .env
   
   # 编辑.env文件，填入实际配置
   # 需要配置的敏感信息包括：
   # - 邮箱账号和密码/授权码
   # - API密钥（如果使用需要API的信息源）
   # - 其他敏感配置
   ```

5. **配置信息源**
   ```bash
   # 编辑config/sources.yaml，启用/禁用特定信息源
   # 调整每个信息源的参数
   ```

## 📖 使用说明

### 基本使用

1. **手动执行一次收集任务**
   ```bash
   python -m src.main --run-once
   ```

2. **启动定时任务调度器**
   ```bash
   python -m src.main --start-scheduler
   ```

3. **查看帮助**
   ```bash
   python -m src.main --help
   ```

### 配置说明

#### 主配置文件 (`config/settings.yaml`)
```yaml
# 系统基本配置
system:
  name: "热点信息收集系统"
  version: "1.0.0"
  log_level: "INFO"
  timezone: "Asia/Shanghai"

# 调度配置
scheduler:
  enabled: true
  cron_expression: "0 19 * * *"  # 每天19:00执行
  retry_count: 3
  retry_delay: 300  # 重试延迟（秒）

# 邮件配置
email:
  enabled: true
  smtp_server: "smtp.example.com"
  smtp_port: 587
  use_tls: true
  sender_name: "热点资讯日报"
  # 敏感信息从环境变量读取
  # sender_email: ${EMAIL_SENDER}
  # sender_password: ${EMAIL_PASSWORD}
  recipients:
    - "recipient@example.com"

# 内容生成配置
content:
  max_items_per_source: 10
  total_max_items: 30
  summary_length: 500
  include_images: false
  template: "daily_summary.html"
```

#### 信息源配置 (`config/sources.yaml`)
```yaml
sources:
  # RSS源
  rss_feeds:
    enabled: true
    sources:
      - name: "新浪新闻"
        url: "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page=1&r=0.123&callback="
        category: "新闻"
        max_items: 10
        interval: 3600  # 访问间隔（秒）
      
      - name: "36氪"
        url: "https://36kr.com/feed"
        category: "科技"
        max_items: 8
        interval: 3600

  # 社交媒体
  social_media:
    enabled: true
    weibo:
      enabled: true
      max_items: 15
      interval: 1800
    zhihu:
      enabled: true
      max_items: 10
      interval: 1800

  # 新闻网站
  news_sites:
    enabled: true
    sites:
      - name: "今日头条"
        url: "https://www.toutiao.com/"
        selector: ".news-box .news-item"
        max_items: 10
        interval: 3600
```

### 环境变量说明

创建 `.env` 文件并配置以下变量：

```env
# 邮箱配置
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=your-email-password-or-app-specific-password

# API密钥（如果使用）
WEIBO_API_KEY=your-weibo-api-key
ZHIHU_API_KEY=your-zhihu-api-key

# 其他配置
LOG_LEVEL=INFO
DEBUG=false
```

## 🔧 开发指南

### 项目架构

系统采用模块化架构，主要组件包括：

1. **爬虫模块 (Crawlers)**
   - 负责从各个信息源获取原始数据
   - 实现频率控制和错误处理
   - 支持插件式扩展新信息源

2. **分析模块 (Analyzers)**
   - 对原始内容进行文本分析
   - 提取关键词、计算热度
   - 过滤无关或低质量内容

3. **总结生成模块 (Summarizers)**
   - 基于模板生成公众号格式内容
   - 支持自定义模板和格式
   - 确保内容排版整洁

4. **邮件模块 (Mailers)**
   - 处理邮件发送逻辑
   - 支持HTML格式邮件
   - 实现发送失败重试

5. **调度模块 (Schedulers)**
   - 管理定时任务执行
   - 协调各模块工作流程
   - 处理异常和恢复

### 添加新信息源

1. 在 `src/crawlers/` 目录下创建新的爬虫类
2. 继承 `BaseCrawler` 基类
3. 实现必要的方法：`fetch()`, `parse()`, `validate()`
4. 在 `config/sources.yaml` 中添加配置
5. 在 `src/config/loader.py` 中注册新爬虫

### 自定义总结模板

1. 在 `config/templates/` 目录下创建HTML模板
2. 使用Jinja2模板语法
3. 在 `config/settings.yaml` 中指定模板文件名
4. 模板可用变量包括：`date`, `items`, `categories`, `metadata`

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成测试覆盖率报告
pytest --cov=src --cov-report=html
```

### 代码质量检查

```bash
# 代码格式化
black src/ tests/

# 导入排序
isort src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/
```

## 🚀 部署指南

### Docker部署（推荐）

1. **构建Docker镜像**
   ```bash
   docker build -t hotnews-collector .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     --name hotnews-collector \
     -v $(pwd)/config:/app/config \
     -v $(pwd)/logs:/app/logs \
     --env-file .env \
     hotnews-collector
   ```

3. **使用Docker Compose**
   ```bash
   # 启动服务
   docker-compose up -d
   
   # 查看日志
   docker-compose logs -f
   
   # 停止服务
   docker-compose down
   ```

### 系统服务部署

1. **创建系统服务文件**
   ```bash
   sudo nano /etc/systemd/system/hotnews.service
   ```

2. **服务文件内容**
   ```ini
   [Unit]
   Description=Hot News Collector Service
   After=network.target
   
   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/project
   EnvironmentFile=/path/to/project/.env
   ExecStart=/path/to/venv/bin/python -m src.main --start-scheduler
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **启用并启动服务**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable hotnews
   sudo systemctl start hotnews
   sudo systemctl status hotnews
   ```

### 定时任务（Cron）

如果不想使用内置调度器，可以使用系统cron：

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天19:00执行）
0 19 * * * cd /path/to/project && /path/to/venv/bin/python -m src.main --run-once >> /var/log/hotnews.log 2>&1
```

## 📊 监控与维护

### 日志查看

```bash
# 实时查看日志
tail -f logs/app.log

# 查看错误日志
grep -i error logs/app.log

# 查看特定日期的日志
grep "2024-01-01" logs/app.log
```

### 性能监控

系统提供以下监控指标：
- 信息源访问成功率
- 内容处理耗时
- 邮件发送成功率
- 内存和CPU使用情况

### 故障排除

1. **信息源访问失败**
   - 检查网络连接
   - 验证信息源URL是否有效
   - 查看频率限制设置
   - 检查代理配置

2. **邮件发送失败**
   - 验证邮箱配置
   - 检查SMTP服务器设置
   - 确认授权码是否正确
   - 查看防火墙设置

3. **定时任务不执行**
   - 检查调度器状态
   - 验证cron表达式
   - 查看系统时间设置
   - 检查服务日志

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出改进建议！

### 贡献步骤

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- 遵循 PEP 8 代码规范
- 添加适当的注释和文档字符串
- 编写单元测试
- 更新相关文档
- 使用语义化版本号

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件至：[your-email@example.com]
- 项目主页：[project-homepage]

## 🙏 致谢

感谢以下开源项目：
- [Requests](https://requests.readthedocs.io/) - HTTP库
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML解析
- [APScheduler](https://apscheduler.readthedocs.io/) - 任务调度
- [Jinja2](https://jinja.palletsprojects.com/) - 模板引擎

---

**注意**：本系统仅用于合法的信息收集和研究目的，请遵守相关法律法规和网站使用条款。