"""
操作日志装饰器 - 对标 Java @LogOperation 注解 + OperationLogAspect 切面类

使用方法：在视图方法上添加 @log_operation 装饰器

    class DeptListView(APIView):
        @log_operation
        def post(self, request):
            ...
"""

import json
import time
import logging
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)


def log_operation(func):
    """
    操作日志装饰器 - 对标 Java AOP @Around
    
    记录：操作人ID、操作时间、类名、方法名、参数、返回值、耗时
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        # 延迟导入，避免循环依赖
        from management.models.operate_log import OperateLog
        
        # 1. 记录开始时间
        start_time = time.time()
        
        # 2. 执行原方法
        result = func(self, request, *args, **kwargs)
        
        # 3. 计算耗时
        end_time = time.time()
        cost_time = int((end_time - start_time) * 1000)  # 转换为毫秒
        
        # 4. 获取当前用户ID（从中间件注入的 request.emp_id）
        emp_id = getattr(request, 'emp_id', None)
        
        # 5. 获取请求参数
        try:
            method_params = json.dumps(request.data, ensure_ascii=False, default=str)
            if len(method_params) > 2000:
                method_params = method_params[:1997] + '...'
        except Exception:
            method_params = str(request.data)[:2000]
        
        # 6. 获取返回值
        try:
            return_value = json.dumps(result.data, ensure_ascii=False, default=str)
            if len(return_value) > 2000:
                return_value = return_value[:1997] + '...'
        except Exception:
            return_value = str(result.data)[:2000] if hasattr(result, 'data') else ''
        
        # 7. 构建日志对象并保存
        try:
            OperateLog.objects.create(
                operate_emp_id=emp_id,
                operate_time=datetime.now(),
                class_name=self.__class__.__name__,
                method_name=request.method,
                method_params=method_params,
                return_value=return_value,
                cost_time=cost_time
            )
            logger.info(f"记录操作日志：{self.__class__.__name__}.{request.method}, 耗时: {cost_time}ms")
        except Exception as e:
            logger.error(f"记录操作日志失败：{e}")
        
        return result
    
    return wrapper
