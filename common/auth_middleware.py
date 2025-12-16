"""
认证中间件 - 对标 Java TokenFilter.java

功能：拦截所有请求，验证 JWT Token
放行：/login 登录接口
未认证：返回 401
"""

import logging
from django.http import JsonResponse
from .jwt_utils import parse_jwt

logger = logging.getLogger(__name__)


class TokenAuthMiddleware:
    """
    Token 认证中间件 - 对标 Java TokenFilter
    """
    
    # 放行的 URL 路径（包含即放行）
    WHITELIST = ['/login', '/media/', '/static/']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 1. 获取请求路径
        path = request.path
        
        # 2. 判断是否在白名单中，如果在则放行
        for pattern in self.WHITELIST:
            if pattern in path:
                logger.info(f"白名单请求，直接放行: {path}")
                return self.get_response(request)
        
        # 3. 获取请求头中的令牌（token）
        token = request.headers.get('token')
        
        # 4. 判断令牌是否存在
        if not token:
            logger.info(f"获取到 token 为空，返回 401: {path}")
            return JsonResponse({'code': 0, 'msg': '未登录'}, status=401)
        
        # 5. 解析 token
        try:
            claims = parse_jwt(token)
            emp_id = claims.get('id')
            logger.info(f"解析到当前员工 id 为：{emp_id}")
            # 将用户信息存入 request，供后续视图使用
            request.emp_id = emp_id
            request.emp_username = claims.get('username')
        except Exception as e:
            logger.info(f"解析令牌失败，返回 401: {e}")
            return JsonResponse({'code': 0, 'msg': '登录已过期'}, status=401)
        
        # 6. 放行
        logger.info(f"令牌合法，放行: {path}")
        return self.get_response(request)
