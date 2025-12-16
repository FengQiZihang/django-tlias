"""
JWT 工具类 - 对标 Java JwtUtils.java

功能：生成和解析 JWT Token
密钥：aGV4aXh1ZXl1YW4= (Base64 编码的学校名称)
过期时间：12 小时 (43200000 毫秒)
"""

import jwt
from datetime import datetime, timedelta

# 密钥和过期时间配置
SIGN_KEY = "aGV4aXh1ZXl1YW4="
EXPIRE_HOURS = 12


def generate_jwt(claims: dict) -> str:
    """
    生成 JWT 令牌 - 对标 Java JwtUtils.generateJwt()
    
    Args:
        claims: 要存储在 Token 中的数据，如 {"id": 1, "username": "admin"}
    
    Returns:
        JWT Token 字符串
    """
    payload = claims.copy()
    payload['exp'] = datetime.utcnow() + timedelta(hours=EXPIRE_HOURS)
    return jwt.encode(payload, SIGN_KEY, algorithm='HS256')


def parse_jwt(token: str) -> dict:
    """
    解析 JWT 令牌 - 对标 Java JwtUtils.parseJWT()
    
    Args:
        token: JWT Token 字符串
    
    Returns:
        Token 中存储的数据
    
    Raises:
        jwt.ExpiredSignatureError: Token 已过期
        jwt.InvalidTokenError: Token 无效
    """
    return jwt.decode(token, SIGN_KEY, algorithms=['HS256'])
