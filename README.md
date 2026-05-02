<div align="center">

# HotNews Agent

### 智能热点信息采集 · 分析 · 生成 · 分发一体化平台

**Intelligent Hot News Collection, Analysis, Generation & Distribution Platform**

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-47%2F47-passing-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Modular-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

[English](#english-version) | 中文

</div>

---

## 一、项目概述

HotNews Agent 是一套**端到端的智能信息处理流水线（Pipeline）系统**，面向信息密集型场景，实现了从多源异构数据采集、自然语言处理（NLP）分析、结构化内容生成到多渠道自动分发的全链路自动化。

系统采用**事件驱动的微内核架构**，通过可插拔的爬虫插件体系、可配置的 NLP 处理链和可定制的模板渲染引擎，为内容运营团队、行业分析师及技术社区提供每日热点情报的自动化采集与结构化输出能力，显著降低人工信息筛选的时间成本与认知负荷。

### 核心价值主张

| 维度 | 传统方式 | HotNews Agent |
|------|---------|---------------|
| 信息覆盖 | 人工浏览 3-5 个平台 | 自动采集 11+ 异构数据源 |
| 处理时效 | 2-4 小时人工整理 | < 5 分钟全自动完成 |
| 内容质量 | 依赖个人经验筛选 | 多维热度评分 + 关键词权重融合 |
| 输出规范性 | 格式不统一 | 公众号标准模板，一键复制发布 |
| 系统可靠性 | 人员依赖 | 定时调度 + 自动重试 + 故障隔离 |

---

## 二、业务痛点与目标用户

### 解决的核心业务痛点

1. **信息过载（Information Overload）**：在信息爆炸时代，专业人员日均需处理 200+ 条资讯，人工筛选效率低下且存在信息遗漏风险
2. **多源异构数据整合困难**：新闻门户（HTML）、社交媒体（JSON API）、技术社区（RSS/Atom）等数据源协议各异，缺乏统一采集框架
3. **内容生产效率瓶颈**：从信息采集到内容发布需经历"采集→筛选→摘要→排版→分发"五步，人力成本高、周转周期长
4. **质量一致性难以保障**：人工处理在注意力衰退后质量显著下降，且缺乏量化的内容评估标准

### 目标用户群体

- **内容运营团队**：公众号、自媒体运营者，需要每日生成热点摘要内容
- **行业分析师**：金融、科技、政策领域分析师，需要跨平台情报聚合
- **企业情报部门**：竞品监控、市场趋势追踪、舆情预警
- **技术社区管理者**：技术博客、Newsletter 运营者，需自动化内容策展
- **学术研究者**：舆情分析、传播学研究的数据采集基础设施

---

## 三、技术架构

### 3.1 整体架构设计

系统采用**分层管道架构（Layered Pipeline Architecture）**，自下而上分为基础设施层、数据采集层、智能分析层、内容生成层和分发层：

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface (main.py)                  │
│                  argparse · Command Pattern                  │
├─────────────────────────────────────────────────────────────┤
│                  Workflow Orchestrator Layer                  │
│              WorkflowScheduler (APScheduler)                  │
│           CronTrigger · EventListener · RetryPolicy          │
├────────────┬──────────────┬──────────────┬──────────────────┤
│  Collection │   Analysis   │  Generation  │   Distribution   │
│    Layer    │    Layer     │    Layer     │      Layer       │
├────────────┼──────────────┼──────────────┼──────────────────┤
│ CrawlerMgr │ TextAnalyzer │ SummaryGen   │   EmailSender    │
│ ThreadPool │ KeywordExt   │ TemplateEng  │   SMTP/TLS       │
│ 4 Workers  │ jieba+sklearn│ Jinja2       │   Retry 3x       │
├────────────┴──────────────┴──────────────┴──────────────────┤
│                  Infrastructure Layer                         │
│  ConfigLoader · Settings(Pydantic) · Logger(loguru) · Retry  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 数据处理流水线

系统核心工作流遵循 **ETL（Extract-Transform-Load）** 模范，以四阶段流水线（Pipeline）模式执行：

```
Stage 1          Stage 2          Stage 3          Stage 4
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ EXTRACT  │───▶│ TRANSFORM│───▶│ GENERATE │───▶│ DELIVER  │
│          │    │          │    │          │    │          │
│ 多源并发  │    │ NLP分析   │    │ 模板渲染  │    │ 邮件分发  │
│ 爬取     │    │ 关键词提取 │    │ HTML生成  │    │ SMTP发送  │
│ 去重过滤  │    │ 热度计算   │    │ 文本生成  │    │ 附件上传  │
│ 频率控制  │    │ 自动分类   │    │ 文件归档  │    │ 重试机制  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │                │                │                │
  11 数据源       jieba+Numpy      Jinja2模板      SMTP/TLS
  ThreadPool      TF-IDF           响应式HTML       3次重试
  4 Workers       TextRank         内联CSS          指数退避
```

### 3.3 设计模式应用

| 设计模式 | 应用位置 | 解决的问题 |
|---------|---------|-----------|
| **Template Method** | `BaseCrawler` 基类 | 定义爬虫执行骨架，子类仅实现 `fetch()` 和 `parse()` |
| **Strategy Pattern** | `SummaryGenerator` 输出策略 | HTML 和纯文本两种输出格式可切换 |
| **Factory Pattern** | `CrawlerManager` 爬虫注册 | 根据配置动态实例化不同类型的爬虫 |
| **Command Pattern** | CLI 入口 `main.py` | 7 种互斥操作模式的命令分发 |
| **Observer Pattern** | `WorkflowScheduler._job_listener` | 监听 APScheduler 事件，记录任务执行状态 |
| **Decorator Pattern** | `@retry` 装饰器 | 透明地为任意函数添加重试能力 |
| **Facade Pattern** | `ConfigLoader` 配置门面 | 统一封装 YAML、环境变量、默认值三种配置源 |

---

## 四、核心模块详解

### 4.1 数据采集层 — Crawler Plugin Architecture

数据采集层采用**可插拔爬虫插件架构**，以 `BaseCrawler` 抽象基类为核心，定义标准化的采集生命周期：

```
BaseCrawler (ABC)
├── fetch()           # 抽象方法：原始数据获取
├── parse()           # 抽象方法：数据解析与结构化
├── validate_item()   # 数据质量校验（标题长度、URL合法性）
├── filter_items()    # 热度排序 + Top-N 截断
├── run()             # 模板方法：编排完整执行流
└── _respect_rate_limit()  # 令牌桶式频率限制
```

**并行采集引擎**：`CrawlerManager` 基于 `concurrent.futures.ThreadPoolExecutor` 实现多线程并发采集，默认 4 Worker 线程池。采集完成后执行**双重去重策略**：URL 精确匹配 + 标准化标题模糊匹配（去除标点符号、空格、统一大小写）。

#### 信息源矩阵

| 爬虫类型 | 信息源 | 协议 | 数据格式 | 单源容量 |
|---------|-------|------|---------|---------|
| `RSSCrawler` | 新浪新闻、36氪、虎嗅网、少数派 | RSS/Atom | XML | 8-10 条/源 |
| `WeiboCrawler` | 微博热搜榜 | REST API | JSON | 15 条/次 |
| `ZhihuCrawler` | 知乎全站热榜 | REST API | JSON | 10 条/次 |
| `NewsCrawler` | 新浪、网易、腾讯、今日头条 | HTML Scraping | HTML | 10 条/源 |

**容错设计**：
- HTTP 层：`requests.Session` + `urllib3.Retry`（3 次重试，指数退避，针对 429/5xx）
- 业务层：单个爬虫异常不阻塞整体流程，`CrawlerManager.run_all()` 通过 `as_completed` 逐个收集结果
- 频率控制：基于时间戳的请求间隔守卫（`_respect_rate_limit`），默认间隔 3600 秒

### 4.2 智能分析层 — NLP Processing Chain

分析层集成中文 NLP 处理能力，构建了从文本理解到语义提取的完整处理链：

#### 4.2.1 文本分析器 (TextAnalyzer)

基于 **jieba 分词** + **scikit-learn** 构建多维度文本分析能力：

| 分析能力 | 算法实现 | 输出指标 |
|---------|---------|---------|
| **关键词提取** | TF-IDF + TextRank 双算法加权融合（TextRank 权重系数 0.8） | Top-N 关键词及权重 |
| **情感倾向分析** | 正/负向情感词典计数法，阈值判定（>0.6 正面，<0.4 负面） | 情感极性 + 置信度 |
| **热度评分** | 多维评分模型：关键词权重 × 位置因子 + 文本丰富度 + 情感强度 + 数据密度 | 热度分值（0-100） |
| **自动摘要** | 抽取式摘要：句子位置权重 + 长度适中 + 关键词覆盖 + 数字密度 | 3-5 句精炼摘要 |
| **新闻分类** | 8 类关键词匹配计数（科技/财经/社会/娱乐/体育/国际/政治/健康） | 分类标签 |

**领域知识增强**：内置 20 个热点关键词权重表（`突发:2.0`, `震惊:1.8`, `最新:1.5` 等），以及 88 个中文停用词表，在通用 NLP 基础上叠加新闻领域先验知识。

#### 4.2.2 关键词提取器 (KeywordExtractor)

提供 **5 种互补的关键词提取算法**，支持按场景选择或融合使用：

| 算法 | 适用场景 | 技术实现 |
|------|---------|---------|
| TF-IDF | 语料级关键词 | `sklearn.TfidfVectorizer`，ngram_range=(1,2) |
| TextRank | 单文档关键词 | jieba.analyse.textrank，限定词性（n/nr/ns/nt/nz/v/vn） |
| LDA 主题模型 | 主题发现 | `sklearn.LatentDirichletAllocation`，5 主题 × 10 词 |
| 命名实体识别 | 实体抽取 | jieba 词性标注（人名/地名/机构/时间/数字） |
| N-gram 短语 | 上下文短语 | 2-gram + 3-gram，频率 × 长度加权 |

### 4.3 内容生成层 — Template Rendering Engine

生成层采用 **Jinja2 模板引擎** 实现数据到富文本的结构化渲染，支持 HTML 和纯文本双输出模式：

**HTML 输出特性**：
- 响应式布局设计，兼容移动端阅读
- 内联 CSS 样式，确保邮件客户端渲染一致性
- 分类卡片式展示，热度标签高亮
- 统计概览面板（总条目数、分类数、信息源数、关键词数）
- 自动生成日期、星期、年份等上下文变量

**纯文本输出**：作为 HTML 邮件的 `alternative` 备选部分，确保所有邮件客户端均可正常阅读。

**智能截断算法**：在目标长度的 70% 位置后寻找句号断句，避免在词语中间截断导致语义破碎。

### 4.4 分发层 — Email Distribution System

邮件分发模块基于 Python 标准库 `smtplib` 实现，支持 SMTP/TLS 加密传输：

**核心能力**：
- HTML + 纯文本 `multipart/alternative` 双格式发送
- 附件支持：MIMEBase + base64 编码
- 发送前完整性校验（`_can_send`）
- 30 秒 SMTP 连接超时控制
- 分级异常捕获：`SMTPAuthenticationError` → `SMTPConnectError` → `SMTPException` → 通用异常
- `finally` 块确保连接资源释放

**安全特性**：
- 邮箱地址脱敏显示（前 3 字符 + `***` + @域名）
- 敏感信息通过环境变量注入，日志中不泄露

### 4.5 调度引擎 — Workflow Orchestration

基于 **APScheduler** 的 `BackgroundScheduler` 实现后台常驻定时调度：

**调度策略**：
- Cron 表达式驱动，默认 `0 19 * * *`（每日 19:00）
- `CronTrigger.from_crontab()` 标准 cron 解析
- 支持运行时动态更新调度计划（`reschedule_job`）
- 事件监听器（`EVENT_JOB_ERROR | EVENT_JOB_EXECUTED`）实时记录执行状态

**故障恢复**：
- 任务级重试：失败后自动重试 3 次，间隔 300 秒
- 信号处理：注册 SIGINT/SIGTERM 信号处理器，确保优雅退出

---

## 五、技术栈全景

### 核心依赖

| 技术领域 | 选型方案 | 版本约束 | 选型理由 |
|---------|---------|---------|---------|
| **HTTP 客户端** | requests | ≥2.31.0 | 成熟稳定，Session 管理 + Retry 适配器 |
| **HTML 解析** | BeautifulSoup4 + lxml | ≥4.12.0 / ≥4.9.0 | 双引擎：bs4 API 易用性 + lxml 解析性能 |
| **RSS 解析** | feedparser | ≥6.0.0 | RSS 2.0 / Atom 1.0 全协议支持 |
| **中文分词** | jieba | ≥0.42.1 | 中文分词事实标准，内置 TF-IDF/TextRank |
| **机器学习** | scikit-learn | ≥1.3.0 | TF-IDF 向量化 + LDA 主题模型 |
| **任务调度** | APScheduler | ≥3.10.0 | 轻量级，支持 Cron/Interval/Date 三种触发器 |
| **模板引擎** | Jinja2 | ≥3.1.2 | 沙盒执行环境，自定义过滤器扩展 |
| **数据验证** | Pydantic V2 + pydantic-settings | ≥2.0.0 | 声明式配置验证 + 环境变量自动映射 |
| **日志框架** | loguru | ≥0.7.0 | 结构化日志 + 文件轮转 + 标准库桥接 |
| **配置管理** | PyYAML + python-dotenv | ≥6.0 / ≥1.0.0 | YAML 人类可读 + .env 敏感信息隔离 |

### 工程化工具链

| 工具类别 | 工具选型 | 用途 |
|---------|---------|------|
| 代码格式化 | Black + isort | 统一代码风格，减少 Code Review 摩擦 |
| 静态分析 | Flake8 + MyPy | Lint 检查 + 类型安全 |
| 测试框架 | pytest + pytest-cov + pytest-mock | 单元测试 + 覆盖率度量 + Mock 注入 |
| 容器化 | Docker + Docker Compose | 环境一致性 + 双模式部署 |
| CI/CD | GitHub Actions | 6 阶段流水线（lint → test → integration → build → publish → deploy） |

---

## 六、配置管理体系

### 多源配置合并策略

系统采用**三层配置合并**机制，优先级从高到低：

```
环境变量 (HOTNEWS_*)  ──最高优先级──▶  覆盖
       ↑
.env 文件 (python-dotenv)              注入
       ↑
YAML 配置 (settings.yaml + sources.yaml)  基础
       ↑
代码默认值 (Pydantic Field(default=...))  兜底
```

### 配置安全设计

- **环境变量替换**：`ConfigLoader._substitute_env_vars()` 递归解析 `${VAR_NAME}` 格式，支持嵌套 dict/list 深层替换
- **敏感信息隔离**：邮箱密码、API 密钥等仅通过环境变量注入，YAML 中使用 `${EMAIL_PASSWORD}` 占位符
- **显示脱敏**：`show-config` 命令自动将 `sender_password` 输出为 `***`
- **强类型验证**：Pydantic V2 模型对配置进行类型校验、范围约束和 cron 表达式格式验证

---

## 七、质量保障体系

### 测试策略

| 测试层级 | 覆盖范围 | 测试用例数 |
|---------|---------|-----------|
| **单元测试** | NewsItem 模型、BaseCrawler 基类、TextAnalyzer、ConfigLoader、Retry 装饰器 | 47 |
| **集成测试** | 完整工作流（采集→分析→生成→分发）端到端验证 | 已编写 |
| **矩阵测试** | Python 3.8 / 3.9 / 3.10 / 3.11 / 3.12 多版本兼容性 | CI 自动化 |

### CI/CD 流水线

```
push/PR to main/develop
        │
        ├──▶ [lint] Black + isort + Flake8 + MyPy
        │
        ├──▶ [test] pytest (Python 3.8-3.12 矩阵) + Codecov 覆盖率上报
        │
        └──▶ [integration-test] 端到端验证
                │
                ▼
        [build] Docker Buildx 构建 + 推送 Docker Hub
                │
                ▼
        [publish] twine 上传 PyPI（仅 release 事件）
                │
                ▼
        [deploy] 生产环境部署（SSH/kubectl/docker-compose）
```

---

## 八、部署方案

### 方案一：Docker Compose 部署（推荐）

```bash
git clone https://github.com/848ttff/redian.git
cd redian
cp config/settings.yaml config/settings.local.yaml  # 编辑本地配置
docker-compose up -d
```

**双运行模式**：
- **常驻模式**（默认）：内置 APScheduler 调度器，后台常驻进程
- **Cron 模式**：`docker-compose --profile cron up -d`，由外部 cron 触发执行

**资源约束**：CPU 0.5-1.0 核，内存 256M-512M
**健康检查**：30 秒间隔，Python 导入测试，启动等待 40 秒
**数据持久化**：挂载 `config/`、`logs/`、`output/` 三个卷

### 方案二：系统服务部署

```ini
# /etc/systemd/system/hotnews.service
[Unit]
Description=HotNews Agent Service
After=network.target

[Service]
Type=simple
EnvironmentFile=/opt/hotnews/.env
ExecStart=/opt/hotnews/venv/bin/python -m src.main --start-scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 方案三：Kubernetes 部署

支持通过 Helm Chart 或原生 YAML 部署至 K8s 集群，利用 CronJob 资源实现定时调度。

---

## 九、项目创新点与技术优势

### 9.1 架构创新

1. **可插拔爬虫插件体系**：基于抽象基类 + 工厂注册表的设计，新增信息源仅需继承 `BaseCrawler` 并注册类型映射，零侵入式扩展，开闭原则（OCP）落地实践
2. **双算法融合的关键词提取**：TF-IDF（统计特征）+ TextRank（图排序特征）加权融合，叠加领域热点词典，兼顾通用性与领域特异性
3. **三层容错体系**：HTTP 层（urllib3 Retry）、函数层（`@retry` 装饰器 + 指数退避）、业务层（爬虫故障隔离 + 邮件发送重试），确保系统在部分组件故障时仍可降级运行

### 9.2 工程化优势

4. **配置即代码（Configuration as Code）**：YAML 声明式配置 + Pydantic 强类型验证 + 环境变量注入，配置变更无需修改代码，支持 Git 版本化管理
5. **双模容器化部署**：APScheduler 常驻模式与 Cron 触发模式通过 `docker-compose profiles` 一键切换，适配不同运维场景
6. **端到端 CI/CD**：6 阶段 GitHub Actions 流水线覆盖代码质量检查、多版本矩阵测试、Docker 镜像构建推送、PyPI 发布和生产部署

### 9.3 安全设计

7. **敏感信息零硬编码**：所有凭证通过 `${ENV_VAR}` 占位符引用 + Pydantic `env_prefix` 自动映射，代码仓库中不包含任何明文密钥
8. **频率控制守卫**：每个爬虫配置独立的请求间隔（`interval`），基于时间戳的请求节流机制，遵守 robots.txt 精神，避免对目标站点造成 DDoS 式访问压力

---

## 十、快速开始

### 环境要求

- Python 3.8+（推荐 3.11）
- pip 或 conda 包管理器
- SMTP 邮箱账号（QQ 邮箱 / 163 邮箱 / 企业邮箱等）

### 5 分钟快速上手

```bash
# 1. 克隆仓库
git clone https://github.com/848ttff/redian.git && cd redian

# 2. 创建虚拟环境
python -m venv venv && source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
export EMAIL_SENDER="your-email@qq.com"
export EMAIL_PASSWORD="your-smtp-auth-code"

# 5. 查看当前配置
python -m src.main --show-config

# 6. 列出所有信息源
python -m src.main --list-crawlers

# 7. 手动执行一次采集
python -m src.main --run-once

# 8. 启动定时调度（每日 19:00 自动执行）
python -m src.main --start-scheduler
```

### CLI 命令参考

| 命令 | 说明 |
|------|------|
| `--run-once` | 手动执行一次完整的采集→分析→生成→分发流程 |
| `--start-scheduler` | 启动后台定时调度器（Cron: 每日 19:00） |
| `--test-email` | 发送测试邮件验证 SMTP 配置 |
| `--test-connection` | 测试 SMTP 服务器连接性 |
| `--show-config` | 显示当前生效配置（密码自动脱敏） |
| `--list-crawlers` | 列出所有已注册并启用的爬虫实例 |
| `--create-config` | 生成示例配置文件 |
| `--config-dir` | 指定配置文件目录路径 |
| `--log-level` | 设置日志级别（DEBUG/INFO/WARNING/ERROR） |
| `--log-dir` | 指定日志文件输出目录 |

---

## 十一、扩展指南

### 新增信息源

```python
# src/crawlers/custom_crawler.py
from src.crawlers.base import BaseCrawler, NewsItem
from typing import List, Any, Dict

class CustomCrawler(BaseCrawler):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = config.get("api_url", "")

    def fetch(self) -> List[NewsItem]:
        raw_data = self.fetch_page(self.api_url)
        return self.parse(raw_data)

    def parse(self, raw_data: Any) -> List[NewsItem]:
        # 实现数据解析逻辑
        items = []
        # ... 解析代码 ...
        return items
```

在 `CrawlerManager.CRAWLER_TYPES` 中注册后即可通过 YAML 配置启用。

### 自定义输出模板

在 `config/templates/` 目录下创建 Jinja2 模板文件，可用变量包括：
- `categorized_news` — 按分类组织的新闻列表
- `top_keywords` — 全局 Top 关键词
- `statistics` — 统计信息（总数、分类数、源数）
- `date_str` / `weekday` / `year` — 日期上下文

---

## 十二、项目统计

| 指标 | 数值 |
|------|------|
| 源代码文件数 | 24 |
| 配置与文档文件数 | 25 |
| 总代码行数 | 9,459 |
| 单元测试用例数 | 47 (100% 通过) |
| 信息源数量 | 11 |
| NLP 算法数量 | 7 |
| 设计模式应用数 | 7 |
| CI/CD 阶段数 | 6 |

---

## 十三、许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

---

<div align="center">

**HotNews Agent** — 让信息采集从重复劳动变为智能流水线

[![GitHub](https://img.shields.io/badge/GitHub-848ttff%2Fredian-181717?logo=github)](https://github.com/848ttff/redian)

</div>
