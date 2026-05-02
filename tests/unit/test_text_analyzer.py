"""
文本分析器单元测试
"""

import pytest
from src.analyzers.text_analyzer import TextAnalyzer


class TestTextAnalyzer:
    """
    测试文本分析器
    """
    
    @pytest.fixture
    def analyzer(self):
        """
        文本分析器夹具
        """
        return TextAnalyzer()
    
    def test_init(self, analyzer):
        """
        测试初始化
        """
        assert analyzer is not None
        assert len(analyzer.stop_words) > 0
    
    def test_analyze_text_empty(self, analyzer):
        """
        测试分析空文本
        """
        result = analyzer.analyze_text("")
        assert result == {}
    
    def test_analyze_text_normal(self, analyzer):
        """
        测试分析正常文本
        """
        text = "今日国内经济数据发布，一季度GDP同比增长5.2%，经济运行持续恢复向好。消费市场表现亮眼，新能源汽车销量大增。"
        
        result = analyzer.analyze_text(text)
        
        assert "keywords" in result
        assert "stats" in result
        assert "sentiment" in result
        assert "hot_score" in result
        assert result["char_count"] == len(text)
    
    def test_extract_keywords(self, analyzer):
        """
        测试提取关键词
        """
        text = "人工智能技术发展迅速，GPT-5发布引发热议。AI在各行业的应用越来越广泛，科技创新成为发展动力。"
        
        keywords = analyzer.extract_keywords(text, top_k=5)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        
        for keyword, weight in keywords:
            assert isinstance(keyword, str)
            assert isinstance(weight, float)
            assert weight > 0
    
    def test_extract_keywords_empty(self, analyzer):
        """
        测试从空文本提取关键词
        """
        keywords = analyzer.extract_keywords("")
        assert keywords == []
    
    def test_generate_summary(self, analyzer):
        """
        测试生成摘要
        """
        text = "今日国内经济数据发布。一季度GDP同比增长5.2%。经济运行持续恢复向好。消费市场表现亮眼。新能源汽车销量大增。"
        
        summary = analyzer.generate_summary(text, max_length=30)
        
        assert isinstance(summary, str)
        assert len(summary) <= 30 + 10  # 允许一些误差
    
    def test_generate_summary_short_text(self, analyzer):
        """
        测试对短文本生成摘要
        """
        text = "这是一条短文本。"
        
        summary = analyzer.generate_summary(text, max_length=100)
        
        assert summary == text
    
    def test_generate_summary_empty(self, analyzer):
        """
        测试对空文本生成摘要
        """
        summary = analyzer.generate_summary("")
        assert summary == ""
    
    def test_categorize_news_tech(self, analyzer):
        """
        测试科技类新闻分类
        """
        title = "OpenAI发布GPT-5，人工智能技术取得重大突破"
        content = "人工智能公司OpenAI今日正式发布GPT-5大语言模型。"
        
        category = analyzer.categorize_news(title, content)
        
        assert category == "科技"
    
    def test_categorize_news_finance(self, analyzer):
        """
        测试财经类新闻分类
        """
        title = "A股三大指数全线上涨，沪指突破3500点"
        content = "今日股票市场表现强劲，投资者信心增强。"
        
        category = analyzer.categorize_news(title, content)
        
        assert category == "财经"
    
    def test_categorize_news_general(self, analyzer):
        """
        测试综合类新闻分类
        """
        title = "今日天气预报"
        content = "明天天气晴朗。"
        
        category = analyzer.categorize_news(title, content)
        
        assert category == "综合"
    
    def test_analyze_sentiment_positive(self, analyzer):
        """
        测试正面情感分析
        """
        text = "经济数据表现亮眼，市场信心大增，股市大涨，投资者情绪乐观。"
        
        result = analyzer._analyze_sentiment(text)
        
        assert result["label"] == "正面"
        assert result["score"] > 0.5
    
    def test_analyze_sentiment_negative(self, analyzer):
        """
        测试负面情感分析
        """
        text = "市场出现大幅下跌，投资者恐慌情绪蔓延，风险警示频发。"
        
        result = analyzer._analyze_sentiment(text)
        
        assert result["label"] == "负面"
        assert result["score"] < 0.5
    
    def test_analyze_sentiment_neutral(self, analyzer):
        """
        测试中性情感分析
        """
        text = "今日召开例行新闻发布会。"
        
        result = analyzer._analyze_sentiment(text)
        
        assert result["label"] == "中性"