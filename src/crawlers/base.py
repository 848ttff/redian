"""
爬虫基类模块
定义所有爬虫的通用接口和基础功能
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """新闻条目数据结构"""
    title: str
    content: str
    url: str
    source: str
    category: str = "综合"
    publish_time: Optional[datetime] = None
    popularity: int = 0
    keywords: List[str] = None
    summary: str = ""
    image_url: Optional[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class BaseCrawler(ABC):
    """
    爬虫基类
    所有信息源爬虫都应继承此类并实现抽象方法
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化爬虫
        
        Args:
            config: 爬虫配置字典
        """
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.enabled = config.get("enabled", True)
        self.max_items = config.get("max_items", 10)
        self.interval = config.get("interval", 3600)  # 访问间隔（秒）
        self.timeout = config.get("timeout", 30)
        self.last_fetch_time = 0
        self.session = self._create_session()
        
        logger.info(f"初始化爬虫: {self.name}")
    
    def _create_session(self) -> requests.Session:
        """
        创建带有重试机制的HTTP会话
        
        Returns:
            requests.Session: 配置好的会话对象
        """
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置默认请求头
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
        
        return session
    
    def _respect_rate_limit(self):
        """
        遵守访问频率限制
        确保两次请求之间有足够的时间间隔
        """
        current_time = time.time()
        elapsed = current_time - self.last_fetch_time
        
        if elapsed < self.interval:
            sleep_time = self.interval - elapsed
            logger.debug(f"等待 {sleep_time:.1f} 秒以遵守频率限制")
            time.sleep(sleep_time)
        
        self.last_fetch_time = time.time()
    
    def fetch_page(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            **kwargs: 其他请求参数
            
        Returns:
            Optional[requests.Response]: 响应对象，失败时返回None
        """
        try:
            self._respect_rate_limit()
            
            response = self.session.get(
                url, 
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            
            logger.debug(f"成功获取页面: {url}")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取页面失败 {url}: {e}")
            return None
    
    @abstractmethod
    def fetch(self) -> List[NewsItem]:
        """
        获取新闻列表（抽象方法）
        
        Returns:
            List[NewsItem]: 新闻条目列表
        """
        pass
    
    @abstractmethod
    def parse(self, raw_data: Any) -> List[NewsItem]:
        """
        解析原始数据（抽象方法）
        
        Args:
            raw_data: 原始数据
            
        Returns:
            List[NewsItem]: 解析后的新闻列表
        """
        pass
    
    def validate_item(self, item: NewsItem) -> bool:
        """
        验证新闻条目是否有效
        
        Args:
            item: 新闻条目
            
        Returns:
            bool: 是否有效
        """
        if not item.title or not item.title.strip():
            return False
        
        if len(item.title) < 5:  # 标题太短
            return False
        
        if not item.url:
            return False
        
        return True
    
    def filter_items(self, items: List[NewsItem]) -> List[NewsItem]:
        """
        过滤新闻条目
        
        Args:
            items: 原始新闻列表
            
        Returns:
            List[NewsItem]: 过滤后的新闻列表
        """
        valid_items = []
        
        for item in items:
            if self.validate_item(item):
                valid_items.append(item)
            else:
                logger.debug(f"过滤无效条目: {item.title[:50]}...")
        
        # 按热度排序，取前N条
        valid_items.sort(key=lambda x: x.popularity, reverse=True)
        filtered_items = valid_items[:self.max_items]
        
        logger.info(f"过滤后保留 {len(filtered_items)}/{len(items)} 条新闻")
        return filtered_items
    
    def run(self) -> List[NewsItem]:
        """
        执行完整的爬取流程
        
        Returns:
            List[NewsItem]: 最终的新闻列表
        """
        if not self.enabled:
            logger.info(f"爬虫 {self.name} 已禁用，跳过")
            return []
        
        try:
            logger.info(f"开始执行爬虫: {self.name}")
            start_time = time.time()
            
            # 获取原始数据
            items = self.fetch()
            
            # 过滤和验证
            filtered_items = self.filter_items(items)
            
            elapsed = time.time() - start_time
            logger.info(f"爬虫 {self.name} 完成，获取 {len(filtered_items)} 条新闻，耗时 {elapsed:.2f} 秒")
            
            return filtered_items
            
        except Exception as e:
            logger.error(f"爬虫 {self.name} 执行失败: {e}", exc_info=True)
            return []
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})>"