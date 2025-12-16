"""
部门管理视图 - 极薄 Controller 层

职责：解析 HTTP 输入 → 调用 Service → 返回统一 Result
禁止：直接 ORM 操作、复杂业务逻辑、字段拼装
"""

import logging
from rest_framework.views import APIView
from ..services import DeptService
from ..serializers import DeptSerializer
from common.result import Result
from common.log_decorator import log_operation

logger = logging.getLogger(__name__)


class DeptListView(APIView):
    """
    GET /depts - 查询所有部门
    POST /depts - 新增部门
    PUT /depts - 修改部门（id 在 body）
    DELETE /depts?id=x - 删除部门（id 在 query）
    """
    
    def get(self, request):
        """查询所有部门"""
        logger.info("查询所有部门")
        deptList = DeptService.findAll()
        return Result.success(DeptSerializer(deptList, many=True).data)
    
    @log_operation
    def post(self, request):
        """新增部门"""
        logger.info(f"新增部门：{request.data}")
        DeptService.add(request.data)
        return Result.success()
    
    @log_operation
    def put(self, request):
        """修改部门"""
        logger.info(f"修改部门：{request.data}")
        DeptService.update(request.data)
        return Result.success()
    
    @log_operation
    def delete(self, request):
        """删除部门"""
        id = request.query_params.get('id')
        logger.info(f"删除部门：{id}")
        DeptService.deleteById(int(id))
        return Result.success()


class DeptDetailView(APIView):
    """
    GET /depts/{id} - 查询部门详情
    """
    
    def get(self, request, id):
        """根据ID查询部门"""
        logger.info(f"根据ID查询部门：{id}")
        dept = DeptService.getById(id)
        return Result.success(DeptSerializer(dept).data)
