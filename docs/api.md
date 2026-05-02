# API文档

## 概述

本文档描述热点信息自动收集与处理系统的主要API接口和类定义。

## 核心类

### 1. NewsItem (数据模型)

新闻条目数据结构，定义在 `src/crawlers/base.py`。

```python
@dataclass
class NewsItem:
    title: str                    # 标题
    content: str                  # 内容
    url: str                      # 链接
    source: str                   # 来源
    category: str = "综合"        # 分类
    publish_time: Optional[datetime] = None  # 发布时间
    popularity: int = 0           # 热度
    keywords: List[str] = None    # 关键词
    summary: str = ""             # 摘要
    image_url: Optional[str] = None  # 图片链接
```

**使用示例**:

```python
from src.crawlers.base import NewsItem
from datetime import datetime

item = NewsItem(
    title="测试新闻标题",
    content="测试新闻内容",
    url="https://example.com/news/1",
    source="测试来源",
    category="新闻",
    publish_time=datetime.now(),
    popularity=85,
    keywords=["测试", "新闻"]
)
```

### 2. BaseCrawler (爬虫基类)

爬虫基类，定义在 `src/crawlers/base.py`。

**主要方法**:

```python
class BaseCrawler(ABC):
    def __init__(self, config: Dict[str, Any]):
        """初始化爬虫"""
        pass
    
    @abstractmethod
    def fetch(self) -> List[NewsItem]:
        """获取新闻列表"""
        pass
    
    @abstractmethod
    def parse(self, raw_data: Any) -> List[NewsItem]:
        """解析原始数据"""
        pass
    
    def validate_item(self, item: NewsItem) -> bool:
        """验证新闻条目"""
        pass
    
    def filter_items(self, items: List[NewsItem]) -> List[NewsItem]:
        """过滤新闻条目"""
        pass
    
    def run(self) -> List[NewsItem]:
        """执行完整的爬取流程"""
        pass
```

**自定义爬虫示例**:

```python
from src.crawlers.base import BaseCrawler, NewsItem
from typing import List, Any

class MyCrawler(BaseCrawler):
    def fetch(self) -> List[NewsItem]:
        # 实现获取逻辑
        response = self.fetch_page("https://example.com/api")
        if response:
            return self.parse(response.json())
        return []
    
    def parse(self, raw_data: Any) -> List[NewsItem]:
        # 实现解析逻辑
        items = []
        for data in raw_data:
            items.append(NewsItem(
                title=data["title"],
                content=data["content"],
                url=data["url"],
                source=self.name
            ))
        return items
```

### 3. CrawlerManager (爬虫管理器)

爬虫管理器，定义在 `src/crawlers/manager.py`。

**主要方法**:

```python
class CrawlerManager:
    def __init__(self, config: Dict[str, Any]):
        """初始化爬虫管理器"""
        pass
    
    def add_crawler(self, crawler: BaseCrawler):
        """添加爬虫实例"""
        pass
    
    def remove_crawler(self, crawler_name: str):
        """移除爬虫实例"""
        pass
    
    def run_all(self) -> List[NewsItem]:
        """执行所有爬虫并收集结果"""
        pass
    
    def run_single(self, crawler_name: str) -> List[NewsItem]:
        """执行单个爬虫"""
        pass
    
    def list_crawlers(self) -> List[Dict[str, Any]]:
        """列出所有爬虫信息"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取爬虫统计信息"""
        pass
```

**使用示例**:

```python
from src.crawlers import CrawlerManager

config = {
    "sources": {
        "rss_feeds": {
            "enabled": True,
            "sources": [...]
        }
    }
}

manager = CrawlerManager(config)
news_items = manager.run_all()
```

### 4. TextAnalyzer (文本分析器)

文本分析器，定义在 `src/analyzers/text_analyzer.py`。

**主要方法**:

```python
class TextAnalyzer:
    def __init__(self, config: Dict[str, Any] = None):
        """初始化文本分析器"""
        pass
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """分析文本内容"""
        pass
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """提取文本关键词"""
        pass
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成文本摘要"""
        pass
    
    def categorize_news(self, title: str, content: str = "") -> str:
        """对新闻进行分类"""
        pass
```

**使用示例**:

```python
from src.analyzers import TextAnalyzer

analyzer = TextAnalyzer()

# 分析文本
result = analyzer.analyze_text("今日国内经济数据发布...")
print(result["keywords"])
print(result["sentiment"])

# 提取关键词
keywords = analyzer.extract_keywords("人工智能技术发展迅速...", top_k=5)
for keyword, weight in keywords:
    print(f"{keyword}: {weight:.4f}")

# 生成摘要
summary = analyzer.generate_summary("长文本...", max_length=100)
print(summary)

# 新闻分类
category = analyzer.categorize_news("OpenAI发布GPT-5")
print(category)  # 输出: 科技
```

### 5. SummaryGenerator (总结生成器)

总结生成器，定义在 `src/summarizers/summary_generator.py`。

**主要方法**:

```python
class SummaryGenerator:
    def __init__(self, config: Dict[str, Any] = None):
        """初始化总结生成器"""
        pass
    
    def generate(self, news_items: List[Any], metadata: Dict[str, Any] = None) -> str:
        """生成公众号格式的总结"""
        pass
    
    def generate_text_summary(self, news_items: List[Any]) -> str:
        """生成纯文本格式的总结"""
        pass
    
    def get_statistics(self, news_items: List[Any]) -> Dict[str, Any]:
        """获取新闻统计信息"""
        pass
```

**使用示例**:

```python
from src.summarizers import SummaryGenerator

generator = SummaryGenerator()

# 生成HTML总结
html = generator.generate(news_items)
with open("summary.html", "w", encoding="utf-8") as f:
    f.write(html)

# 生成文本总结
text = generator.generate_text_summary(news_items)
print(text)

# 获取统计信息
stats = generator.get_statistics(news_items)
print(f"总条目: {stats['total_items']}")
print(f"分类数: {stats['total_categories']}")
```

### 6. EmailSender (邮件发送器)

邮件发送器，定义在 `src/mailers/email_sender.py`。

**主要方法**:

```python
class EmailSender:
    def __init__(self, config: Dict[str, Any]):
        """初始化邮件发送器"""
        pass
    
    def send(self, subject: str, html_content: str, text_content: str = None) -> bool:
        """发送邮件"""
        pass
    
    def send_with_attachment(
        self, 
        subject: str, 
        html_content: str, 
        attachments: List[Dict[str, str]] = None,
        text_content: str = None
    ) -> bool:
        """发送带附件的邮件"""
        pass
    
    def test_connection(self) -> bool:
        """测试SMTP连接"""
        pass
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        pass
```

**使用示例**:

```python
from src.mailers import EmailSender

config = {
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "use_tls": True,
    "sender_email": "sender@example.com",
    "sender_password": "password",
    "sender_name": "热点资讯日报",
    "recipients": ["recipient@example.com"]
}

sender = EmailSender(config)

# 测试连接
if sender.test_connection():
    print("连接成功")

# 发送邮件
success = sender.send(
    subject="今日热点资讯",
    html_content="<html>...</html>",
    text_content="纯文本内容"
)

if success:
    print("发送成功")
```

### 7. WorkflowScheduler (工作流调度器)

工作流调度器，定义在 `src/schedulers/workflow_scheduler.py`。

**主要方法**:

```python
class WorkflowScheduler:
    def __init__(self, config: Dict[str, Any]):
        """初始化工作流调度器"""
        pass
    
    def start(self):
        """启动调度器"""
        pass
    
    def stop(self):
        """停止调度器"""
        pass
    
    def run_workflow(self):
        """执行完整的工作流程"""
        pass
    
    def run_once(self):
        """手动执行一次工作流"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        pass
    
    def update_schedule(self, cron_expression: str):
        """更新调度计划"""
        pass
```

**使用示例**:

```python
from src.schedulers import WorkflowScheduler

config = {
    "scheduler": {
        "enabled": True,
        "cron_expression": "0 19 * * *"
    },
    "email": {...},
    "sources": {...},
    "content": {...}
}

scheduler = WorkflowScheduler(config)

# 手动执行一次
scheduler.run_once()

# 启动定时任务
scheduler.start()

# 获取状态
status = scheduler.get_status()
print(f"运行状态: {status['is_running']}")

# 更新调度计划
scheduler.update_schedule("0 20 * * *")

# 停止调度器
scheduler.stop()
```

### 8. ConfigLoader (配置加载器)

配置加载器，定义在 `src/config/loader.py`。

**主要方法**:

```python
class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        """初始化配置加载器"""
        pass
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """加载YAML配置文件"""
        pass
    
    def load_config(self) -> Dict[str, Any]:
        """加载完整配置"""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置"""
        pass
    
    def create_example_config(self):
        """创建示例配置文件"""
        pass
```

**使用示例**:

```python
from src.config import ConfigLoader

loader = ConfigLoader("config")

# 加载配置
config = loader.load_config()

# 验证配置
validation = loader.validate_config(config)
if validation["valid"]:
    print("配置有效")
else:
    print(f"配置错误: {validation['errors']}")

# 创建示例配置
loader.create_example_config()
```

## 命令行接口

### 主程序入口

```bash
python -m src.main [选项]
```

**可用选项**:

| 选项 | 说明 |
|------|------|
| `--run-once` | 手动执行一次收集任务 |
| `--start-scheduler` | 启动定时任务调度器 |
| `--test-email` | 测试邮件发送 |
| `--test-connection` | 测试SMTP连接 |
| `--create-config` | 创建示例配置文件 |
| `--show-config` | 显示当前配置 |
| `--list-crawlers` | 列出所有可用的爬虫 |
| `--config-dir DIR` | 配置文件目录 |
| `--log-level LEVEL` | 日志级别 |
| `--log-dir DIR` | 日志目录 |

**使用示例**:

```bash
# 手动执行一次
python -m src.main --run-once

# 启动调度器
python -m src.main --start-scheduler

# 测试邮件
python -m src.main --test-email

# 查看配置
python -m src.main --show-config

# 列出爬虫
python -m src.main --list-crawlers
```

## 错误处理

### 异常类型

系统定义了以下异常类型：

```python
class CrawlerError(Exception):
    """爬虫错误"""
    pass

class ConfigError(Exception):
    """配置错误"""
    pass

class EmailError(Exception):
    """邮件发送错误"""
    pass
```

### 重试机制

系统支持自动重试机制：

```python
from src.utils.retry import retry

@retry(max_attempts=3, delay=1.0, backoff=2.0)
def risky_operation():
    # 可能失败的操作
    pass
```

## 配置参考

### 配置结构

```yaml
system:
  name: "系统名称"
  version: "版本号"
  log_level: "日志级别"
  timezone: "时区"

scheduler:
  enabled: true
  cron_expression: "cron表达式"
  retry_count: 3
  retry_delay: 300

email:
  enabled: true
  smtp_server: "SMTP服务器"
  smtp_port: 587
  use_tls: true
  sender_name: "发件人名称"
  sender_email: "发件人邮箱"
  sender_password: "发件人密码"
  recipients: ["收件人列表"]

content:
  max_items_per_source: 10
  total_max_items: 30
  template: "模板文件名"

sources:
  rss_feeds:
    enabled: true
    sources: [...]
  social_media:
    enabled: true
    weibo: {...}
    zhihu: {...}
  news_sites:
    enabled: true
    sites: [...]
```