"""
全局异常处理 - 对标 Java GlobalExceptionHandler

职责：
1. 捕获 IntegrityError，解析唯一键冲突信息
2. 捕获 BusinessException，返回自定义业务错误
3. 其他异常记录日志，返回通用错误提示
"""

import logging
import re
from django.db import IntegrityError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from common.result import Result

logger = logging.getLogger(__name__)


class BusinessException(Exception):
    """业务异常 - 对标 Java BusinessException"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器 - 对标 Java @RestControllerAdvice
    
    处理顺序：
    1. IntegrityError（唯一键冲突）
    2. BusinessException（业务异常）
    3. 其他异常（调用 DRF 默认处理器，未处理的返回通用错误）
    """
    
    # 1. 处理 IntegrityError（唯一键冲突）
    if isinstance(exc, IntegrityError):
        logger.error(f"数据已存在~: {exc}")
        message = str(exc)
        # 解析 "Duplicate entry 'xxx' for key 'yyy'" 格式
        match = re.search(r"Duplicate entry '(.+?)' for key '(.+?)'", message)
        if match:
            value = match.group(1)
            return Response(Result.error_data(f"数据已存在：{value}"))
        return Response(Result.error_data("数据已存在"))
    
    # 2. 处理 BusinessException（业务异常）
    if isinstance(exc, BusinessException):
        logger.error(f"业务出错啦~: {exc.message}")
        return Response(Result.error_data(exc.message))
    
    # 3. 调用 DRF 默认处理器
    response = exception_handler(exc, context)
    
    # 4. 未处理的异常，返回通用错误
    if response is None:
        logger.error(f"程序出错啦~", exc_info=exc)
        return Response(Result.error_data("程序出错啦，请联系管理员~"), status=500)
    
    return response
