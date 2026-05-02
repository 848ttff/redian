"""
总结生成器模块
负责将新闻数据转换为公众号格式的总结
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

from .template_engine import TemplateEngine

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """
    总结生成器
    将新闻数据转换为公众号格式的总结
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化总结生成器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 模板配置
        self.template_name = self.config.get("template", "daily_summary.html")
        self.max_items_per_category = self.config.get("max_items_per_category", 5)
        self.max_total_items = self.config.get("max_total_items", 30)
        self.content_max_length = self.config.get("content_max_length", 150)
        
        # 初始化模板引擎
        self.template_engine = TemplateEngine(self.config)
        
        # 确保默认模板存在
        self.template_engine.create_default_template(self.template_name)
        
        logger.info("总结生成器初始化完成")
    
    def generate(self, news_items: List[Any], metadata: Dict[str, Any] = None) -> str:
        """
        生成公众号格式的总结
        
        Args:
            news_items: 新闻条目列表
            metadata: 元数据（可选）
            
        Returns:
            str: 生成的HTML总结
        """
        if not news_items:
            logger.warning("没有新闻数据可生成总结")
            return self._generate_empty_summary()
        
        try:
            logger.info(f"开始生成总结，共 {len(news_items)} 条新闻")
            
            # 按分类组织新闻
            categorized_news = self._categorize_news(news_items)
            
            # 提取关键词
            keywords = self._extract_top_keywords(news_items)
            
            # 准备模板数据
            template_data = self._prepare_template_data(
                categorized_news, 
                keywords, 
                metadata
            )
            
            # 渲染模板
            html_content = self.template_engine.render(
                self.template_name, 
                template_data
            )
            
            logger.info("总结生成完成")
            return html_content
            
        except Exception as e:
            logger.error(f"生成总结失败: {e}", exc_info=True)
            return self._generate_error_summary(str(e))
    
    def _categorize_news(self, news_items: List[Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        将新闻按分类组织
        
        Args:
            news_items: 新闻条目列表
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 分类到新闻列表的映射
        """
        categorized = defaultdict(list)
        
        for item in news_items:
            # 获取分类
            category = getattr(item, 'category', '综合')
            if not category:
                category = '综合'
            
            # 转换为字典格式
            news_dict = {
                "title": self._clean_text(getattr(item, 'title', '')),
                "content": self._truncate_content(getattr(item, 'content', '')),
                "url": getattr(item, 'url', ''),
                "source": getattr(item, 'source', '未知'),
                "popularity": getattr(item, 'popularity', 0),
                "publish_time": getattr(item, 'publish_time', None),
                "keywords": getattr(item, 'keywords', [])
            }
            
            categorized[category].append(news_dict)
        
        # 对每个分类内的新闻按热度排序
        for category in categorized:
            categorized[category].sort(
                key=lambda x: x['popularity'], 
                reverse=True
            )
            # 限制每个分类的新闻数量
            categorized[category] = categorized[category][:self.max_items_per_category]
        
        return dict(categorized)
    
    def _extract_top_keywords(self, news_items: List[Any], top_k: int = 15) -> List[str]:
        """
        提取所有新闻的热门关键词
        
        Args:
            news_items: 新闻条目列表
            top_k: 返回前K个关键词
            
        Returns:
            List[str]: 关键词列表
        """
        keyword_freq = defaultdict(int)
        
        for item in news_items:
            keywords = getattr(item, 'keywords', [])
            for keyword in keywords:
                keyword_freq[keyword] += 1
        
        # 按频率排序
        sorted_keywords = sorted(
            keyword_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [keyword for keyword, _ in sorted_keywords[:top_k]]
    
    def _prepare_template_data(
        self, 
        categorized_news: Dict[str, List[Dict[str, Any]]],
        keywords: List[str],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        准备模板渲染数据
        
        Args:
            categorized_news: 分类后的新闻
            keywords: 关键词列表
            metadata: 元数据
            
        Returns:
            Dict[str, Any]: 模板数据
        """
        # 统计信息
        total_items = sum(len(items) for items in categorized_news.values())
        total_categories = len(categorized_news)
        total_sources = len(set(
            item['source'] 
            for items in categorized_news.values() 
            for item in items
        ))
        
        # 组织分类数据
        categories = []
        category_order = self._get_category_order()
        
        # 按照预定义顺序添加分类
        for category_name in category_order:
            if category_name in categorized_news:
                categories.append({
                    "name": category_name,
                    "items": categorized_news[category_name]
                })
        
        # 添加其他未在预定义顺序中的分类
        for category_name, items in categorized_news.items():
            if category_name not in category_order:
                categories.append({
                    "name": category_name,
                    "items": items
                })
        
        # 构建模板数据
        template_data = {
            "title": self.config.get("title", "今日热点资讯"),
            "total_items": total_items,
            "total_categories": total_categories,
            "total_sources": total_sources,
            "categories": categories,
            "keywords": keywords,
            "metadata": metadata or {}
        }
        
        return template_data
    
    def _get_category_order(self) -> List[str]:
        """
        获取分类显示顺序
        
        Returns:
            List[str]: 分类名称列表
        """
        return [
            "新闻", "科技", "财经", "社会", "娱乐", 
            "体育", "国际", "政治", "健康", "综合",
            "社交媒体", "问答社区", "资讯"
        ]
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        if not text:
            return ""
        
        import re
        
        # 移除HTML标签
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余空白
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # 移除特殊字符
        clean_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', clean_text)
        
        return clean_text
    
    def _truncate_content(self, content: str) -> str:
        """
        截断内容到指定长度
        
        Args:
            content: 原始内容
            
        Returns:
            str: 截断后的内容
        """
        if not content:
            return ""
        
        if len(content) <= self.content_max_length:
            return content
        
        # 尝试在句号处截断
        truncated = content[:self.content_max_length]
        last_period = max(truncated.rfind('。'), truncated.rfind('！'), truncated.rfind('？'))
        
        if last_period > self.content_max_length * 0.7:  # 如果句号位置在70%之后
            return truncated[:last_period + 1]
        else:
            return truncated + "..."
    
    def _generate_empty_summary(self) -> str:
        """
        生成空的总结
        
        Returns:
            str: 空总结HTML
        """
        return f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>今日热点资讯 - {datetime.now().strftime("%Y年%m月%d日")}</title>
</head>
<body>
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #007bff; text-align: center;">今日热点资讯</h1>
        <p style="text-align: center; color: #666;">{datetime.now().strftime("%Y年%m月%d日")}</p>
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;">
            <p>今日暂无热点信息收集。</p>
            <p>系统将自动在明日继续收集。</p>
        </div>
    </div>
</body>
</html>
'''
    
    def _generate_error_summary(self, error_message: str) -> str:
        """
        生成错误总结
        
        Args:
            error_message: 错误信息
            
        Returns:
            str: 错误总结HTML
        """
        return f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>今日热点资讯 - {datetime.now().strftime("%Y年%m月%d日")}</title>
</head>
<body>
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #007bff; text-align: center;">今日热点资讯</h1>
        <p style="text-align: center; color: #666;">{datetime.now().strftime("%Y年%m月%d日")}</p>
        <div style="background-color: #f8d7da; padding: 20px; border-radius: 8px; border: 1px solid #f5c6cb;">
            <h3 style="color: #721c24;">系统提示</h3>
            <p>在生成热点资讯时遇到问题：</p>
            <p style="color: #721c24; font-style: italic;">{error_message}</p>
            <p>系统将自动重试，请稍后查看。</p>
        </div>
    </div>
</body>
</html>
'''
    
    def generate_text_summary(self, news_items: List[Any]) -> str:
        """
        生成纯文本格式的总结（用于邮件正文等）
        
        Args:
            news_items: 新闻条目列表
            
        Returns:
            str: 纯文本总结
        """
        if not news_items:
            return "今日暂无热点信息收集。"
        
        try:
            # 按分类组织新闻
            categorized_news = self._categorize_news(news_items)
            
            # 生成文本
            lines = []
            lines.append(f"📰 今日热点资讯 - {datetime.now().strftime('%Y年%m月%d日')}")
            lines.append("=" * 50)
            lines.append("")
            
            # 统计信息
            total_items = sum(len(items) for items in categorized_news.values())
            lines.append(f"共收集 {total_items} 条热点信息，涵盖 {len(categorized_news)} 个领域。")
            lines.append("")
            
            # 按分类输出
            for category_name, items in categorized_news.items():
                lines.append(f"【{category_name}】")
                lines.append("-" * 30)
                
                for i, item in enumerate(items, 1):
                    lines.append(f"{i}. {item['title']}")
                    if item['content']:
                        lines.append(f"   {item['content'][:100]}...")
                    lines.append(f"   来源: {item['source']} | 热度: {item['popularity']}")
                    lines.append("")
            
            lines.append("=" * 50)
            lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("本报告由热点信息自动收集系统生成")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"生成文本总结失败: {e}")
            return f"生成总结时发生错误: {str(e)}"
    
    def get_statistics(self, news_items: List[Any]) -> Dict[str, Any]:
        """
        获取新闻统计信息
        
        Args:
            news_items: 新闻条目列表
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        if not news_items:
            return {}
        
        # 分类统计
        category_counts = defaultdict(int)
        source_counts = defaultdict(int)
        
        for item in news_items:
            category = getattr(item, 'category', '综合')
            source = getattr(item, 'source', '未知')
            
            category_counts[category] += 1
            source_counts[source] += 1
        
        # 热度统计
        popularities = [getattr(item, 'popularity', 0) for item in news_items]
        
        return {
            "total_items": len(news_items),
            "total_categories": len(category_counts),
            "total_sources": len(source_counts),
            "category_distribution": dict(category_counts),
            "source_distribution": dict(source_counts),
            "avg_popularity": sum(popularities) / len(popularities) if popularities else 0,
            "max_popularity": max(popularities) if popularities else 0,
            "min_popularity": min(popularities) if popularities else 0
        }