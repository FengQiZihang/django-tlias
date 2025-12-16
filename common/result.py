
"""
统一响应结果封装类

对标 Java: com.example.pojo.Result
"""

from rest_framework.response import Response


class Result:
    """后端统一返回结果"""
    
    @staticmethod
    def success():
        """成功响应（无数据）"""
        return Response({
            "code": 1,
            "msg": "success",
            "data": None
        })
    
    @staticmethod
    def success(data=None):
        """成功响应（带数据）"""
        return Response({
            "code": 1,
            "msg": "success",
            "data": data
        })
    
    @staticmethod
    def error(msg: str):
        """失败响应"""
        return Response({
            "code": 0,
            "msg": msg,
            "data": None
        })
    
    @staticmethod
    def error_data(msg: str) -> dict:
        """失败响应数据（供异常处理器使用，返回字典而非 Response）"""
        return {
            "code": 0,
            "msg": msg,
            "data": None
        }
