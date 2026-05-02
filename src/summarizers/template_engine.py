"""
模板引擎模块
提供HTML模板加载和渲染功能
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    模板引擎
    负责加载和渲染HTML模板
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化模板引擎
        
        Args:
            config: 配置字典，包含以下字段：
                - template_dir: 模板目录路径
                - auto_reload: 是否自动重载模板
                - cache_size: 模板缓存大小
        """
        self.config = config or {}
        
        # 模板目录
        self.template_dir = self.config.get("template_dir", "config/templates")
        
        # 确保模板目录存在
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir, exist_ok=True)
            logger.info(f"创建模板目录: {self.template_dir}")
        
        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            auto_reload=self.config.get("auto_reload", True),
            cache_size=self.config.get("cache_size", 40)
        )
        
        # 添加自定义过滤器
        self._add_custom_filters()
        
        logger.info(f"模板引擎初始化完成，模板目录: {self.template_dir}")
    
    def _add_custom_filters(self):
        """
        添加自定义Jinja2过滤器
        """
        # 日期格式化过滤器
        def date_format(value, format='%Y年%m月%d日'):
            if isinstance(value, datetime):
                return value.strftime(format)
            return value
        
        # 截断文本过滤器
        def truncate_text(value, length=100, suffix='...'):
            if len(value) <= length:
                return value
            return value[:length] + suffix
        
        # 移除HTML标签过滤器
        def strip_html(value):
            import re
            clean_text = re.sub(r'<[^>]+>', '', value)
            return clean_text
        
        # 注册过滤器
        self.env.filters['date_format'] = date_format
        self.env.filters['truncate_text'] = truncate_text
        self.env.filters['strip_html'] = strip_html
    
    def load_template(self, template_name: str):
        """
        加载模板
        
        Args:
            template_name: 模板文件名
            
        Returns:
            Template: Jinja2模板对象
            
        Raises:
            TemplateNotFound: 模板不存在时抛出异常
        """
        try:
            template = self.env.get_template(template_name)
            logger.debug(f"加载模板: {template_name}")
            return template
        except TemplateNotFound:
            logger.error(f"模板不存在: {template_name}")
            raise
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染模板
        
        Args:
            template_name: 模板文件名
            context: 模板上下文数据
            
        Returns:
            str: 渲染后的HTML字符串
        """
        try:
            template = self.load_template(template_name)
            
            # 添加通用上下文变量
            context.update({
                "now": datetime.now(),
                "year": datetime.now().year,
                "month": datetime.now().month,
                "day": datetime.now().day,
                "date_str": datetime.now().strftime("%Y年%m月%d日"),
                "weekday": self._get_weekday_chinese(datetime.now().weekday())
            })
            
            # 渲染模板
            rendered = template.render(**context)
            
            logger.debug(f"模板渲染完成: {template_name}")
            return rendered
            
        except Exception as e:
            logger.error(f"模板渲染失败: {e}", exc_info=True)
            raise
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        渲染模板字符串
        
        Args:
            template_string: 模板字符串
            context: 模板上下文数据
            
        Returns:
            str: 渲染后的HTML字符串
        """
        try:
            template = self.env.from_string(template_string)
            
            # 添加通用上下文变量
            context.update({
                "now": datetime.now(),
                "year": datetime.now().year,
                "month": datetime.now().month,
                "day": datetime.now().day,
                "date_str": datetime.now().strftime("%Y年%m月%d日"),
                "weekday": self._get_weekday_chinese(datetime.now().weekday())
            })
            
            # 渲染模板
            rendered = template.render(**context)
            
            logger.debug("模板字符串渲染完成")
            return rendered
            
        except Exception as e:
            logger.error(f"模板字符串渲染失败: {e}", exc_info=True)
            raise
    
    def _get_weekday_chinese(self, weekday: int) -> str:
        """
        获取中文星期几
        
        Args:
            weekday: 星期几（0-6，0是周一）
            
        Returns:
            str: 中文星期几
        """
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return weekdays[weekday]
    
    def list_templates(self) -> list:
        """
        列出所有可用模板
        
        Returns:
            list: 模板文件名列表
        """
        try:
            templates = self.env.list_templates()
            logger.debug(f"可用模板: {templates}")
            return templates
        except Exception as e:
            logger.error(f"列出模板失败: {e}")
            return []
    
    def template_exists(self, template_name: str) -> bool:
        """
        检查模板是否存在
        
        Args:
            template_name: 模板文件名
            
        Returns:
            bool: 模板是否存在
        """
        try:
            self.env.get_template(template_name)
            return True
        except TemplateNotFound:
            return False
    
    def create_default_template(self, template_name: str = "daily_summary.html"):
        """
        创建默认模板
        
        Args:
            template_name: 模板文件名
        """
        default_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - {{ date_str }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #007bff;
            margin: 0;
            font-size: 28px;
        }
        .header .date {
            color: #666;
            font-size: 16px;
            margin-top: 10px;
        }
        .summary {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 0 4px 4px 0;
        }
        .category {
            margin-bottom: 30px;
        }
        .category h2 {
            color: #007bff;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            font-size: 20px;
        }
        .news-item {
            padding: 15px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .news-item:last-child {
            border-bottom: none;
        }
        .news-title {
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }
        .news-title a {
            color: #333;
            text-decoration: none;
        }
        .news-title a:hover {
            color: #007bff;
        }
        .news-content {
            color: #666;
            font-size: 14px;
            line-height: 1.5;
        }
        .news-meta {
            font-size: 12px;
            color: #999;
            margin-top: 8px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }
        .keywords {
            margin-top: 15px;
        }
        .keyword-tag {
            display: inline-block;
            background-color: #e9ecef;
            color: #495057;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <div class="date">{{ date_str }} {{ weekday }}</div>
        </div>
        
        <div class="summary">
            <strong>今日概览：</strong>共收集 {{ total_items }} 条热点信息，涵盖 {{ total_categories }} 个领域。
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{{ total_items }}</div>
                <div class="stat-label">热点总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ total_categories }}</div>
                <div class="stat-label">涵盖领域</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ total_sources }}</div>
                <div class="stat-label">信息源</div>
            </div>
        </div>
        
        {% for category in categories %}
        <div class="category">
            <h2>{{ category.name }}</h2>
            {% for item in category.items %}
            <div class="news-item">
                <div class="news-title">
                    <a href="{{ item.url }}">{{ item.title }}</a>
                </div>
                <div class="news-content">{{ item.content }}</div>
                <div class="news-meta">
                    来源: {{ item.source }} | 热度: {{ item.popularity }}
                </div>
            </div>
            {% endfor %}
        </div>
        {% endfor %}
        
        {% if keywords %}
        <div class="keywords">
            <h3>今日热点关键词</h3>
            {% for keyword in keywords %}
            <span class="keyword-tag">{{ keyword }}</span>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="footer">
            <p>本报告由热点信息自动收集系统生成</p>
            <p>生成时间: {{ now.strftime("%Y-%m-%d %H:%M:%S") }}</p>
        </div>
    </div>
</body>
</html>'''
        
        template_path = os.path.join(self.template_dir, template_name)
        
        # 只有当模板不存在时才创建
        if not os.path.exists(template_path):
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(default_template)
            logger.info(f"创建默认模板: {template_path}")
        else:
            logger.debug(f"模板已存在: {template_path}")