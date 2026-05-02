"""
RSS源爬虫模块
支持从RSS/Atom源获取新闻信息
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import feedparser
from bs4 import BeautifulSoup

from .base import BaseCrawler, NewsItem

logger = logging.getLogger(__name__)


class RSSCrawler(BaseCrawler):
    """
    RSS源爬虫
    支持从RSS/Atom源获取新闻信息
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化RSS爬虫
        
        Args:
            config: 爬虫配置，需要包含以下字段：
                - url: RSS源地址
                - category: 新闻分类
                - max_items: 最大条目数
                - interval: 访问间隔
        """
        super().__init__(config)
        self.url = config.get("url", "")
        self.category = config.get("category", "综合")
        
        if not self.url:
            logger.warning(f"RSS爬虫 {self.name} 未配置URL")
    
    def fetch(self) -> List[NewsItem]:
        """
        从RSS源获取新闻
        
        Returns:
            List[NewsItem]: 新闻列表
        """
        if not self.url:
            logger.error(f"RSS爬虫 {self.name} URL为空")
            return []
        
        try:
            logger.info(f"正在获取RSS源: {self.url}")
            
            # 使用feedparser解析RSS
            feed = feedparser.parse(self.url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"RSS解析警告: {feed.bozo_exception}")
            
            if not feed.entries:
                logger.warning(f"RSS源 {self.url} 没有条目")
                return []
            
            # 解析条目
            items = self.parse(feed.entries)
            
            logger.info(f"从RSS源 {self.name} 获取 {len(items)} 条新闻")
            return items
            
        except Exception as e:
            logger.error(f"获取RSS源失败 {self.url}: {e}", exc_info=True)
            return []
    
    def parse(self, raw_data: Any) -> List[NewsItem]:
        """
        解析RSS条目
        
        Args:
            raw_data: feedparser解析后的条目列表
            
        Returns:
            List[NewsItem]: 新闻列表
        """
        items = []
        
        for entry in raw_data:
            try:
                # 提取标题
                title = entry.get("title", "").strip()
                if not title:
                    continue
                
                # 提取链接
                url = entry.get("link", "")
                if not url:
                    continue
                
                # 提取内容摘要
                content = ""
                if "summary" in entry:
                    content = self._clean_html(entry.summary)
                elif "description" in entry:
                    content = self._clean_html(entry.description)
                elif "content" in entry:
                    # content可能是列表
                    if isinstance(entry.content, list) and entry.content:
                        content = self._clean_html(entry.content[0].get("value", ""))
                    else:
                        content = self._clean_html(str(entry.content))
                
                # 提取发布时间
                publish_time = None
                if "published_parsed" in entry:
                    try:
                        publish_time = datetime(*entry.published_parsed[:6])
                    except (TypeError, ValueError):
                        pass
                elif "updated_parsed" in entry:
                    try:
                        publish_time = datetime(*entry.updated_parsed[:6])
                    except (TypeError, ValueError):
                        pass
                
                # 提取图片
                image_url = None
                if "media_content" in entry:
                    media = entry.media_content
                    if isinstance(media, list) and media:
                        image_url = media[0].get("url")
                elif "media_thumbnail" in entry:
                    thumbnail = entry.media_thumbnail
                    if isinstance(thumbnail, list) and thumbnail:
                        image_url = thumbnail[0].get("url")
                
                # 创建新闻条目
                item = NewsItem(
                    title=title,
                    content=content[:500],  # 限制内容长度
                    url=url,
                    source=self.name,
                    category=self.category,
                    publish_time=publish_time,
                    popularity=self._calculate_popularity(entry),
                    image_url=image_url
                )
                
                items.append(item)
                
            except Exception as e:
                logger.warning(f"解析RSS条目失败: {e}")
                continue
        
        return items
    
    def _clean_html(self, html_content: str) -> str:
        """
        清理HTML内容，提取纯文本
        
        Args:
            html_content: HTML内容
            
        Returns:
            str: 清理后的纯文本
        """
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, "lxml")
            
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 获取文本
            text = soup.get_text(separator=" ", strip=True)
            
            # 清理多余空白
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.warning(f"清理HTML失败: {e}")
            # 如果解析失败，简单移除HTML标签
            import re
            clean_text = re.sub(r'<[^>]+>', '', html_content)
            return clean_text.strip()
    
    def _calculate_popularity(self, entry: Any) -> int:
        """
        计算新闻热度
        
        Args:
            entry: RSS条目
            
        Returns:
            int: 热度分数
        """
        popularity = 0
        
        # 基于发布时间计算热度（越新越热）
        if "published_parsed" in entry:
            try:
                pub_time = datetime(*entry.published_parsed[:6])
                hours_ago = (datetime.now() - pub_time).total_seconds() / 3600
                # 24小时内越新热度越高
                if hours_ago < 24:
                    popularity += int(100 - hours_ago * 4)
            except (TypeError, ValueError):
                pass
        
        # 基于内容长度
        content = entry.get("summary", "") or entry.get("description", "")
        if len(content) > 200:
            popularity += 10
        
        # 基于是否有图片
        if "media_content" in entry or "media_thumbnail" in entry:
            popularity += 5
        
        # 基于分类关键词
        title = entry.get("title", "").lower()
        hot_keywords = ["突发", "重磅", "最新", "热议", "热搜", "震惊", "速看"]
        for keyword in hot_keywords:
            if keyword in title:
                popularity += 20
                break
        
        return max(0, popularity)