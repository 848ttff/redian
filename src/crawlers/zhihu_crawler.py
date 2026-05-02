"""
知乎热榜爬虫模块
获取知乎热榜数据
"""

import json
import logging
import re
from typing import Dict, List, Any
from datetime import datetime

from .base import BaseCrawler, NewsItem

logger = logging.getLogger(__name__)


class ZhihuCrawler(BaseCrawler):
    """
    知乎热榜爬虫
    通过知乎API获取热榜数据
    """
    
    # 知乎热榜API
    HOT_LIST_URL = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化知乎爬虫
        
        Args:
            config: 爬虫配置
        """
        super().__init__(config)
        self.category = config.get("category", "问答社区")
        
        # 更新请求头
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://www.zhihu.com/hot",
            "x-requested-with": "fetch",
        })
    
    def fetch(self) -> List[NewsItem]:
        """
        获取知乎热榜列表
        
        Returns:
            List[NewsItem]: 热榜新闻列表
        """
        try:
            logger.info("正在获取知乎热榜...")
            
            # 构建请求参数
            params = {
                "desktop": "true",
                "limit": "50",
            }
            
            response = self.fetch_page(self.HOT_LIST_URL, params=params)
            if not response:
                return []
            
            data = response.json()
            
            # 解析热榜数据
            items = self.parse(data)
            
            logger.info(f"获取知乎热榜 {len(items)} 条")
            return items
            
        except Exception as e:
            logger.error(f"获取知乎热榜失败: {e}", exc_info=True)
            return []
    
    def parse(self, raw_data: Any) -> List[NewsItem]:
        """
        解析知乎热榜数据
        
        Args:
            raw_data: API返回的JSON数据
            
        Returns:
            List[NewsItem]: 新闻列表
        """
        items = []
        
        try:
            data_list = raw_data.get("data", [])
            
            for item_data in data_list:
                try:
                    target = item_data.get("target", {})
                    
                    # 提取标题
                    title = target.get("title", "").strip()
                    if not title:
                        continue
                    
                    # 提取问题ID和链接
                    question_id = target.get("id", "")
                    url = f"https://www.zhihu.com/question/{question_id}" if question_id else ""
                    
                    # 提取内容摘要
                    excerpt = target.get("excerpt", "")
                    content = excerpt[:300] if excerpt else ""
                    
                    # 提取热度值
                    detail_text = item_data.get("detail_text", "")
                    popularity = self._extract_popularity(detail_text)
                    
                    # 提取图片
                    image_url = None
                    if "thumbnail" in target:
                        image_url = target["thumbnail"]
                    
                    # 创建新闻条目
                    item = NewsItem(
                        title=title,
                        content=content,
                        url=url,
                        source="知乎热榜",
                        category="问答社区",
                        publish_time=datetime.now(),
                        popularity=popularity,
                        image_url=image_url
                    )
                    
                    items.append(item)
                    
                except Exception as e:
                    logger.warning(f"解析知乎热榜条目失败: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"解析知乎热榜数据失败: {e}", exc_info=True)
            return []
    
    def _extract_popularity(self, detail_text: str) -> int:
        """
        从详情文本中提取热度值
        
        Args:
            detail_text: 详情文本，如 "4532 万热度"
            
        Returns:
            int: 热度值
        """
        if not detail_text:
            return 0
        
        try:
            # 移除"热度"等文字
            clean_text = detail_text.replace("热度", "").strip()
            
            # 提取数字
            numbers = re.findall(r'[\d,.]+', clean_text)
            if not numbers:
                return 0
            
            # 取第一个数字
            num_str = numbers[0].replace(",", "")
            
            # 检查是否有"万"单位
            if "万" in clean_text:
                return int(float(num_str) * 10000)
            else:
                return int(float(num_str))
                
        except (ValueError, TypeError):
            return 0
    
    def validate_item(self, item: NewsItem) -> bool:
        """
        验证知乎热榜条目
        
        Args:
            item: 新闻条目
            
        Returns:
            bool: 是否有效
        """
        # 基类验证
        if not super().validate_item(item):
            return False
        
        # 过滤掉太短的标题
        if len(item.title) < 5:
            return False
        
        return True