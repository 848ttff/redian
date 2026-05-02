"""
配置加载器单元测试
"""

import os
import pytest
import tempfile
from pathlib import Path

import yaml

from src.config.loader import ConfigLoader


class TestConfigLoader:
    """
    测试配置加载器
    """
    
    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """
        临时配置目录夹具
        """
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        return config_dir
    
    @pytest.fixture
    def loader(self, temp_config_dir):
        """
        配置加载器夹具
        """
        return ConfigLoader(str(temp_config_dir))
    
    def test_init(self, loader, temp_config_dir):
        """
        测试初始化
        """
        assert loader.config_dir == temp_config_dir
    
    def test_load_yaml_not_exists(self, loader):
        """
        测试加载不存在的YAML文件
        """
        result = loader.load_yaml("nonexistent.yaml")
        assert result == {}
    
    def test_load_yaml_valid(self, loader, temp_config_dir):
        """
        测试加载有效的YAML文件
        """
        config_data = {
            "system": {
                "name": "测试系统",
                "version": "1.0.0"
            }
        }
        
        config_file = temp_config_dir / "test.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
        
        result = loader.load_yaml("test.yaml")
        
        assert result["system"]["name"] == "测试系统"
        assert result["system"]["version"] == "1.0.0"
    
    def test_load_yaml_invalid(self, loader, temp_config_dir):
        """
        测试加载无效的YAML文件
        """
        config_file = temp_config_dir / "invalid.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: content: [")
        
        result = loader.load_yaml("invalid.yaml")
        assert result == {}
    
    def test_substitute_env_vars(self, loader, monkeypatch):
        """
        测试环境变量替换
        """
        monkeypatch.setenv("TEST_VAR", "test_value")
        
        config = {
            "key1": "${TEST_VAR}",
            "key2": "prefix_${TEST_VAR}_suffix",
            "key3": {
                "nested": "${TEST_VAR}"
            },
            "key4": ["${TEST_VAR}", "normal"]
        }
        
        result = loader._substitute_env_vars(config)
        
        assert result["key1"] == "test_value"
        assert result["key2"] == "prefix_test_value_suffix"
        assert result["key3"]["nested"] == "test_value"
        assert result["key4"][0] == "test_value"
        assert result["key4"][1] == "normal"
    
    def test_substitute_env_vars_missing(self, loader):
        """
        测试缺失环境变量的替换
        """
        config = {
            "key": "${NONEXISTENT_VAR_12345}"
        }
        
        result = loader._substitute_env_vars(config)
        
        # 保留原始值
        assert result["key"] == "${NONEXISTENT_VAR_12345}"
    
    def test_load_config(self, loader, temp_config_dir):
        """
        测试加载完整配置
        """
        # 创建settings.yaml
        settings = {
            "system": {"name": "测试"},
            "email": {"enabled": False}
        }
        with open(temp_config_dir / "settings.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(settings, f, allow_unicode=True)
        
        # 创建sources.yaml
        sources = {
            "sources": {
                "rss_feeds": {"enabled": False}
            }
        }
        with open(temp_config_dir / "sources.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(sources, f, allow_unicode=True)
        
        result = loader.load_config()
        
        assert "system" in result
        assert "sources" in result
        assert result["system"]["name"] == "测试"
    
    def test_validate_config_valid(self, loader):
        """
        测试验证有效配置
        """
        config = {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.test.com",
                "sender_email": "test@example.com",
                "sender_password": "password",
                "recipients": ["recipient@example.com"]
            },
            "scheduler": {
                "enabled": True,
                "cron_expression": "0 19 * * *"
            },
            "sources": {
                "rss_feeds": {"enabled": True}
            }
        }
        
        result = loader.validate_config(config)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_config_missing_fields(self, loader):
        """
        测试验证缺失字段的配置
        """
        config = {
            "email": {
                "enabled": True
            }
        }
        
        result = loader.validate_config(config)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_create_example_config(self, loader, temp_config_dir):
        """
        测试创建示例配置
        """
        loader.create_example_config()
        
        assert (temp_config_dir / "settings.yaml").exists()
        assert (temp_config_dir / "sources.yaml").exists()
    
    def test_reload(self, loader, temp_config_dir):
        """
        测试重新加载配置
        """
        # 创建配置文件
        config_data = {"key": "value1"}
        with open(temp_config_dir / "test.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        # 第一次加载
        result1 = loader.load_yaml("test.yaml")
        assert result1["key"] == "value1"
        
        # 修改配置文件
        config_data["key"] = "value2"
        with open(temp_config_dir / "test.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        # 重新加载前，使用缓存
        result2 = loader.load_yaml("test.yaml")
        assert result2["key"] == "value1"  # 从缓存读取
        
        # 重新加载
        loader.reload()
        
        # 重新加载后
        result3 = loader.load_yaml("test.yaml")
        assert result3["key"] == "value2"