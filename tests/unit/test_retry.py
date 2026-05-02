"""
重试机制单元测试
"""

import pytest
from unittest.mock import Mock, patch
import time

from src.utils.retry import retry, RetryableOperation


class TestRetryDecorator:
    """
    测试重试装饰器
    """
    
    def test_retry_success_first_attempt(self):
        """
        测试第一次尝试就成功
        """
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = success_func()
        
        assert result == "success"
        assert call_count == 1
    
    def test_retry_success_after_failures(self):
        """
        测试失败后成功
        """
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def eventually_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("暂时失败")
            return "success"
        
        result = eventually_success()
        
        assert result == "success"
        assert call_count == 3
    
    def test_retry_exhausted(self):
        """
        测试重试次数耗尽
        """
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("持续失败")
        
        with pytest.raises(ValueError):
            always_fail()
        
        assert call_count == 3
    
    def test_retry_specific_exceptions(self):
        """
        测试只重试特定异常
        """
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("类型错误")
        
        with pytest.raises(TypeError):
            raise_type_error()
        
        assert call_count == 1  # 只调用一次，因为TypeError不在重试列表中
    
    def test_retry_with_args(self):
        """
        测试带参数的重试
        """
        @retry(max_attempts=3, delay=0.01)
        def add(a, b):
            return a + b
        
        result = add(1, 2)
        assert result == 3
    
    def test_retry_with_kwargs(self):
        """
        测试带关键字参数的重试
        """
        @retry(max_attempts=3, delay=0.01)
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        result = greet("World")
        assert result == "Hello, World!"


class TestRetryableOperation:
    """
    测试可重试操作类
    """
    
    def test_execute_success(self):
        """
        测试执行成功
        """
        operation = RetryableOperation(max_attempts=3, delay=0.01)
        
        def success_func():
            return "success"
        
        result = operation.execute(success_func)
        
        assert result == "success"
        assert operation.attempt == 1
    
    def test_execute_success_after_failures(self):
        """
        测试失败后成功
        """
        call_count = 0
        operation = RetryableOperation(max_attempts=3, delay=0.01)
        
        def eventually_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("暂时失败")
            return "success"
        
        result = operation.execute(eventually_success)
        
        assert result == "success"
        assert call_count == 3
    
    def test_execute_exhausted(self):
        """
        测试重试次数耗尽
        """
        call_count = 0
        operation = RetryableOperation(max_attempts=3, delay=0.01)
        
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("持续失败")
        
        with pytest.raises(ValueError):
            operation.execute(always_fail)
        
        assert call_count == 3
    
    def test_reset(self):
        """
        测试重置
        """
        operation = RetryableOperation(max_attempts=3, delay=0.01)
        
        # 模拟一些尝试
        operation.attempt = 2
        
        operation.reset()
        
        assert operation.attempt == 0
    
    def test_with_args_and_kwargs(self):
        """
        测试带参数执行
        """
        operation = RetryableOperation(max_attempts=3, delay=0.01)
        
        def add(a, b, c=0):
            return a + b + c
        
        result = operation.execute(add, 1, 2, c=3)
        
        assert result == 6