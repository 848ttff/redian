"""
新闻网站爬虫模块
支持从多个新闻网站获取热点新闻
"""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseCrawler, NewsItem

logger = logging.getLogger(__name__)


class NewsCrawler(BaseCrawler):
    """
    新闻网站爬虫
    通过CSS选择器从新闻网站提取新闻
    """
    
    # 常见新闻网站配置
    DEFAULT_SITES = {
        "sina": {
            "name": "新浪新闻",
            "url": "https://news.sina.com.cn/",
            "selectors": {
                "container": ".news-item, .feed-card-item, .top_newslist li",
                "title": "h2 a, h3 a, .news_item_tit a, .title a",
                "content": ".news_item_desc, .feed-card-txt, .desc",
                "link": "a[href]"
            },
            "category": "新闻"
        },
        "163": {
            "name": "网易新闻",
            "url": "https://news.163.com/",
            "selectors": {
                "container": ".news_item, .newsdata_item, .cm_item",
                "title": "h3 a, .news_title a, .title a",
                "content": ".news_desc, .news_item_summary, .desc",
                "link": "a[href]"
            },
            "category": "新闻"
        },
        "qq": {
            "name": "腾讯新闻",
            "url": "https://news.qq.com/",
            "selectors": {
                "container": ".news_item, .list_item, .feed_item",
                "title": "h3 a, .news_title a, .title a",
                "content": ".news_desc, .desc, .summary",
                "link": "a[href]"
            },
            "category": "新闻"
        },
        "toutiao": {
            "name": "今日头条",
            "url": "https://www.toutiao.com/",
            "selectors": {
                "container": ".news-box .news-item, .feed-infinite-item",
                "title": ".news-item-title a, .title a",
                "content": ".news-item-desc, .desc",
                "link": "a[href]"
            },
            "category": "资讯"
        },
        "huxiu": {
            "name": "虎嗅网",
            "url": "https://www.huxiu.com/",
            "selectors": {
                "container": ".article-item, .recommend-article-item",
                "title": "h2 a, .article-title a",
                "content": ".article-desc, .summary",
                "link": "a[href]"
            },
            "category": "科技"
        },
        "36kr": {
            "name": "36氪",
            "url": "https://36kr.com/",
            "selectors": {
                "container": ".article-item, .flow-item",
                "title": ".article-item-title a, h3 a",
                "content": ".article-item-description, .summary",
                "link": "a[href]"
            },
            "category": "科技"
        }
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化新闻爬虫
        
        Args:
            config: 爬虫配置，需要包含以下字段：
                - site: 网站标识（如'sina', '163'等）或自定义配置
                - url: 新闻网站URL（可选，如果使用预设网站）
                - selectors: CSS选择器配置（可选，如果使用预设网站）
                - category: 新闻分类（可选）
        """
        super().__init__(config)
        
        self.site_id = config.get("site", "")
        
        # 获取网站配置
        if self.site_id in self.DEFAULT_SITES:
            site_config = self.DEFAULT_SITES[self.site_id]
            self.url = config.get("url", site_config["url"])
            self.selectors = config.get("selectors", site_config["selectors"])
            self.category = config.get("category", site_config["category"])
            self.name = config.get("name", site_config["name"])
        else:
            # 自定义配置
            self.url = config.get("url", "")
            self.selectors = config.get("selectors", {})
            self.category = config.get("category", "综合")
        
        if not self.url:
            logger.warning(f"新闻爬虫 {self.name} 未配置URL")
        
        if not self.selectors:
            logger.warning(f"新闻爬虫 {self.name} 未配置CSS选择器")
    
    def fetch(self) -> List[NewsItem]:
        """
        从新闻网站获取新闻列表
        
        Returns:
            List[NewsItem]: 新闻列表
        """
        if not self.url:
            logger.error(f"新闻爬虫 {self.name} URL为空")
            return []
        
        try:
            logger.info(f"正在获取新闻网站: {self.url}")
            
            response = self.fetch_page(self.url)
            if not response:
                return []
            
            # 设置正确的编码
            response.encoding = response.apparent_encoding
            
            # 解析HTML
            items = self.parse(response.text)
            
            logger.info(f"从 {self.name} 获取 {len(items)} 条新闻")
            return items
            
        except Exception as e:
            logger.error(f"获取新闻网站失败 {self.url}: {e}", exc_info=True)
            return []
    
    def parse(self, raw_data: Any) -> List[NewsItem]:
        """
        解析HTML内容
        
        Args:
            raw_data: HTML字符串
            
        Returns:
            List[NewsItem]: 新闻列表
        """
        items = []
        
        try:
            soup = BeautifulSoup(raw_data, "lxml")
            
            # 查找所有新闻容器
            container_selector = self.selectors.get("container", "")
            if not container_selector:
                logger.warning(f"未配置容器选择器")
                return []
            
            containers = soup.select(container_selector)
            
            for container in containers:
                try:
                    item = self._parse_container(container)
                    if item:
                        items.append(item)
                except Exception as e:
                    logger.warning(f"解析新闻容器失败: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"解析HTML失败: {e}", exc_info=True)
            return []
    
    def _parse_container(self, container) -> Optional[NewsItem]:
        """
        解析单个新闻容器
        
        Args:
            container: BeautifulSoup元素
            
        Returns:
            Optional[NewsItem]: 新闻条目，解析失败返回None
        """
        # 提取标题和链接
        title = ""
        url = ""
        
        title_selector = self.selectors.get("title", "")
        link_selector = self.selectors.get("link", "a[href]")
        
        if title_selector:
            title_elem = container.select_one(title_selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                # 尝试从标题元素获取链接
                link_elem = title_elem if title_elem.name == 'a' else title_elem.find_parent('a')
                if link_elem:
                    url = link_elem.get("href", "")
        
        # 如果没有找到标题，尝试从链接获取
        if not title:
            link_elem = container.select_one(link_selector)
            if link_elem:
                title = link_elem.get_text(strip=True)
                url = link_elem.get("href", "")
        
        if not title or len(title) < 5:
            return None
        
        # 处理相对URL
        if url and not url.startswith(("http://", "https://")):
            url = urljoin(self.url, url)
        
        # 提取内容摘要
        content = ""
        content_selector = self.selectors.get("content", "")
        if content_selector:
            content_elem = container.select_one(content_selector)
            if content_elem:
                content = content_elem.get_text(strip=True)[:300]
        
        # 提取图片
        image_url = None
        img_elem = container.find("img")
        if img_elem:
            image_url = img_elem.get("src") or img_elem.get("data-src")
            if image_url and not image_url.startswith(("http://", "https://")):
                image_url = urljoin(self.url, image_url)
        
        # 创建新闻条目
        item = NewsItem(
            title=title,
            content=content,
            url=url,
            source=self.name,
            category=self.category,
            publish_time=datetime.now(),
            popularity=self._calculate_popularity(title, content),
            image_url=image_url
        )
        
        return item
    
    def _calculate_popularity(self, title: str, content: str) -> int:
        """
        计算新闻热度
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            int: 热度分数
        """
        popularity = 50  # 基础分
        
        # 热点关键词加分
        hot_keywords = [
            "突发", "重磅", "最新", "热议", "热搜", "震惊", "速看",
            "首次", "宣布", "发布", "上市", "融资", "收购",
            "政策", "改革", "发布", "实施", "影响"
        ]
        
        text = (title + " " + content).lower()
        for keyword in hot_keywords:
            if keyword in text:
                popularity += 10
        
        # 标题长度适中加分
        if 10 < len(title) < 50:
            popularity += 5
        
        # 内容丰富度加分
        if len(content) > 100:
            popularity += 10
        
        return popularity
    
    def validate_item(self, item: NewsItem) -> bool:
        """
        验证新闻条目
        
        Args:
            item: 新闻条目
            
        Returns:
            bool: 是否有效
        """
        # 基类验证
        if not super().validate_item(item):
            return False
        
        # 过滤掉广告和无关内容
        ad_patterns = [
            r'广告', r'推广', r'赞助', r'商务合作',
            r'客户端', r'下载', r'APP', r'关注',
            r'登录', r'注册', r'会员', r'VIP'
        ]
        
        title_lower = item.title.lower()
        for pattern in ad_patterns:
            if re.search(pattern, title_lower, re.IGNORECASE):
                return False
        
        # 过滤掉太短的URL（可能是锚点或无效链接）
        if item.url and len(item.url) < 10:
            return False
        
        return True