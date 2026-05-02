"""
爬虫管理器模块
负责管理和协调多个爬虫实例
"""

import logging
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import BaseCrawler, NewsItem
from .rss_crawler import RSSCrawler
from .weibo_crawler import WeiboCrawler
from .zhihu_crawler import ZhihuCrawler
from .news_crawler import NewsCrawler

logger = logging.getLogger(__name__)


class CrawlerManager:
    """
    爬虫管理器
    负责加载、配置和执行多个爬虫
    """
    
    # 爬虫类型映射
    CRAWLER_TYPES = {
        "rss": RSSCrawler,
        "weibo": WeiboCrawler,
        "zhihu": ZhihuCrawler,
        "news": NewsCrawler,
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化爬虫管理器
        
        Args:
            config: 信息源配置字典
        """
        self.config = config
        self.crawlers: List[BaseCrawler] = []
        self.max_workers = config.get("max_workers", 4)
        
        # 加载爬虫
        self._load_crawlers()
        
        logger.info(f"爬虫管理器初始化完成，加载 {len(self.crawlers)} 个爬虫")
    
    def _load_crawlers(self):
        """
        根据配置加载爬虫实例
        """
        sources = self.config.get("sources", {})
        
        # 加载RSS源
        rss_config = sources.get("rss_feeds", {})
        if rss_config.get("enabled", False):
            for rss_source in rss_config.get("sources", []):
                try:
                    crawler = RSSCrawler(rss_source)
                    self.crawlers.append(crawler)
                    logger.info(f"加载RSS爬虫: {rss_source.get('name', '未命名')}")
                except Exception as e:
                    logger.error(f"加载RSS爬虫失败: {e}")
        
        # 加载社交媒体爬虫
        social_config = sources.get("social_media", {})
        if social_config.get("enabled", False):
            # 微博爬虫
            weibo_config = social_config.get("weibo", {})
            if weibo_config.get("enabled", False):
                try:
                    crawler = WeiboCrawler(weibo_config)
                    self.crawlers.append(crawler)
                    logger.info("加载微博爬虫")
                except Exception as e:
                    logger.error(f"加载微博爬虫失败: {e}")
            
            # 知乎爬虫
            zhihu_config = social_config.get("zhihu", {})
            if zhihu_config.get("enabled", False):
                try:
                    crawler = ZhihuCrawler(zhihu_config)
                    self.crawlers.append(crawler)
                    logger.info("加载知乎爬虫")
                except Exception as e:
                    logger.error(f"加载知乎爬虫失败: {e}")
        
        # 加载新闻网站爬虫
        news_config = sources.get("news_sites", {})
        if news_config.get("enabled", False):
            for site_config in news_config.get("sites", []):
                try:
                    crawler = NewsCrawler(site_config)
                    self.crawlers.append(crawler)
                    logger.info(f"加载新闻爬虫: {site_config.get('name', '未命名')}")
                except Exception as e:
                    logger.error(f"加载新闻爬虫失败: {e}")
    
    def add_crawler(self, crawler: BaseCrawler):
        """
        添加爬虫实例
        
        Args:
            crawler: 爬虫实例
        """
        self.crawlers.append(crawler)
        logger.info(f"添加爬虫: {crawler.name}")
    
    def remove_crawler(self, crawler_name: str):
        """
        移除爬虫实例
        
        Args:
            crawler_name: 爬虫名称
        """
        self.crawlers = [c for c in self.crawlers if c.name != crawler_name]
        logger.info(f"移除爬虫: {crawler_name}")
    
    def get_crawler(self, crawler_name: str) -> Optional[BaseCrawler]:
        """
        获取指定名称的爬虫
        
        Args:
            crawler_name: 爬虫名称
            
        Returns:
            Optional[BaseCrawler]: 爬虫实例，未找到返回None
        """
        for crawler in self.crawlers:
            if crawler.name == crawler_name:
                return crawler
        return None
    
    def list_crawlers(self) -> List[Dict[str, Any]]:
        """
        列出所有爬虫信息
        
        Returns:
            List[Dict[str, Any]]: 爬虫信息列表
        """
        return [
            {
                "name": crawler.name,
                "type": crawler.__class__.__name__,
                "enabled": crawler.enabled,
                "max_items": crawler.max_items,
                "interval": crawler.interval
            }
            for crawler in self.crawlers
        ]
    
    def run_all(self) -> List[NewsItem]:
        """
        执行所有爬虫并收集结果
        
        Returns:
            List[NewsItem]: 合并后的新闻列表
        """
        all_items = []
        
        logger.info(f"开始执行 {len(self.crawlers)} 个爬虫")
        
        # 使用线程池并行执行爬虫
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有爬虫任务
            future_to_crawler = {
                executor.submit(crawler.run): crawler 
                for crawler in self.crawlers 
                if crawler.enabled
            }
            
            # 收集结果
            for future in as_completed(future_to_crawler):
                crawler = future_to_crawler[future]
                try:
                    items = future.result()
                    all_items.extend(items)
                    logger.info(f"爬虫 {crawler.name} 完成，获取 {len(items)} 条新闻")
                except Exception as e:
                    logger.error(f"爬虫 {crawler.name} 执行异常: {e}", exc_info=True)
        
        # 去重
        unique_items = self._deduplicate(all_items)
        
        logger.info(f"所有爬虫执行完成，共获取 {len(unique_items)} 条唯一新闻")
        return unique_items
    
    def run_single(self, crawler_name: str) -> List[NewsItem]:
        """
        执行单个爬虫
        
        Args:
            crawler_name: 爬虫名称
            
        Returns:
            List[NewsItem]: 新闻列表
        """
        crawler = self.get_crawler(crawler_name)
        if not crawler:
            logger.error(f"未找到爬虫: {crawler_name}")
            return []
        
        return crawler.run()
    
    def _deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        """
        对新闻列表进行去重
        
        Args:
            items: 原始新闻列表
            
        Returns:
            List[NewsItem]: 去重后的新闻列表
        """
        seen_urls = set()
        seen_titles = set()
        unique_items = []
        
        for item in items:
            # 基于URL去重
            if item.url in seen_urls:
                continue
            
            # 基于标题去重（相似标题检测）
            title_key = self._normalize_title(item.title)
            if title_key in seen_titles:
                continue
            
            seen_urls.add(item.url)
            seen_titles.add(title_key)
            unique_items.append(item)
        
        logger.info(f"去重: {len(items)} -> {len(unique_items)}")
        return unique_items
    
    def _normalize_title(self, title: str) -> str:
        """
        标准化标题用于去重
        
        Args:
            title: 原始标题
            
        Returns:
            str: 标准化后的标题
        """
        import re
        
        # 移除标点符号和特殊字符
        normalized = re.sub(r'[^\w\s]', '', title)
        
        # 移除多余空格
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # 转换为小写
        normalized = normalized.lower()
        
        return normalized
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取爬虫统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            "total_crawlers": len(self.crawlers),
            "enabled_crawlers": sum(1 for c in self.crawlers if c.enabled),
            "disabled_crawlers": sum(1 for c in self.crawlers if not c.enabled),
            "crawler_details": self.list_crawlers()
        }