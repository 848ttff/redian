"""
测试配置文件
提供测试夹具和配置
"""

import os
import sys
import pytest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_config():
    """
    示例配置夹具
    """
    return {
        "system": {
            "name": "测试系统",
            "version": "1.0.0",
            "log_level": "DEBUG",
            "timezone": "Asia/Shanghai"
        },
        "scheduler": {
            "enabled": False,
            "cron_expression": "0 19 * * *",
            "retry_count": 3,
            "retry_delay": 5
        },
        "email": {
            "enabled": False,
            "smtp_server": "smtp.test.com",
            "smtp_port": 587,
            "use_tls": True,
            "sender_name": "测试发件人",
            "sender_email": "test@example.com",
            "sender_password": "test_password",
            "recipients": ["recipient@example.com"],
            "retry_count": 1,
            "retry_delay": 1
        },
        "content": {
            "max_items_per_source": 5,
            "total_max_items": 10,
            "summary_length": 200,
            "content_max_length": 100,
            "template": "daily_summary.html",
            "title": "测试热点资讯"
        },
        "sources": {
            "rss_feeds": {
                "enabled": False,
                "sources": []
            },
            "social_media": {
                "enabled": False,
                "weibo": {"enabled": False},
                "zhihu": {"enabled": False}
            },
            "news_sites": {
                "enabled": False,
                "sites": []
            }
        }
    }


@pytest.fixture
def sample_news_item():
    """
    示例新闻条目夹具
    """
    from src.crawlers.base import NewsItem
    from datetime import datetime
    
    return NewsItem(
        title="测试新闻标题",
        content="这是一条测试新闻的内容，用于单元测试。",
        url="https://example.com/news/1",
        source="测试来源",
        category="测试",
        publish_time=datetime.now(),
        popularity=85,
        keywords=["测试", "新闻", "单元测试"]
    )


@pytest.fixture
def sample_news_items():
    """
    示例新闻列表夹具
    """
    from src.crawlers.base import NewsItem
    from datetime import datetime
    
    items = []
    
    # 新闻类
    items.append(NewsItem(
        title="国内经济持续恢复向好",
        content="一季度国内生产总值同比增长5.2%，经济运行持续恢复向好。",
        url="https://example.com/news/1",
        source="新浪新闻",
        category="新闻",
        publish_time=datetime.now(),
        popularity=95,
        keywords=["经济", "GDP", "增长"]
    ))
    
    # 科技类
    items.append(NewsItem(
        title="OpenAI发布最新AI模型",
        content="OpenAI今日发布最新AI模型，性能大幅提升。",
        url="https://example.com/tech/1",
        source="36氪",
        category="科技",
        publish_time=datetime.now(),
        popularity=98,
        keywords=["AI", "OpenAI", "人工智能"]
    ))
    
    # 社交媒体类
    items.append(NewsItem(
        title="#今日热点话题#",
        content="微博热搜话题引发广泛讨论。",
        url="https://weibo.com/hot/1",
        source="微博热搜",
        category="社交媒体",
        publish_time=datetime.now(),
        popularity=90,
        keywords=["热搜", "微博", "话题"]
    ))
    
    return items


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    模拟环境变量夹具
    """
    monkeypatch.setenv("EMAIL_SENDER", "test@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "test_password")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def temp_dir(tmp_path):
    """
    临时目录夹具
    """
    return tmp_path