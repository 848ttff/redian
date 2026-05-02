"""
配置设置模块
使用Pydantic进行配置验证和管理
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemSettings(BaseModel):
    """系统配置"""
    name: str = "热点信息收集系统"
    version: str = "1.0.0"
    log_level: str = "INFO"
    timezone: str = "Asia/Shanghai"
    debug: bool = False


class SchedulerSettings(BaseModel):
    """调度配置"""
    enabled: bool = True
    cron_expression: str = "0 19 * * *"
    retry_count: int = 3
    retry_delay: int = 300
    
    @field_validator('cron_expression')
    @classmethod
    def validate_cron(cls, v):
        parts = v.split()
        if len(parts) != 5:
            raise ValueError('cron表达式必须包含5个部分')
        return v


class EmailSettings(BaseModel):
    """邮箱配置"""
    enabled: bool = True
    smtp_server: str = ""
    smtp_port: int = 587
    use_tls: bool = True
    sender_name: str = "热点资讯日报"
    sender_email: str = ""
    sender_password: str = ""
    recipients: List[str] = []
    retry_count: int = 3
    retry_delay: int = 5


class ContentSettings(BaseModel):
    """内容配置"""
    max_items_per_source: int = 10
    total_max_items: int = 30
    summary_length: int = 500
    content_max_length: int = 150
    template: str = "daily_summary.html"
    title: str = "今日热点资讯"


class RSSSource(BaseModel):
    """RSS源配置"""
    name: str
    url: str
    category: str = "综合"
    max_items: int = 10
    interval: int = 3600
    enabled: bool = True


class SocialMediaConfig(BaseModel):
    """社交媒体配置"""
    enabled: bool = True
    max_items: int = 15
    interval: int = 1800


class NewsSiteConfig(BaseModel):
    """新闻网站配置"""
    name: str
    site: str = ""
    url: Optional[str] = None
    selectors: Optional[Dict[str, str]] = None
    category: str = "新闻"
    max_items: int = 10
    interval: int = 3600
    enabled: bool = True


class RSSFeedsConfig(BaseModel):
    """RSS源集合配置"""
    enabled: bool = True
    sources: List[RSSSource] = []


class SocialMediaSources(BaseModel):
    """社交媒体源配置"""
    enabled: bool = True
    weibo: SocialMediaConfig = SocialMediaConfig()
    zhihu: SocialMediaConfig = SocialMediaConfig()


class NewsSitesConfig(BaseModel):
    """新闻网站配置"""
    enabled: bool = True
    sites: List[NewsSiteConfig] = []


class SourcesConfig(BaseModel):
    """信息源配置"""
    rss_feeds: RSSFeedsConfig = RSSFeedsConfig()
    social_media: SocialMediaSources = SocialMediaSources()
    news_sites: NewsSitesConfig = NewsSitesConfig()


class Settings(BaseSettings):
    """主配置类"""
    system: SystemSettings = SystemSettings()
    scheduler: SchedulerSettings = SchedulerSettings()
    email: EmailSettings = EmailSettings()
    content: ContentSettings = ContentSettings()
    sources: SourcesConfig = SourcesConfig()
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="HOTNEWS_",
        env_nested_delimiter="__"
    )
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Settings":
        """
        从YAML文件加载配置
        
        Args:
            yaml_path: YAML文件路径
            
        Returns:
            Settings: 配置实例
        """
        import yaml
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f) or {}
        
        return cls(**config_data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Settings":
        """
        从字典加载配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            Settings: 配置实例
        """
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return self.model_dump()
    
    def get_email_config(self) -> Dict[str, Any]:
        """
        获取邮箱配置（用于EmailSender）
        
        Returns:
            Dict[str, Any]: 邮箱配置字典
        """
        return {
            "smtp_server": self.email.smtp_server,
            "smtp_port": self.email.smtp_port,
            "use_tls": self.email.use_tls,
            "sender_email": self.email.sender_email,
            "sender_password": self.email.sender_password,
            "sender_name": self.email.sender_name,
            "recipients": self.email.recipients,
            "retry_count": self.email.retry_count,
            "retry_delay": self.email.retry_delay
        }
    
    def get_sources_config(self) -> Dict[str, Any]:
        """
        获取信息源配置（用于CrawlerManager）
        
        Returns:
            Dict[str, Any]: 信息源配置字典
        """
        return self.sources.model_dump()
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """
        获取调度配置
        
        Returns:
            Dict[str, Any]: 调度配置字典
        """
        return self.scheduler.model_dump()
    
    def get_content_config(self) -> Dict[str, Any]:
        """
        获取内容配置
        
        Returns:
            Dict[str, Any]: 内容配置字典
        """
        return self.content.model_dump()
    
    def validate(self) -> Dict[str, Any]:
        """
        验证配置
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        errors = []
        warnings = []
        
        # 验证邮箱配置
        if self.email.enabled:
            if not self.email.smtp_server:
                errors.append("邮箱配置缺少 smtp_server")
            if not self.email.sender_email:
                errors.append("邮箱配置缺少 sender_email")
            if not self.email.sender_password:
                warnings.append("邮箱配置缺少 sender_password")
            if not self.email.recipients:
                warnings.append("邮箱配置缺少 recipients")
        
        # 验证调度配置
        if self.scheduler.enabled:
            if not self.scheduler.cron_expression:
                warnings.append("调度配置缺少 cron_expression")
        
        # 验证信息源配置
        sources = self.sources
        if not sources.rss_feeds.enabled and not sources.social_media.enabled and not sources.news_sites.enabled:
            warnings.append("未启用任何信息源")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }