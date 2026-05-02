"""
工作流集成测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.crawlers.base import NewsItem
from src.summarizers.summary_generator import SummaryGenerator
from src.schedulers.workflow_scheduler import WorkflowScheduler


class TestWorkflowIntegration:
    """
    测试工作流集成
    """
    
    @pytest.fixture
    def sample_news_items(self):
        """
        示例新闻数据
        """
        return [
            NewsItem(
                title="测试新闻标题1",
                content="这是测试新闻内容1，用于集成测试。",
                url="https://example.com/news/1",
                source="测试来源",
                category="新闻",
                publish_time=datetime.now(),
                popularity=95,
                keywords=["测试", "新闻"]
            ),
            NewsItem(
                title="测试科技新闻",
                content="这是测试科技新闻内容。",
                url="https://example.com/tech/1",
                source="测试来源",
                category="科技",
                publish_time=datetime.now(),
                popularity=90,
                keywords=["科技", "测试"]
            ),
            NewsItem(
                title="测试财经新闻",
                content="这是测试财经新闻内容。",
                url="https://example.com/finance/1",
                source="测试来源",
                category="财经",
                publish_time=datetime.now(),
                popularity=85,
                keywords=["财经", "测试"]
            )
        ]
    
    def test_summary_generator(self, sample_config, sample_news_items):
        """
        测试总结生成器
        """
        generator = SummaryGenerator(sample_config.get("content", {}))
        
        html = generator.generate(sample_news_items)
        
        assert isinstance(html, str)
        assert len(html) > 0
        assert "测试新闻标题1" in html
        assert "测试科技新闻" in html
    
    def test_summary_generator_empty(self, sample_config):
        """
        测试空数据的总结生成
        """
        generator = SummaryGenerator(sample_config.get("content", {}))
        
        html = generator.generate([])
        
        assert isinstance(html, str)
        assert len(html) > 0
        assert "暂无热点信息" in html
    
    def test_summary_generator_text_format(self, sample_config, sample_news_items):
        """
        测试文本格式总结
        """
        generator = SummaryGenerator(sample_config.get("content", {}))
        
        text = generator.generate_text_summary(sample_news_items)
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert "测试新闻标题1" in text
    
    def test_summary_statistics(self, sample_config, sample_news_items):
        """
        测试总结统计信息
        """
        generator = SummaryGenerator(sample_config.get("content", {}))
        
        stats = generator.get_statistics(sample_news_items)
        
        assert stats["total_items"] == 3
        assert stats["total_categories"] == 3
        assert "新闻" in stats["category_distribution"]
        assert "科技" in stats["category_distribution"]
    
    @patch('src.schedulers.workflow_scheduler.CrawlerManager')
    @patch('src.schedulers.workflow_scheduler.EmailSender')
    def test_workflow_scheduler_init(self, mock_email, mock_crawler, sample_config):
        """
        测试工作流调度器初始化
        """
        scheduler = WorkflowScheduler(sample_config)
        
        assert scheduler is not None
        assert scheduler.enabled == sample_config["scheduler"]["enabled"]
    
    @patch('src.schedulers.workflow_scheduler.CrawlerManager')
    @patch('src.schedulers.workflow_scheduler.EmailSender')
    def test_workflow_scheduler_status(self, mock_email, mock_crawler, sample_config):
        """
        测试获取调度器状态
        """
        scheduler = WorkflowScheduler(sample_config)
        
        status = scheduler.get_status()
        
        assert "is_running" in status
        assert "enabled" in status
        assert "cron_expression" in status
    
    def test_categorize_and_summarize(self, sample_config, sample_news_items):
        """
        测试分类和总结流程
        """
        from src.analyzers.text_analyzer import TextAnalyzer
        
        analyzer = TextAnalyzer()
        
        # 分析每条新闻
        for item in sample_news_items:
            analysis = analyzer.analyze_text(item.title + " " + item.content)
            assert "keywords" in analysis
            assert "sentiment" in analysis
        
        # 生成总结
        generator = SummaryGenerator(sample_config.get("content", {}))
        html = generator.generate(sample_news_items)
        
        # 验证总结包含所有分类
        assert "新闻" in html
        assert "科技" in html
        assert "财经" in html