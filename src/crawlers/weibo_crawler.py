"""
微博热搜爬虫模块
获取微博热搜榜数据
"""

import json
import logging
import re
from typing import Dict, List, Any
from datetime import datetime

from .base import BaseCrawler, NewsItem

logger = logging.getLogger(__name__)


class WeiboCrawler(BaseCrawler):
    """
    微博热搜爬虫
    通过微博移动端API获取热搜数据
    """
    
    # 微博热搜API
    HOT_SEARCH_URL = "https://m.weibo.cn/api/container/getIndex"
    CONTAINER_ID = "106003type=25&t=3&disable_hot=1&filter_type=realtimehot"
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化微博爬虫
        
        Args:
            config: 爬虫配置
        """
        super().__init__(config)
        self.category = config.get("category", "社交媒体")
        
        # 更新请求头，模拟移动端
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://m.weibo.cn/",
            "X-Requested-With": "XMLHttpRequest",
        })
    
    def fetch(self) -> List[NewsItem]:
        """
        获取微博热搜列表
        
        Returns:
            List[NewsItem]: 热搜新闻列表
        """
        try:
            logger.info("正在获取微博热搜...")
            
            # 构建请求参数
            params = {
                "containerid": self.CONTAINER_ID,
                "page_type": "08",
            }
            
            response = self.fetch_page(self.HOT_SEARCH_URL, params=params)
            if not response:
                return []
            
            data = response.json()
            
            if data.get("ok") != 1:
                logger.error(f"微博API返回错误: {data.get('msg', '未知错误')}")
                return []
            
            # 解析热搜数据
            items = self.parse(data)
            
            logger.info(f"获取微博热搜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取微博热搜失败: {e}", exc_info=True)
            return []
    
    def parse(self, raw_data: Any) -> List[NewsItem]:
        """
        解析微博热搜数据
        
        Args:
            raw_data: API返回的JSON数据
            
        Returns:
            List[NewsItem]: 新闻列表
        """
        items = []
        
        try:
            data = raw_data.get("data", {})
            cards = data.get("cards", [])
            
            for card in cards:
                card_group = card.get("card_group", [])
                
                for group in card_group:
                    # 跳过广告和推荐
                    if group.get("card_type") != 9:
                        continue
                    
                    desc = group.get("desc", "")
                    title = group.get("desc_extr", "")
                    
                    if not title:
                        # 尝试从desc中提取
                        title = desc
                    
                    if not title:
                        continue
                    
                    # 提取热搜链接
                    scheme = group.get("scheme", "")
                    url = self._extract_url(scheme)
                    
                    # 提取热度值
                    popularity = self._extract_popularity(group.get("desc_extr", ""))
                    
                    # 提取图标标签（如“热”、“新”、“沸”等）
                    icon_desc = group.get("icon_desc", "")
                    is_hot = icon_desc in ["热", "沸", "爆"]
                    
                    # 创建新闻条目
                    item = NewsItem(
                        title=title,
                        content=desc if desc != title else "",
                        url=url,
                        source="微博热搜",
                        category="社交媒体",
                        publish_time=datetime.now(),
                        popularity=popularity + (50 if is_hot else 0)
                    )
                    
                    items.append(item)
            
            return items
            
        except Exception as e:
            logger.error(f"解析微博热搜数据失败: {e}", exc_info=True)
            return []
    
    def _extract_url(self, scheme: str) -> str:
        """
        从scheme中提取URL
        
        Args:
            scheme: 微博scheme字符串
            
        Returns:
            str: 提取的URL
        """
        if not scheme:
            return "https://s.weibo.com/"
        
        # 尝试提取URL
        url_match = re.search(r'https?://[^\s]+', scheme)
        if url_match:
            return url_match.group(0)
        
        # 如果没有找到URL，构建搜索URL
        return "https://s.weibo.com/"
    
    def _extract_popularity(self, desc: str) -> int:
        """
        从描述中提取热度值
        
        Args:
            desc: 热搜描述
            
        Returns:
            int: 热度值
        """
        if not desc:
            return 0
        
        # 尝试提取数字
        numbers = re.findall(r'[\d,.]+[万]?', desc)
        if not numbers:
            return 0
        
        try:
            # 取最大的数字作为热度
            max_num = 0
            for num_str in numbers:
                # 移除逗号
                clean_num = num_str.replace(",", "")
                
                # 处理"万"单位
                if "万" in clean_num:
                    num = float(clean_num.replace("万", "")) * 10000
                else:
                    num = float(clean_num)
                
                max_num = max(max_num, num)
            
            return int(max_num)
            
        except (ValueError, TypeError):
            return 0
    
    def validate_item(self, item: NewsItem) -> bool:
        """
        验证微博热搜条目
        
        Args:
            item: 新闻条目
            
        Returns:
            bool: 是否有效
        """
        # 基类验证
        if not super().validate_item(item):
            return False
        
        # 过滤掉太短的标题（可能是广告）
        if len(item.title) < 3:
            return False
        
        # 过滤掉包含广告关键词的条目
        ad_keywords = ["广告", "推广", "荐", "客户端", "下载", "APP"]
        title_lower = item.title.lower()
        for keyword in ad_keywords:
            if keyword in title_lower:
                return False
        
        return True