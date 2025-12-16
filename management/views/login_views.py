"""
登录视图 - 极薄 Controller 层

职责：解析 HTTP 输入 → 调用 Service → 返回统一 Result
"""

import logging
from rest_framework.views import APIView
from ..services.emp_service import EmpService
from common.result import Result

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    POST /login - 员工登录
    """
    
    def post(self, request):
        """员工登录"""
        username = request.data.get('username')
        password = request.data.get('password')
        logger.info(f"员工登录: {username}")
        
        loginInfo = EmpService.login(username, password)
        if loginInfo:
            return Result.success(loginInfo)
        return Result.error("用户名或密码错误")
