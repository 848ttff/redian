"""
配置加载器模块
负责从各种来源加载和合并配置
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    配置加载器
    支持从YAML文件、环境变量和默认值加载配置
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置加载器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_cache = {}
        
        # 加载环境变量
        self._load_env_file()
        
        logger.info(f"配置加载器初始化完成，配置目录: {self.config_dir}")
    
    def _load_env_file(self):
        """
        加载.env文件
        """
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
            logger.info("已加载.env文件")
        else:
            logger.debug(".env文件不存在，使用系统环境变量")
    
    def load_settings(self) -> Dict[str, Any]:
        """
        加载主配置文件
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return self.load_yaml("settings.yaml")
    
    def load_sources(self) -> Dict[str, Any]:
        """
        加载信息源配置文件
        
        Returns:
            Dict[str, Any]: 信息源配置字典
        """
        return self.load_yaml("sources.yaml")
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        加载YAML配置文件
        
        Args:
            filename: 配置文件名
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        filepath = self.config_dir / filename
        
        # 检查缓存
        cache_key = str(filepath)
        if cache_key in self.config_cache:
            logger.debug(f"从缓存加载配置: {filename}")
            return self.config_cache[cache_key]
        
        try:
            if not filepath.exists():
                logger.warning(f"配置文件不存在: {filepath}")
                return {}
            
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            # 处理环境变量替换
            config = self._substitute_env_vars(config)
            
            # 缓存配置
            self.config_cache[cache_key] = config
            
            logger.info(f"加载配置文件: {filepath}")
            return config
            
        except yaml.YAMLError as e:
            logger.error(f"解析YAML文件失败 {filepath}: {e}")
            return {}
        except Exception as e:
            logger.error(f"加载配置文件失败 {filepath}: {e}")
            return {}
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """
        递归替换配置中的环境变量
        
        Args:
            config: 配置值
            
        Returns:
            Any: 替换后的配置值
        """
        if isinstance(config, dict):
            return {key: self._substitute_env_vars(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            return self._replace_env_var(config)
        else:
            return config
    
    def _replace_env_var(self, value: str) -> str:
        """
        替换字符串中的环境变量
        
        Args:
            value: 包含环境变量引用的字符串
            
        Returns:
            str: 替换后的字符串
        """
        import re
        
        # 匹配 ${VAR_NAME} 格式的环境变量
        pattern = r'\$\{([^}]+)\}'
        
        def replace_match(match):
            var_name = match.group(1)
            env_value = os.environ.get(var_name)
            
            if env_value is not None:
                logger.debug(f"替换环境变量: {var_name}")
                return env_value
            else:
                logger.warning(f"环境变量未设置: {var_name}")
                return match.group(0)  # 保留原始值
        
        return re.sub(pattern, replace_match, value)
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载完整配置（合并所有配置文件）
        
        Returns:
            Dict[str, Any]: 完整配置字典
        """
        # 加载主配置
        settings = self.load_settings()
        
        # 加载信息源配置
        sources = self.load_sources()
        
        # 合并配置 - 如果sources.yaml本身包含sources键，提取其内容
        sources_content = sources.get("sources", sources)
        
        config = {
            **settings,
            "sources": sources_content
        }
        
        # 应用环境变量覆盖
        config = self._apply_env_overrides(config)
        
        logger.info("完整配置加载完成")
        return config
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用环境变量覆盖
        
        Args:
            config: 原始配置
            
        Returns:
            Dict[str, Any]: 覆盖后的配置
        """
        # 邮箱配置覆盖
        email_config = config.get("email", {})
        
        if os.environ.get("EMAIL_SENDER"):
            email_config["sender_email"] = os.environ["EMAIL_SENDER"]
        
        if os.environ.get("EMAIL_PASSWORD"):
            email_config["sender_password"] = os.environ["EMAIL_PASSWORD"]
        
        if os.environ.get("EMAIL_SMTP_SERVER"):
            email_config["smtp_server"] = os.environ["EMAIL_SMTP_SERVER"]
        
        if os.environ.get("EMAIL_SMTP_PORT"):
            email_config["smtp_port"] = int(os.environ["EMAIL_SMTP_PORT"])
        
        if os.environ.get("EMAIL_RECIPIENTS"):
            # 支持逗号分隔的多个收件人
            recipients = os.environ["EMAIL_RECIPIENTS"].split(",")
            email_config["recipients"] = [r.strip() for r in recipients]
        
        config["email"] = email_config
        
        # 日志级别覆盖
        if os.environ.get("LOG_LEVEL"):
            config.setdefault("system", {})["log_level"] = os.environ["LOG_LEVEL"]
        
        # 调试模式
        if os.environ.get("DEBUG"):
            config.setdefault("system", {})["debug"] = os.environ["DEBUG"].lower() in ("true", "1", "yes")
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持点号分隔的路径）
        
        Args:
            key: 配置键（如 "email.smtp_server"）
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        config = self.load_config()
        
        # 支持点号分隔的路径
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload(self):
        """
        重新加载配置
        """
        self.config_cache.clear()
        logger.info("配置缓存已清除，将重新加载")
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证配置
        
        Args:
            config: 配置字典
            
        Returns:
            Dict[str, Any]: 验证结果，包含 errors 和 warnings
        """
        errors = []
        warnings = []
        
        # 验证邮箱配置
        email_config = config.get("email", {})
        if email_config.get("enabled", True):
            if not email_config.get("smtp_server"):
                errors.append("邮箱配置缺少 smtp_server")
            if not email_config.get("sender_email"):
                errors.append("邮箱配置缺少 sender_email")
            if not email_config.get("sender_password"):
                warnings.append("邮箱配置缺少 sender_password")
            if not email_config.get("recipients"):
                warnings.append("邮箱配置缺少 recipients")
        
        # 验证调度配置
        scheduler_config = config.get("scheduler", {})
        if scheduler_config.get("enabled", True):
            cron_expr = scheduler_config.get("cron_expression")
            if not cron_expr:
                warnings.append("调度配置缺少 cron_expression")
        
        # 验证信息源配置
        sources_config = config.get("sources", {})
        if not sources_config:
            warnings.append("未配置任何信息源")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def create_example_config(self):
        """
        创建示例配置文件
        """
        # 创建 settings.yaml 示例
        settings_example = {
            "system": {
                "name": "热点信息收集系统",
                "version": "1.0.0",
                "log_level": "INFO",
                "timezone": "Asia/Shanghai"
            },
            "scheduler": {
                "enabled": True,
                "cron_expression": "0 19 * * *",
                "retry_count": 3,
                "retry_delay": 300
            },
            "email": {
                "enabled": True,
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "use_tls": True,
                "sender_name": "热点资讯日报",
                "sender_email": "${EMAIL_SENDER}",
                "sender_password": "${EMAIL_PASSWORD}",
                "recipients": ["recipient@example.com"]
            },
            "content": {
                "max_items_per_source": 10,
                "total_max_items": 30,
                "summary_length": 500,
                "template": "daily_summary.html"
            }
        }
        
        # 创建 sources.yaml 示例
        sources_example = {
            "sources": {
                "rss_feeds": {
                    "enabled": True,
                    "sources": [
                        {
                            "name": "新浪新闻",
                            "url": "https://feed.mix.sina.com.cn/api/roll/get",
                            "category": "新闻",
                            "max_items": 10,
                            "interval": 3600
                        }
                    ]
                },
                "social_media": {
                    "enabled": True,
                    "weibo": {
                        "enabled": True,
                        "max_items": 15,
                        "interval": 1800
                    },
                    "zhihu": {
                        "enabled": True,
                        "max_items": 10,
                        "interval": 1800
                    }
                },
                "news_sites": {
                    "enabled": True,
                    "sites": [
                        {
                            "name": "新浪新闻",
                            "site": "sina",
                            "max_items": 10,
                            "interval": 3600
                        }
                    ]
                }
            }
        }
        
        # 创建 .env 示例
        env_example = """# 邮箱配置
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=your-email-password-or-app-specific-password

# SMTP配置（可选，覆盖settings.yaml中的配置）
# EMAIL_SMTP_SERVER=smtp.example.com
# EMAIL_SMTP_PORT=587

# 收件人（可选，逗号分隔多个收件人）
# EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com

# 日志级别
LOG_LEVEL=INFO

# 调试模式
DEBUG=false
"""
        
        # 保存文件
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        settings_path = self.config_dir / "settings.yaml"
        sources_path = self.config_dir / "sources.yaml"
        env_path = Path(".env.example")
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            yaml.dump(settings_example, f, default_flow_style=False, allow_unicode=True)
        
        with open(sources_path, 'w', encoding='utf-8') as f:
            yaml.dump(sources_example, f, default_flow_style=False, allow_unicode=True)
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_example)
        
        logger.info(f"示例配置文件已创建: {settings_path}, {sources_path}, {env_path}")