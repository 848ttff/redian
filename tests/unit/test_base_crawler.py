"""
爬虫基类单元测试
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.crawlers.base import BaseCrawler, NewsItem


class TestNewsItem:
    """
    测试NewsItem数据类
    """
    
    def test_create_news_item(self):
        """
        测试创建新闻条目
        """
        item = NewsItem(
            title="测试标题",
            content="测试内容",
            url="https://example.com",
            source="测试来源"
        )
        
        assert item.title == "测试标题"
        assert item.content == "测试内容"
        assert item.url == "https://example.com"
        assert item.source == "测试来源"
        assert item.category == "综合"
        assert item.popularity == 0
        assert item.keywords == []
        assert item.summary == ""
        assert item.image_url is None
    
    def test_news_item_defaults(self):
        """
        测试新闻条目默认值
        """
        item = NewsItem(
            title="测试",
            content="",
            url="https://example.com",
            source="测试"
        )
        
        assert item.publish_time is None
        assert isinstance(item.keywords, list)
    
    def test_news_item_with_keywords(self):
        """
        测试带关键词的新闻条目
        """
        keywords = ["关键词1", "关键词2"]
        item = NewsItem(
            title="测试",
            content="",
            url="https://example.com",
            source="测试",
            keywords=keywords
        )
        
        assert item.keywords == keywords


class ConcreteCrawler(BaseCrawler):
    """
    具体爬虫实现（用于测试）
    """
    
    def fetch(self):
        return []
    
    def parse(self, raw_data):
        return []


class TestBaseCrawler:
    """
    测试爬虫基类
    """
    
    def test_init_with_config(self):
        """
        测试使用配置初始化
        """
        config = {
            "name": "测试爬虫",
            "enabled": True,
            "max_items": 20,
            "interval": 1800
        }
        
        crawler = ConcreteCrawler(config)
        
        assert crawler.name == "测试爬虫"
        assert crawler.enabled is True
        assert crawler.max_items == 20
        assert crawler.interval == 1800
    
    def test_init_with_default_config(self):
        """
        测试使用默认配置初始化
        """
        config = {}
        crawler = ConcreteCrawler(config)
        
        assert crawler.enabled is True
        assert crawler.max_items == 10
        assert crawler.interval == 3600
    
    def test_validate_item_valid(self):
        """
        测试验证有效条目
        """
        config = {}
        crawler = ConcreteCrawler(config)
        
        item = NewsItem(
            title="有效的新闻标题",
            content="内容",
            url="https://example.com",
            source="来源"
        )
        
        assert crawler.validate_item(item) is True
    
    def test_validate_item_empty_title(self):
        """
        测试验证空标题条目
        """
        config = {}
        crawler = ConcreteCrawler(config)
        
        item = NewsItem(
            title="",
            content="内容",
            url="https://example.com",
            source="来源"
        )
        
        assert crawler.validate_item(item) is False
    
    def test_validate_item_short_title(self):
        """
        测试验证短标题条目
        """
        config = {}
        crawler = ConcreteCrawler(config)
        
        item = NewsItem(
            title="短",
            content="内容",
            url="https://example.com",
            source="来源"
        )
        
        assert crawler.validate_item(item) is False
    
    def test_validate_item_no_url(self):
        """
        测试验证无URL条目
        """
        config = {}
        crawler = ConcreteCrawler(config)
        
        item = NewsItem(
            title="有效标题",
            content="内容",
            url="",
            source="来源"
        )
        
        assert crawler.validate_item(item) is False
    
    def test_filter_items(self):
        """
        测试过滤条目
        """
        config = {"max_items": 2}
        crawler = ConcreteCrawler(config)
        
        items = [
            NewsItem(title="这是第一个有效标题", content="", url="https://1.com", source="来源", popularity=10),
            NewsItem(title="这是第二个有效标题", content="", url="https://2.com", source="来源", popularity=20),
            NewsItem(title="这是第三个有效标题", content="", url="https://3.com", source="来源", popularity=30),
            NewsItem(title="", content="", url="https://4.com", source="来源", popularity=40),  # 无效
        ]
        
        filtered = crawler.filter_items(items)
        
        assert len(filtered) == 2
        assert filtered[0].title == "这是第三个有效标题"  # 按热度排序
        assert filtered[1].title == "这是第二个有效标题"
    
    def test_run_disabled(self):
        """
        测试禁用爬虫运行
        """
        config = {"enabled": False}
        crawler = ConcreteCrawler(config)
        
        result = crawler.run()
        
        assert result == []