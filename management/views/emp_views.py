"""
员工管理视图 - 极薄 Controller 层

职责：解析 HTTP 输入 → 调用 Service → 返回统一 Result
禁止：直接 ORM 操作、复杂业务逻辑、字段拼装
"""

import logging
from rest_framework.views import APIView
from ..services import EmpService
from ..serializers import EmpSerializer, EmpDetailSerializer
from common.result import Result
from common.log_decorator import log_operation

logger = logging.getLogger(__name__)


class EmpListView(APIView):
    """
    GET /emps - 分页条件查询
    POST /emps - 新增员工
    PUT /emps - 更新员工
    DELETE /emps?ids=1,2,3 - 批量删除员工
    """
    
    def get(self, request):
        """分页查询"""
        # QueryDict 转普通 dict，每个值取单值而非列表
        params = {k: v for k, v in request.query_params.items()}
        logger.info(f"分页查询员工：{params}")
        pageResult = EmpService.page(params)
        return Result.success({
            'total': pageResult['total'],
            'rows': EmpSerializer(pageResult['rows'], many=True).data
        })
    
    @log_operation
    def post(self, request):
        """新增员工"""
        logger.info(f"新增员工：{request.data}")
        EmpService.save(request.data)
        return Result.success()
    
    @log_operation
    def put(self, request):
        """更新员工"""
        logger.info(f"更新员工：{request.data}")
        EmpService.update(request.data)
        return Result.success()
    
    @log_operation
    def delete(self, request):
        """批量删除员工"""
        ids_str = request.query_params.get('ids', '')
        ids = [int(id) for id in ids_str.split(',') if id]
        logger.info(f"删除员工：{ids}")
        EmpService.delete(ids)
        return Result.success()


class EmpDetailView(APIView):
    """
    GET /emps/{id} - 根据ID查询员工详情
    """
    
    def get(self, request, id):
        """根据ID查询员工"""
        logger.info(f"查询员工详情：{id}")
        result = EmpService.getInfo(id)
        serializer = EmpDetailSerializer(
            result['emp'], 
            context={'expr_list': result['exprList']}
        )
        return Result.success(serializer.data)


class EmpAllView(APIView):
    """
    GET /emps/list - 查询所有员工
    """
    
    def get(self, request):
        """查询所有员工"""
        logger.info("查询所有员工")
        empList = EmpService.findAll()
        return Result.success(EmpSerializer(empList, many=True).data)
