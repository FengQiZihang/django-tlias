"""
班级管理视图 - 极薄 Controller 层

职责：解析 HTTP 输入 → 调用 Service → 返回统一 Result
禁止：直接 ORM 操作、复杂业务逻辑、字段拼装
"""

import logging
from rest_framework.views import APIView
from ..services import ClazzService
from ..serializers import ClazzPageSerializer
from common.result import Result
from common.log_decorator import log_operation

logger = logging.getLogger(__name__)


class ClazzListView(APIView):
    """
    GET /clazzs - 分页查询班级
    POST /clazzs - 添加班级
    PUT /clazzs - 修改班级
    """
    
    def get(self, request):
        """分页查询班级"""
        params = {k: v for k, v in request.query_params.items()}
        logger.info(f"分页查询班级：{params}")
        pageResult = ClazzService.page(params)
        return Result.success({
            'total': pageResult['total'],
            'rows': ClazzPageSerializer(pageResult['rows'], many=True).data
        })
    
    @log_operation
    def post(self, request):
        """添加班级"""
        logger.info(f"添加班级：{request.data}")
        ClazzService.save(request.data)
        return Result.success()
    
    @log_operation
    def put(self, request):
        """修改班级"""
        logger.info(f"修改班级：{request.data}")
        ClazzService.update(request.data)
        return Result.success()


class ClazzAllView(APIView):
    """
    GET /clazzs/list - 查询所有班级
    """
    
    def get(self, request):
        """查询所有班级"""
        logger.info("查询所有班级")
        from ..serializers import ClazzSerializer
        clazzList = ClazzService.findAll()
        return Result.success(ClazzSerializer(clazzList, many=True).data)


class ClazzDetailView(APIView):
    """
    GET /clazzs/{id} - 根据ID查询班级
    DELETE /clazzs/{id} - 删除班级
    """
    
    def get(self, request, id):
        """根据ID查询班级"""
        logger.info(f"根据ID查询班级：{id}")
        from ..serializers import ClazzSerializer
        clazz = ClazzService.getInfo(id)
        return Result.success(ClazzSerializer(clazz).data)
    
    @log_operation
    def delete(self, request, id):
        """删除班级"""
        logger.info(f"删除班级：{id}")
        ClazzService.delete(id)
        return Result.success()
