"""
重试机制模块
提供装饰器和函数级别的重试支持
"""

import time
import logging
from typing import Callable, Any, Optional, Tuple, Type
from functools import wraps

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍数
        exceptions: 需要重试的异常类型
        on_retry: 重试时的回调函数
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"函数 {func.__name__} 在 {max_attempts} 次尝试后仍然失败: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt} 次尝试失败: {e}，"
                        f"将在 {current_delay:.1f} 秒后重试"
                    )
                    
                    # 调用重试回调
                    if on_retry:
                        try:
                            on_retry(attempt, e)
                        except Exception as callback_error:
                            logger.warning(f"重试回调执行失败: {callback_error}")
                    
                    # 等待
                    time.sleep(current_delay)
                    
                    # 增加延迟
                    current_delay *= backoff
            
            # 不应该到达这里，但为了安全
            raise last_exception
        
        return wrapper
    
    return decorator


def retry_with_config(config: dict):
    """
    使用配置创建重试装饰器
    
    Args:
        config: 包含重试配置的字典
        
    Returns:
        装饰器函数
    """
    return retry(
        max_attempts=config.get("max_attempts", 3),
        delay=config.get("delay", 1.0),
        backoff=config.get("backoff", 2.0),
        exceptions=tuple(config.get("exceptions", [Exception]))
    )


class RetryableOperation:
    """
    可重试的操作类
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        初始化可重试操作
        
        Args:
            max_attempts: 最大重试次数
            delay: 初始延迟时间（秒）
            backoff: 延迟倍数
            exceptions: 需要重试的异常类型
        """
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.attempt = 0
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行可重试的操作
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Any: 函数返回值
            
        Raises:
            Exception: 最后一次尝试的异常
        """
        self.attempt = 0
        current_delay = self.delay
        last_exception = None
        
        while self.attempt < self.max_attempts:
            self.attempt += 1
            
            try:
                return func(*args, **kwargs)
                
            except self.exceptions as e:
                last_exception = e
                
                if self.attempt == self.max_attempts:
                    logger.error(
                        f"操作在 {self.max_attempts} 次尝试后仍然失败: {e}"
                    )
                    raise
                
                logger.warning(
                    f"操作第 {self.attempt} 次尝试失败: {e}，"
                    f"将在 {current_delay:.1f} 秒后重试"
                )
                
                time.sleep(current_delay)
                current_delay *= self.backoff
        
        # 不应该到达这里
        raise last_exception
    
    def reset(self):
        """
        重置重试状态
        """
        self.attempt = 0