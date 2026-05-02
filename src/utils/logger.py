"""
日志工具模块
提供统一的日志配置和管理
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from loguru import logger as loguru_logger


def setup_logger(
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "30 days",
    format: Optional[str] = None
) -> logging.Logger:
    """
    设置日志系统
    
    Args:
        log_level: 日志级别
        log_dir: 日志目录
        log_file: 日志文件名（可选）
        rotation: 日志轮转大小
        retention: 日志保留时间
        format: 日志格式
        
    Returns:
        logging.Logger: 配置好的日志器
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 默认日志格式
    if format is None:
        format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    # 清除默认处理器
    loguru_logger.remove()
    
    # 添加控制台处理器
    loguru_logger.add(
        sys.stderr,
        format=format,
        level=log_level,
        colorize=True
    )
    
    # 添加文件处理器
    if log_file is None:
        log_file = f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    log_file_path = log_path / log_file
    
    loguru_logger.add(
        str(log_file_path),
        format=format,
        level=log_level,
        rotation=rotation,
        retention=retention,
        encoding="utf-8"
    )
    
    # 添加错误日志文件
    error_log_file = log_path / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
    loguru_logger.add(
        str(error_log_file),
        format=format,
        level="ERROR",
        rotation=rotation,
        retention=retention,
        encoding="utf-8"
    )
    
    # 配置标准库logging以兼容
    class InterceptHandler(logging.Handler):
        """
        将标准库logging重定向到loguru
        """
        def emit(self, record):
            try:
                level = loguru_logger.level(record.levelname).name
            except ValueError:
                level = record.level
            
            frame = logging.currentframe()
            depth = 2
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            loguru_logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 移除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加拦截处理器
    root_logger.addHandler(InterceptHandler())
    
    # 配置特定模块的日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)
    
    loguru_logger.info(f"日志系统初始化完成，日志级别: {log_level}，日志目录: {log_dir}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger: 日志器实例
    """
    return logging.getLogger(name)